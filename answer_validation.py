"""
Answer Quality Validation Module
Validates answer completeness and quality before proceeding to next question
"""
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API")
client = Groq(api_key=api_key) if api_key else Groq()

models_to_try = ["llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it"]


def validate_answer_quality(answer, question, question_type="general", conversation_context=None):
    """
    Validate answer quality and completeness
    
    Args:
        answer: The user's answer
        question: The question that was asked
        question_type: Type of question (discovery, consultative, technical)
        conversation_context: Recent conversation history for context
    
    Returns:
        dict with:
            - is_valid: bool - Whether answer is acceptable
            - quality_score: float (0-1) - Quality score
            - feedback: str - Feedback message
            - should_probe: bool - Whether to ask follow-up
            - missing_aspects: list - What's missing
    """
    if not answer or len(answer.strip()) < 10:
        return {
            "is_valid": False,
            "quality_score": 0.0,
            "feedback": "Your answer seems too brief. Could you provide more details?",
            "should_probe": True,
            "missing_aspects": ["detail", "specificity"]
        }
    
    # Check for common vague responses
    vague_indicators = [
        "i don't know", "not sure", "maybe", "possibly", 
        "it depends", "probably", "i think", "not really"
    ]
    answer_lower = answer.lower()
    is_vague = any(indicator in answer_lower for indicator in vague_indicators)
    
    # Use AI to assess answer quality
    validation_prompt = f"""
You are a quality assurance analyst evaluating the completeness and quality of an answer to a business requirements question.

Question: {question}
Question Type: {question_type}
Answer: {answer}

Recent Conversation Context:
{conversation_context[-500] if conversation_context else "None"}

Evaluate this answer on:
1. **Specificity**: Is it specific and concrete (vs vague/generic)?
2. **Completeness**: Does it fully address the question?
3. **Actionability**: Does it provide actionable information?
4. **Relevance**: Is it relevant to the project context?
5. **Detail Level**: Is there sufficient detail?

Provide your assessment in this format:
- Quality Score: [0.0-1.0]
- Is Valid: [Yes/No]
- Feedback: [Brief feedback message]
- Should Probe: [Yes/No - should we ask follow-up?]
- Missing Aspects: [List what's missing, if any]

Be strict but fair. An answer is valid if it provides useful information, even if not perfect.
"""
    
    try:
        for model_name in models_to_try:
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a quality assurance analyst. Evaluate answers objectively and provide structured feedback."
                        },
                        {
                            "role": "user",
                            "content": validation_prompt
                        }
                    ],
                    temperature=0.3,  # Lower temperature for more consistent evaluation
                    max_tokens=300
                )
                
                result_text = response.choices[0].message.content
                return parse_validation_result(result_text, is_vague)
            except Exception as e:
                continue
        
        # Fallback: Basic validation
        return basic_validation(answer, is_vague)
    except Exception as e:
        print(f"Error in answer validation: {e}")
        return basic_validation(answer, is_vague)


def parse_validation_result(result_text, is_vague):
    """Parse AI validation result into structured format"""
    try:
        # Extract quality score
        quality_score = 0.7  # Default
        if "Quality Score:" in result_text:
            try:
                score_line = [line for line in result_text.split('\n') if 'Quality Score' in line][0]
                score_str = score_line.split(':')[1].strip()
                quality_score = float(score_str)
            except:
                pass
        
        # Extract is_valid
        is_valid = True
        if "Is Valid:" in result_text:
            valid_line = [line for line in result_text.split('\n') if 'Is Valid' in line][0]
            is_valid = "yes" in valid_line.lower()
        
        # Extract feedback
        feedback = "Answer looks good. Let's continue."
        if "Feedback:" in result_text:
            feedback_lines = []
            in_feedback = False
            for line in result_text.split('\n'):
                if 'Feedback:' in line:
                    in_feedback = True
                    feedback = line.split('Feedback:')[1].strip()
                elif in_feedback and line.strip() and not line.startswith('-'):
                    feedback += " " + line.strip()
                elif in_feedback and line.startswith('-'):
                    break
        
        # Extract should_probe
        should_probe = False
        if "Should Probe:" in result_text:
            probe_line = [line for line in result_text.split('\n') if 'Should Probe' in line][0]
            should_probe = "yes" in probe_line.lower()
        
        # Extract missing aspects
        missing_aspects = []
        if "Missing Aspects:" in result_text:
            missing_line = [line for line in result_text.split('\n') if 'Missing Aspects' in line][0]
            if 'none' not in missing_line.lower():
                missing_aspects = [item.strip() for item in missing_line.split(':')[1].split(',')]
        
        # Adjust for vague answers
        if is_vague:
            quality_score = min(quality_score, 0.5)
            should_probe = True
        
        return {
            "is_valid": is_valid and quality_score >= 0.5,
            "quality_score": quality_score,
            "feedback": feedback,
            "should_probe": should_probe or quality_score < 0.7,
            "missing_aspects": missing_aspects
        }
    except Exception as e:
        print(f"Error parsing validation result: {e}")
        return basic_validation("", is_vague)


def basic_validation(answer, is_vague):
    """Basic validation fallback"""
    if not answer or len(answer.strip()) < 10:
        return {
            "is_valid": False,
            "quality_score": 0.0,
            "feedback": "Your answer seems too brief. Could you provide more details?",
            "should_probe": True,
            "missing_aspects": ["detail"]
        }
    
    if is_vague:
        return {
            "is_valid": True,
            "quality_score": 0.5,
            "feedback": "Your answer seems a bit vague. Could you be more specific?",
            "should_probe": True,
            "missing_aspects": ["specificity"]
        }
    
    # Basic length check
    if len(answer) < 50:
        return {
            "is_valid": True,
            "quality_score": 0.6,
            "feedback": "Good start. Could you add a bit more detail?",
            "should_probe": False,
            "missing_aspects": []
        }
    
    return {
        "is_valid": True,
        "quality_score": 0.8,
        "feedback": "Answer looks good!",
        "should_probe": False,
        "missing_aspects": []
    }


def generate_probing_question(answer, question, validation_result, conversation_context=None):
    """
    Generate a probing follow-up question based on validation results
    """
    if not validation_result.get("should_probe"):
        return None
    
    missing_aspects = validation_result.get("missing_aspects", [])
    
    probe_prompt = f"""
You are a senior MBB consultant. The user answered: "{answer}"
To the question: "{question}"

The answer is missing: {', '.join(missing_aspects) if missing_aspects else 'some detail'}

Ask ONE concise follow-up question that probes deeper into what's missing. Be direct and professional.
Output ONLY the question, no preamble.
"""
    
    try:
        for model_name in models_to_try:
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a senior MBB consultant. Ask direct, probing questions."
                        },
                        {
                            "role": "user",
                            "content": probe_prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=100
                )
                
                probe_question = response.choices[0].message.content.strip()
                # Clean up
                probe_question = probe_question.strip('"').strip("'")
                if not probe_question.endswith('?'):
                    probe_question += "?"
                return probe_question
            except Exception as e:
                continue
    except Exception as e:
        print(f"Error generating probe question: {e}")
    
    return None


# Example usage
if __name__ == "__main__":
    # Test validation
    test_answer = "We need a system to automate our processes."
    test_question = "What are the primary business objectives for this project?"
    
    result = validate_answer_quality(test_answer, test_question, "discovery")
    print("Validation Result:")
    print(f"  Valid: {result['is_valid']}")
    print(f"  Score: {result['quality_score']}")
    print(f"  Feedback: {result['feedback']}")
    print(f"  Should Probe: {result['should_probe']}")
    
    if result['should_probe']:
        probe = generate_probing_question(test_answer, test_question, result)
        if probe:
            print(f"\nProbing Question: {probe}")

