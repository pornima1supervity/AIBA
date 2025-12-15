"""
Requirements Completeness Scoring Module
Tracks and scores completeness of requirements across different BRD sections
"""
import os
from groq import Groq
from dotenv import load_dotenv
import json

load_dotenv()

api_key = os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API")
client = Groq(api_key=api_key) if api_key else Groq()

models_to_try = ["llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it"]


# Define required sections for different project types
REQUIREMENT_SECTIONS = {
    "ai_ml": {
        "business_objectives": {
            "weight": 0.15,
            "subsections": ["primary_objectives", "success_criteria", "expected_outcomes", "roi_expectations"]
        },
        "functional_requirements": {
            "weight": 0.20,
            "subsections": ["core_features", "user_stories", "use_cases", "business_rules"]
        },
        "technical_requirements": {
            "weight": 0.25,
            "subsections": ["data_requirements", "model_requirements", "infrastructure", "integration"]
        },
        "non_functional": {
            "weight": 0.15,
            "subsections": ["performance", "security", "scalability", "compliance"]
        },
        "stakeholders": {
            "weight": 0.10,
            "subsections": ["primary_stakeholders", "user_personas", "roles_responsibilities"]
        },
        "scope": {
            "weight": 0.10,
            "subsections": ["in_scope", "out_of_scope", "assumptions", "constraints"]
        },
        "timeline": {
            "weight": 0.05,
            "subsections": ["project_timeline", "milestones", "phases"]
        }
    },
    "general": {
        "business_objectives": {"weight": 0.20},
        "functional_requirements": {"weight": 0.25},
        "non_functional": {"weight": 0.20},
        "stakeholders": {"weight": 0.15},
        "scope": {"weight": 0.10},
        "timeline": {"weight": 0.10}
    }
}


def calculate_completeness_score(conversation_history, project_type="ai_ml", project_context=""):
    """
    Calculate overall requirements completeness score
    
    Args:
        conversation_history: List of conversation messages
        project_type: Type of project (ai_ml, general, etc.)
        project_context: Project context string
    
    Returns:
        dict with:
            - overall_score: float (0-1)
            - section_scores: dict of section scores
            - missing_items: list of missing requirements
            - recommendations: list of recommendations
    """
    # Extract key information from conversation
    conversation_text = "\n".join([
        f"{msg['role']}: {msg['content']}" 
        for msg in conversation_history
    ])
    
    # Get section scores using AI analysis
    section_scores = analyze_sections(conversation_text, project_type, project_context)
    
    # Calculate weighted overall score
    sections = REQUIREMENT_SECTIONS.get(project_type, REQUIREMENT_SECTIONS["general"])
    overall_score = 0.0
    
    for section_name, section_config in sections.items():
        weight = section_config.get("weight", 0.1)
        score = section_scores.get(section_name, 0.0)
        overall_score += weight * score
    
    # Identify missing items
    missing_items = identify_missing_items(section_scores, sections)
    
    # Generate recommendations
    recommendations = generate_recommendations(section_scores, missing_items, project_type)
    
    return {
        "overall_score": round(overall_score, 2),
        "section_scores": section_scores,
        "missing_items": missing_items,
        "recommendations": recommendations,
        "ready_for_brd": overall_score >= 0.7  # 70% threshold
    }


def analyze_sections(conversation_text, project_type, project_context):
    """Analyze conversation and score each section"""
    
    sections = REQUIREMENT_SECTIONS.get(project_type, REQUIREMENT_SECTIONS["general"])
    
    analysis_prompt = f"""
You are a requirements analyst evaluating the completeness of a requirements discovery conversation.

Project Context: {project_context[:300]}

Conversation:
{conversation_text[-2000]}  # Last 2000 chars for context

Evaluate completeness for each section (0.0 = not covered, 1.0 = fully covered):

Sections to evaluate:
{', '.join(sections.keys())}

For each section, assess:
- Is information present?
- Is it detailed enough?
- Are key aspects covered?

Respond in JSON format:
{{
    "business_objectives": 0.0-1.0,
    "functional_requirements": 0.0-1.0,
    "technical_requirements": 0.0-1.0,
    "non_functional": 0.0-1.0,
    "stakeholders": 0.0-1.0,
    "scope": 0.0-1.0,
    "timeline": 0.0-1.0
}}

Only include sections that exist. Be strict but fair.
"""
    
    try:
        for model_name in models_to_try:
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a requirements analyst. Evaluate completeness objectively. Respond only with valid JSON."
                        },
                        {
                            "role": "user",
                            "content": analysis_prompt
                        }
                    ],
                    temperature=0.3,
                    max_tokens=500,
                    response_format={"type": "json_object"}
                )
                
                result_text = response.choices[0].message.content
                scores = json.loads(result_text)
                
                # Ensure all sections have scores
                default_scores = {section: 0.0 for section in sections.keys()}
                default_scores.update(scores)
                
                return default_scores
            except Exception as e:
                continue
        
        # Fallback: basic keyword-based scoring
        return basic_section_scoring(conversation_text, sections)
    except Exception as e:
        print(f"Error analyzing sections: {e}")
        return basic_section_scoring(conversation_text, sections)


def basic_section_scoring(conversation_text, sections):
    """Basic keyword-based scoring fallback"""
    text_lower = conversation_text.lower()
    
    scores = {}
    
    # Keywords for each section
    keywords = {
        "business_objectives": ["objective", "goal", "purpose", "aim", "target", "success"],
        "functional_requirements": ["feature", "function", "capability", "requirement", "need"],
        "technical_requirements": ["technical", "infrastructure", "system", "architecture", "data", "model"],
        "non_functional": ["performance", "security", "scalability", "compliance", "reliability"],
        "stakeholders": ["stakeholder", "user", "persona", "role", "team"],
        "scope": ["scope", "include", "exclude", "assumption", "constraint"],
        "timeline": ["timeline", "schedule", "milestone", "phase", "deadline"]
    }
    
    for section in sections.keys():
        section_keywords = keywords.get(section, [])
        matches = sum(1 for keyword in section_keywords if keyword in text_lower)
        # Simple scoring: more keywords = higher score (capped at 0.8)
        scores[section] = min(0.8, matches * 0.2)
    
    return scores


def identify_missing_items(section_scores, sections):
    """Identify what's missing based on low scores"""
    missing = []
    
    for section_name, score in section_scores.items():
        if score < 0.5:  # Less than 50% complete
            section_config = sections.get(section_name, {})
            subsections = section_config.get("subsections", [])
            
            if subsections:
                missing.append({
                    "section": section_name,
                    "score": score,
                    "missing_subsections": subsections
                })
            else:
                missing.append({
                    "section": section_name,
                    "score": score,
                    "message": f"Section '{section_name}' needs more detail"
                })
    
    return missing


def generate_recommendations(section_scores, missing_items, project_type):
    """Generate actionable recommendations"""
    recommendations = []
    
    # Sort sections by score (lowest first)
    sorted_sections = sorted(section_scores.items(), key=lambda x: x[1])
    
    for section_name, score in sorted_sections[:3]:  # Top 3 lowest scores
        if score < 0.7:
            rec = get_section_recommendation(section_name, score, project_type)
            if rec:
                recommendations.append(rec)
    
    return recommendations


def get_section_recommendation(section_name, score, project_type):
    """Get specific recommendation for a section"""
    
    recommendations_map = {
        "business_objectives": "Ask about primary business objectives, success criteria, and expected ROI or business impact.",
        "functional_requirements": "Explore core features, user stories, and key use cases in detail.",
        "technical_requirements": "Dive into technical requirements: data needs, infrastructure, integrations, and deployment.",
        "non_functional": "Discuss performance requirements, security needs, scalability, and compliance.",
        "stakeholders": "Identify primary stakeholders, user personas, and their roles and responsibilities.",
        "scope": "Clarify what's in scope, out of scope, assumptions, and constraints.",
        "timeline": "Discuss project timeline, key milestones, and phases."
    }
    
    base_rec = recommendations_map.get(section_name, f"Gather more information about {section_name}.")
    
    if score < 0.3:
        return f"⚠️ CRITICAL: {base_rec}"
    elif score < 0.5:
        return f"⚠️ IMPORTANT: {base_rec}"
    else:
        return f"💡 Consider: {base_rec}"


def get_completeness_dashboard(completeness_result):
    """Generate a user-friendly dashboard display"""
    overall_score = completeness_result["overall_score"]
    section_scores = completeness_result["section_scores"]
    missing_items = completeness_result["missing_items"]
    recommendations = completeness_result["recommendations"]
    
    dashboard = {
        "overall": {
            "score": overall_score,
            "percentage": int(overall_score * 100),
            "status": "ready" if overall_score >= 0.7 else "needs_more_info",
            "message": get_overall_message(overall_score)
        },
        "sections": [
            {
                "name": section_name.replace("_", " ").title(),
                "score": score,
                "percentage": int(score * 100),
                "status": get_section_status(score)
            }
            for section_name, score in section_scores.items()
        ],
        "missing": missing_items,
        "recommendations": recommendations
    }
    
    return dashboard


def get_overall_message(score):
    """Get overall status message"""
    if score >= 0.9:
        return "Excellent! Requirements are comprehensive."
    elif score >= 0.7:
        return "Good! Ready to generate BRD."
    elif score >= 0.5:
        return "Fair. Consider gathering more details."
    else:
        return "Needs more information. Continue discovery."


def get_section_status(score):
    """Get status for a section"""
    if score >= 0.7:
        return "complete"
    elif score >= 0.5:
        return "partial"
    else:
        return "incomplete"


# Example usage
if __name__ == "__main__":
    # Test with sample conversation
    sample_conversation = [
        {"role": "assistant", "content": "What are your primary business objectives?"},
        {"role": "user", "content": "We want to automate our customer service using AI chatbots."},
        {"role": "assistant", "content": "What are the key features you need?"},
        {"role": "user", "content": "Natural language understanding, multi-language support, and integration with our CRM."},
    ]
    
    result = calculate_completeness_score(sample_conversation, "ai_ml", "AI Customer Service Automation")
    
    print("Completeness Analysis:")
    print(f"Overall Score: {result['overall_score']} ({int(result['overall_score']*100)}%)")
    print(f"Ready for BRD: {result['ready_for_brd']}")
    print("\nSection Scores:")
    for section, score in result['section_scores'].items():
        print(f"  {section}: {score:.2f}")
    
    print("\nRecommendations:")
    for rec in result['recommendations']:
        print(f"  - {rec}")

