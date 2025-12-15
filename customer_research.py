"""
Customer Research Module
Performs deep research on customers to gather context
"""
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API")
client = Groq(api_key=api_key) if api_key else Groq()

models_to_try = ["llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it"]

def research_customer(customer_name, company_name=None):
    """
    Research customer to gather context and background information
    Uses AI to synthesize information about the customer
    """
    try:
        # Create research prompt
        research_prompt = f"""
You are a business research analyst. Conduct deep research and analysis on the following customer:

Customer Name: {customer_name}
Company Name: {company_name if company_name else 'Not specified'}

Please provide comprehensive research covering:
1. Company Overview: Industry, size, business model, market position
2. Business Context: What they do, their products/services, target market
3. Technology Profile: Current tech stack, digital maturity, IT infrastructure
4. Business Challenges: Common pain points in their industry, typical needs
5. Market Context: Industry trends, competitive landscape, growth trajectory
6. Key Insights: Important facts, recent news, strategic initiatives

Provide detailed, actionable insights that will help in consultative discovery conversations.
Format the research in a clear, structured way.
"""
        
        # Try different models
        for model_name in models_to_try:
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a senior research analyst at a top-tier MBB consulting firm (McKinsey, Bain, or BCG). You have an MBA from a top business school and specialize in strategic business analysis. Your research is structured, hypothesis-driven, and focuses on actionable insights. You understand business models, competitive dynamics, and strategic initiatives. Provide comprehensive, strategic research that enables consultative discovery."
                        },
                        {
                            "role": "user",
                            "content": research_prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                research_result = response.choices[0].message.content
                return research_result, model_name
            except Exception as e:
                continue
        
        return None, None
    except Exception as e:
        print(f"Error in customer research: {e}")
        return None, None

def generate_adaptive_question(conversation_history, customer_research, phase="discovery", project_topic=""):
    """
    Generate adaptive, consultative questions based on conversation history and customer research
    
    Phases:
    - discovery: Initial exploratory questions
    - consultative: Deep-dive questions based on answers
    - technical: Technical requirements (hosting, tech stack, integrations)
    """
    try:
        # Build context from conversation
        conversation_summary = ""
        if conversation_history:
            recent_exchanges = conversation_history[-6:]  # Last 3 Q&A pairs
            conversation_summary = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in recent_exchanges
            ])
        
        # Extract project context from conversation if available, or use provided project_topic
        project_context = project_topic if project_topic else ""
        if not project_context and conversation_history:
            # Look for initial project topic in early messages
            for msg in conversation_history[:4]:
                if msg.get('role') == 'user' and msg.get('content'):
                    content = msg.get('content', '').lower()
                    if any(keyword in content for keyword in ['project', 'solution', 'system', 'application', 'platform']):
                        project_context = msg.get('content', '')
                        break
        
        # Phase-specific prompts - MBB consulting style
        if phase == "discovery":
            prompt = f"""
You are a senior consultant at a top MBB firm (McKinsey, Bain, or BCG). You're conducting a strategic discovery session to gather requirements for an AI/ML PROJECT.

IMPORTANT CONTEXT - Company Information (DO NOT ask about these - they're already known):
{customer_research if customer_research else "No research available"}

Initial Project Context (if provided):
{project_context if project_context else "To be discovered"}

Recent Conversation:
{conversation_summary if conversation_summary else "Starting discovery"}

CRITICAL INSTRUCTIONS:
- DO NOT ask about company information (industry, size, business model, products, services, market position) - this is already known from research
- DO ask about the SPECIFIC PROJECT requirements

QUESTION CATEGORIES TO COVER (prioritize what hasn't been asked):
1. **Project Objectives & Business Goals**: What are the primary business objectives? What problems does this solve? What is the expected ROI/business impact? How does this align with strategic goals?
2. **Project Scope**: What is included/excluded? What are the boundaries? What dependencies exist?
3. **Current State & Pain Points**: What is the current process/system? What are the pain points? What limitations exist?
4. **Success Criteria**: How will success be measured? What are the KPIs? What are the expected outcomes?
5. **Stakeholders & Users**: Who are the primary stakeholders? Who are the end users? What are their needs?
6. **Functional Requirements**: What are the core features? What workflows need support? What are the key use cases?

Ask ONE strategic, project-focused question from these categories. Output ONLY the question. No preamble.
"""
        elif phase == "consultative":
            prompt = f"""
You are a senior MBB consultant conducting a deep-dive session on the PROJECT requirements.

Company Context (for reference only - DO NOT ask about this):
{customer_research[:500] if customer_research else ""}

Recent Conversation:
{conversation_summary}

CRITICAL INSTRUCTIONS:
- DO NOT ask about company information - focus on PROJECT specifics
- Ask ONE follow-up question about the PROJECT that deepens understanding

QUESTION CATEGORIES TO DIVE DEEPER INTO (prioritize what needs clarification):
1. **Business Impact & ROI**: What is the quantitative business impact? What is the expected ROI? What are the cost savings or revenue increases?
2. **Functional Requirements**: What are the must-have vs nice-to-have features? What are the detailed workflows? What are the business rules?
3. **User Needs & Personas**: What are the different user types? What are their specific needs? How will they interact with the solution?
4. **Constraints & Assumptions**: What are the budget constraints? Timeline constraints? Resource constraints? What assumptions are being made?
5. **Risks & Dependencies**: What are the project risks? What dependencies exist? What could go wrong?
6. **Data & Information**: What data inputs are required? What outputs are expected? What information needs to be displayed?

Use the "5 Whys" technique or hypothesis testing to probe deeper. Output ONLY the question. Be strategic and project-focused.
"""
        elif phase == "technical":
            prompt = f"""
You are a senior MBB consultant specializing in AI/ML solutions. Ask ONE technical question about THIS PROJECT's requirements.

Company Context (for reference only):
{customer_research[:300] if customer_research else ""}

Recent Conversation:
{conversation_summary}

CRITICAL INSTRUCTIONS:
- DO NOT ask about general company tech stack - ask about THIS PROJECT's technical needs
- Focus on technical requirements SPECIFIC TO THIS PROJECT

TECHNICAL QUESTION CATEGORIES (prioritize what hasn't been covered for THIS PROJECT):

1. **AI/ML Model Requirements**:
   - What type of AI/ML problem? (classification, regression, NLP, computer vision, etc.)
   - What accuracy/precision/recall requirements?
   - Is model explainability required?
   - Are there fairness/bias mitigation requirements?

2. **Data Requirements**:
   - What data sources will be used? (training and inference)
   - What is the expected data volume? (records per day/month)
   - What is the data velocity? (real-time vs batch)
   - What is the current data quality state?
   - What data preprocessing/transformation is needed?

3. **Infrastructure & Deployment**:
   - Where will the solution be deployed? (Cloud: AWS/Azure/GCP, on-premise, hybrid, edge)
   - What are the scalability requirements? (users, transactions, data volume)
   - What are the availability/uptime requirements?
   - What are the disaster recovery requirements?

4. **Integration Requirements**:
   - What existing systems need integration?
   - What APIs/interfaces are required?
   - What data formats are needed? (JSON, XML, CSV, Parquet)
   - Are there legacy systems to integrate?

5. **Performance Requirements**:
   - What is acceptable response time? (p50, p95, p99)
   - What is required throughput? (requests per second)
   - What are concurrent user requirements?
   - What are peak load requirements?

6. **Security & Compliance**:
   - What security requirements? (authentication, authorization, encryption)
   - What compliance regulations? (GDPR, CCPA, HIPAA, SOC2)
   - What audit logging is required?
   - Industry-specific security standards?

7. **Model Operations (MLOps)**:
   - Model versioning strategy?
   - CI/CD pipeline requirements?
   - Rollback strategy?
   - Model monitoring requirements? (accuracy, drift, latency)
   - A/B testing strategy?

8. **Resources & Constraints**:
   - Compute requirements? (CPU, GPU, memory)
   - Team capabilities? (data scientists, ML engineers, DevOps)
   - Budget constraints?
   - Timeline constraints?

Ask ONE direct, project-specific technical question from these categories. No preamble.
"""
        else:
            prompt = f"""
Based on the conversation, ask a relevant follow-up question.
{conversation_summary}
"""
        
        # Get AI response
        for model_name in models_to_try:
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a senior consultant at a top-tier MBB firm (McKinsey, Bain, or BCG). You have an MBA from a top business school and specialize in strategic consulting and AI/ML solutions.\n\nCRITICAL RULES:\n- You have access to company research - DO NOT ask questions about company information (industry, size, business model, products, services, market position)\n- Focus ONLY on PROJECT-specific questions: project objectives, requirements, use cases, technical needs, constraints, success criteria\n- Your questioning style is:\n  * Strategic and hypothesis-driven\n  * Focused on PROJECT requirements and business impact\n  * Structured and methodical (MECE framework)\n  * Direct and professional\n  * Project-specific and actionable\n\nYou ask ONE direct, project-focused question at a time. No acknowledgments, no filler words, no explanations. Just the strategic question about the PROJECT."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=100
                )
                question = response.choices[0].message.content.strip()
                # Clean up: remove quotes, acknowledgments, and ensure it's just the question
                question = question.strip('"').strip("'")
                # Remove common filler phrases
                filler_phrases = [
                    "Thank you for that.",
                    "Thanks for sharing.",
                    "I understand.",
                    "Got it.",
                    "That's helpful.",
                    "Let me ask",
                    "I'd like to know",
                    "Can you tell me",
                    "I'm curious about"
                ]
                for phrase in filler_phrases:
                    if question.lower().startswith(phrase.lower()):
                        question = question[len(phrase):].strip()
                        # Remove leading punctuation
                        question = question.lstrip(',:;. ')
                
                # Ensure it ends with ?
                if not question.endswith('?'):
                    question += "?"
                return question, model_name
            except Exception as e:
                continue
        
        return None, None
    except Exception as e:
        print(f"Error generating adaptive question: {e}")
        return None, None

def determine_conversation_phase(conversation_history, total_exchanges):
    """
    Determine which phase of the conversation we're in
    MBB approach: Discovery → Deep Dive → Technical Requirements
    """
    if total_exchanges < 4:
        return "discovery"  # Strategic business needs and objectives
    elif total_exchanges < 9:
        return "consultative"  # Deep-dive into business impact and requirements
    else:
        return "technical"  # AI/ML technical requirements and infrastructure

def should_continue_phase(conversation_history, phase):
    """
    Determine if we should continue current phase or move to next
    """
    if not conversation_history:
        return True
    
    # Check if we have enough depth in current phase
    recent_answers = [
        msg['content'] 
        for msg in conversation_history[-4:] 
        if msg['role'] == 'user'
    ]
    
    # If answers are getting shorter or less detailed, might be time to move on
    if phase == "discovery" and len(recent_answers) >= 3:
        return False  # Move to consultative
    elif phase == "consultative" and len(recent_answers) >= 5:
        return False  # Move to technical
    elif phase == "technical" and len(recent_answers) >= 4:
        return False  # Ready for BRD generation
    
    return True

