import os
from groq import Groq
from dotenv import load_dotenv
import json
from datetime import datetime

# PDF generation imports
try:
    import markdown
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

# WeasyPrint import is done inside the function to handle system library issues gracefully

# Load your secret API key from the .env file
load_dotenv()

# Initialize Groq API client
api_key = os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API")
client = Groq(api_key=api_key) if api_key else Groq()

# Groq models to try
models_to_try = ["llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it"]

def get_ai_response(prompt, conversation_history=None, model=None):
    """Get response from Groq AI model"""
    messages = []
    
    # Add system message - MBB consultant persona
    messages.append({
        "role": "system",
        "content": "You are a senior consultant at a top-tier MBB firm (McKinsey, Bain, or BCG). You have an MBA from a top business school and specialize in strategic business analysis and AI/ML solutions. Your approach is:\n- Strategic and hypothesis-driven\n- Focused on business impact and value creation\n- Structured and methodical (MECE framework)\n- Data-driven and analytical\n- Professional and consultative\n\nYou help clients articulate their needs, understand business impact, and define requirements for AI solutions. Be concise, insightful, and direct."
    })
    
    # Add conversation history if provided
    if conversation_history:
        messages.extend(conversation_history)
    
    # Add current user prompt
    messages.append({"role": "user", "content": prompt})
    
    # Try models until one works
    for model_name in (models_to_try if model is None else [model]):
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content, model_name
        except Exception as e:
            if model is not None:
                raise e
            continue
    
    raise Exception("Could not get response from any model")

def extract_conversation_summary(conversation_history):
    """Extract key information from conversation history"""
    summary = {
        "questions_answered": [],
        "key_points": []
    }
    
    for i in range(0, len(conversation_history) - 1, 2):
        if conversation_history[i]["role"] == "assistant" and i + 1 < len(conversation_history):
            question = conversation_history[i]["content"]
            answer = conversation_history[i + 1]["content"]
            if answer.lower() not in ["skip", "done", "quit"]:
                summary["questions_answered"].append({
                    "question": question,
                    "answer": answer
                })
                summary["key_points"].append(f"Q: {question}\nA: {answer}")
    
    return summary

def generate_brd(conversation_history, project_context):
    """Generate comprehensive BRD from conversation history"""
    print("\n" + "="*70)
    print("📄 Generating Business Requirements Document (BRD)...")
    print("="*70 + "\n")
    
    # Extract conversation summary
    conversation_summary = extract_conversation_summary(conversation_history)
    
    # Parse project context
    context_lines = project_context.strip().split('\n')
    client_name = ""
    company_name = ""
    project_topic = ""
    project_date = datetime.now().strftime("%B %d, %Y")
    
    for line in context_lines:
        if "Client:" in line:
            client_name = line.split("Client:")[-1].strip()
        elif "Company:" in line:
            company_name = line.split("Company:")[-1].strip()
        elif "Project Topic:" in line:
            project_topic = line.split("Project Topic:")[-1].strip()
        elif "Date:" in line:
            project_date = line.split("Date:")[-1].strip()
    
    # Create a comprehensive prompt for BRD generation - MBB consulting style
    brd_prompt = f"""
You are a senior consultant at a top-tier MBB firm (McKinsey, Bain, or BCG) creating a comprehensive Business Requirements Document (BRD) for an AI/ML solution project. You have an MBA from a top business school and specialize in strategic consulting and AI/ML implementations.

PROJECT INFORMATION:
- Client: {client_name}
- Company: {company_name}
- Project: {project_topic}
- Document Date: {project_date}

CONVERSATION SUMMARY:
{chr(10).join(conversation_summary['key_points'])}

CONVERSATION DETAILS:
{json.dumps(conversation_history, indent=2)}

INSTRUCTIONS:
Create a comprehensive, professional BRD document following MBB consulting methodology:
1. **Strategic Focus**: Emphasize business impact, value creation, and ROI
2. **Structured Thinking**: Use MECE (Mutually Exclusive, Collectively Exhaustive) framework
3. **Data-Driven**: Include measurable success criteria and KPIs
4. **AI/ML Specific**: Include detailed technical requirements for AI/ML solutions (data infrastructure, model requirements, deployment, monitoring, etc.)
5. **Professional**: Use proper markdown formatting with headers, subheaders, bullet points, and tables
6. **Complete**: Fill all sections with actual information from the conversation; use "To be determined" only when necessary
7. **Actionable**: Ensure requirements are specific, measurable, and implementable

BRD STRUCTURE (create this exact structure):

# BUSINESS REQUIREMENTS DOCUMENT (BRD)

## Document Information
- **Document Title:** Business Requirements Document
- **Project:** [Project Name]
- **Client:** {client_name}
- **Company:** {company_name}
- **Document Version:** 1.0
- **Date:** {project_date}
- **Prepared By:** AIBA (AI Business Analyst)
- **Status:** Draft

---

## 1. EXECUTIVE SUMMARY

### 1.1 Project Overview
[Provide a comprehensive overview of the project, its purpose, and what it aims to achieve]

### 1.2 Business Objectives
[List the primary business objectives clearly]

### 1.3 Expected Benefits
[Detail the expected benefits and value proposition]

### 1.4 Key Highlights
[Summarize the most important aspects of the project]

---

## 2. PROJECT BACKGROUND

### 2.1 Client Information
- **Client Name:** {client_name}
- **Company Name:** {company_name}
- **Project Context:** {project_topic}

### 2.2 Current State
[Describe the current state of processes, systems, or operations]

### 2.3 Problem Statement
[Clearly articulate the problem or challenge being addressed]

### 2.4 Business Drivers
[Explain what is driving the need for this project]

### 2.5 Project Justification
[Explain why this project is necessary and what it will achieve]

---

## 3. STAKEHOLDERS

### 3.1 Primary Stakeholders
[List and describe primary stakeholders, their roles, and interests]

### 3.2 Secondary Stakeholders
[List secondary stakeholders and their involvement]

### 3.3 Roles and Responsibilities
[Define roles and responsibilities for each stakeholder group]

### 3.4 Stakeholder Engagement Plan
[Outline how stakeholders will be engaged throughout the project]

---

## 4. BUSINESS OBJECTIVES

### 4.1 Primary Objectives
[Numbered list of primary business objectives]

### 4.2 Secondary Objectives
[Numbered list of secondary objectives]

### 4.3 Success Criteria
[Define measurable success criteria for the project]

### 4.4 Expected Outcomes
[Describe expected outcomes and deliverables]

---

## 5. FUNCTIONAL REQUIREMENTS

### 5.1 Core Features
[Detailed list of core features and functionalities required]

### 5.2 User Stories
[User stories in format: "As a [user type], I want [goal] so that [benefit]"]

### 5.3 Business Rules
[Document business rules and logic that must be followed]

### 5.4 Process Flows
[Describe key business processes that need to be supported]

### 5.5 Use Cases
[Document key use cases and scenarios]

---

## 6. NON-FUNCTIONAL REQUIREMENTS

### 6.1 Performance Requirements
[Specify performance requirements: response times, throughput, capacity]

### 6.2 Security Requirements
[Detail security requirements: authentication, authorization, data protection]

### 6.3 Scalability Requirements
[Define scalability needs: user growth, data volume, system expansion]

### 6.4 Compliance Requirements
[List compliance requirements: regulations, standards, policies]

### 6.5 Integration Requirements
[Specify integration needs with existing systems or third-party services]

### 6.6 Usability Requirements
[Define user experience and usability requirements]

### 6.7 Reliability and Availability
[Specify uptime requirements, backup, disaster recovery]

---

## 7. AI/ML TECHNICAL REQUIREMENTS

### 7.1 Data Infrastructure
[Specify data requirements for AI/ML solution]
- **Data Sources**: [List all data sources: databases, APIs, files, streaming data]
- **Data Volume**: [Expected data volume: records per day/month, storage requirements]
- **Data Velocity**: [Real-time vs batch processing requirements]
- **Data Quality**: [Data quality standards, validation requirements]
- **Data Storage**: [Storage requirements: cloud, on-premise, hybrid]
- **Data Pipelines**: [ETL/ELT pipeline requirements, data transformation needs]

### 7.2 AI/ML Model Requirements
[Specify AI/ML model requirements]
- **Model Type**: [Supervised learning, unsupervised, reinforcement learning, NLP, computer vision, etc.]
- **Accuracy Requirements**: [Target accuracy, precision, recall, F1-score]
- **Model Explainability**: [Requirements for model interpretability and explainability]
- **Fairness & Bias**: [Bias detection and mitigation requirements]
- **Model Training**: [Training data requirements, retraining frequency]
- **Model Versioning**: [Model versioning and management requirements]

### 7.3 Deployment & Infrastructure
[Specify deployment requirements]
- **Deployment Environment**: [Cloud (AWS/Azure/GCP), on-premise, edge, hybrid]
- **Edge Deployment**: [Edge computing requirements if applicable]
- **Real-time vs Batch**: [Real-time inference vs batch processing requirements]
- **Scalability**: [Expected load, auto-scaling requirements, peak capacity]
- **Compute Resources**: [CPU, GPU, memory requirements]
- **Containerization**: [Docker, Kubernetes requirements]

### 7.4 Integration Requirements
[Specify integration needs for AI/ML solution]
- **API Integration**: [REST APIs, GraphQL, gRPC requirements]
- **System Integration**: [Integration with existing systems, ERP, CRM, etc.]
- **Data Format**: [JSON, XML, CSV, Parquet, etc.]
- **Middleware**: [Message queues, event streaming (Kafka), service mesh]
- **Legacy Systems**: [Integration with legacy systems if applicable]

### 7.5 Performance & Monitoring
[Specify performance and monitoring requirements]
- **Latency Requirements**: [Response time requirements: p50, p95, p99]
- **Throughput**: [Requests per second, transactions per second]
- **Model Monitoring**: [Model performance monitoring, drift detection]
- **Alerting**: [Alerting requirements for model degradation, system failures]
- **Observability**: [Logging, metrics, tracing requirements]
- **Dashboard**: [Monitoring dashboard requirements]

### 7.6 Security & Compliance
[Specify security and compliance requirements for AI/ML]
- **Data Privacy**: [GDPR, CCPA, HIPAA compliance requirements]
- **Model Security**: [Model protection, adversarial attack prevention]
- **Access Control**: [Authentication, authorization, role-based access]
- **Audit Trails**: [Audit logging requirements]
- **Regulatory Compliance**: [Industry-specific regulations: finance, healthcare, etc.]
- **Data Encryption**: [Encryption at rest and in transit]

### 7.7 Model Operations (MLOps)
[Specify MLOps requirements]
- **CI/CD for ML**: [Continuous integration/deployment for ML models]
- **Model Versioning**: [Model version control and management]
- **A/B Testing**: [A/B testing framework requirements]
- **Rollback Capabilities**: [Model rollback and recovery requirements]
- **Model Governance**: [Model governance, approval workflows]
- **Reproducibility**: [Reproducibility requirements for experiments and models]

### 7.8 Resource & Cost Requirements
[Specify resource and cost requirements]
- **Compute Costs**: [Expected compute costs, budget constraints]
- **Storage Costs**: [Data storage costs]
- **Team Capabilities**: [Required team skills: data scientists, ML engineers, DevOps]
- **Training Requirements**: [Training needs for client team]

---

## 8. SCOPE

### 7.1 In Scope
[Clearly define what is included in the project scope]

### 7.2 Out of Scope
[Explicitly state what is NOT included]

### 7.3 Assumptions
[List assumptions made during requirements gathering]

### 7.4 Constraints
[Document constraints: budget, time, resources, technical limitations]

### 7.5 Dependencies
[Identify dependencies on other projects, systems, or resources]

---

## 8. TIMELINE & MILESTONES

### 8.1 Project Timeline
[Provide overall project timeline]

### 8.2 Key Milestones
[Table or list of key milestones with dates]

| Milestone | Description | Target Date | Status |
|-----------|-------------|-------------|--------|
| [Milestone 1] | [Description] | [Date] | [Status] |

### 8.3 Phases
[Break down project into phases if applicable]

---

## 10. RISKS & MITIGATION

### 9.1 Identified Risks
[Table of identified risks]

| Risk ID | Risk Description | Impact | Probability | Mitigation Strategy |
|---------|------------------|--------|-------------|---------------------|
| R1 | [Risk] | [High/Medium/Low] | [High/Medium/Low] | [Strategy] |

### 9.2 Risk Mitigation Strategies
[Detailed mitigation strategies for each risk]

### 9.3 Contingency Plans
[Contingency plans for high-impact risks]

---

## 11. SUCCESS METRICS

### 11.1 Key Performance Indicators (KPIs)
[Define KPIs to measure project success]

| KPI | Description | Target | Measurement Method |
|-----|-------------|--------|---------------------|
| [KPI 1] | [Description] | [Target] | [Method] |

### 11.2 Measurement Criteria
[How success will be measured and evaluated]

### 11.3 Acceptance Criteria
[Define acceptance criteria for project deliverables]

---

## 12. APPENDICES

### 12.1 Glossary
[Define key terms and acronyms]

### 12.2 References
[List relevant documents, standards, or references]

### 12.3 Change Log
[Track changes to this document]

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {project_date} | AIBA | Initial version |

---

**END OF DOCUMENT**

Now create the complete BRD following this structure exactly. Fill in all sections with detailed, specific information from the conversation. Make it professional and comprehensive.
"""
    
    try:
        print("🔄 Processing conversation and generating BRD...")
        brd_content, model_used = get_ai_response(brd_prompt, model="llama-3.1-70b-versatile")
        print(f"✅ BRD generated successfully using model: {model_used}")
        return brd_content, model_used
    except Exception as e:
        print(f"⚠️  Error with primary model, trying alternative...")
        try:
            brd_content, model_used = get_ai_response(brd_prompt)
            print(f"✅ BRD generated successfully using model: {model_used}")
            return brd_content, model_used
        except Exception as e2:
            print(f"❌ Error generating BRD: {e2}")
            return None, None


def markdown_to_html(markdown_content):
    """Convert markdown content to HTML"""
    # Try to use extensions, but handle if they're not available
    extensions = ['extra', 'tables']
    
    # Try to add codehilite if Pygments is available
    try:
        import pygments
        extensions.append('codehilite')
    except ImportError:
        pass
    
    # nl2br is not a standard extension, so we'll skip it
    # The 'extra' extension handles most formatting needs
    
    html_body = markdown.markdown(
        markdown_content,
        extensions=extensions
    )
    
    # Professional CSS styling for PDF
    css_style = """
    <style>
        @page {
            size: A4;
            margin: 2cm;
            @top-center {
                content: "Business Requirements Document";
                font-size: 10pt;
                color: #666;
            }
            @bottom-center {
                content: "Page " counter(page) " of " counter(pages);
                font-size: 10pt;
                color: #666;
            }
        }
        body {
            font-family: 'Helvetica', 'Arial', sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
            max-width: 100%;
        }
        h1 {
            color: #1a237e;
            font-size: 24pt;
            margin-top: 20pt;
            margin-bottom: 12pt;
            border-bottom: 3px solid #1a237e;
            padding-bottom: 8pt;
        }
        h2 {
            color: #283593;
            font-size: 18pt;
            margin-top: 16pt;
            margin-bottom: 10pt;
            border-bottom: 2px solid #283593;
            padding-bottom: 6pt;
        }
        h3 {
            color: #3949ab;
            font-size: 14pt;
            margin-top: 12pt;
            margin-bottom: 8pt;
        }
        h4 {
            color: #5c6bc0;
            font-size: 12pt;
            margin-top: 10pt;
            margin-bottom: 6pt;
        }
        p {
            margin: 8pt 0;
            text-align: justify;
        }
        ul, ol {
            margin: 8pt 0;
            padding-left: 24pt;
        }
        li {
            margin: 4pt 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 12pt 0;
            page-break-inside: avoid;
        }
        th {
            background-color: #3949ab;
            color: white;
            padding: 8pt;
            text-align: left;
            font-weight: bold;
            border: 1px solid #283593;
        }
        td {
            padding: 6pt 8pt;
            border: 1px solid #ddd;
        }
        tr:nth-child(even) {
            background-color: #f5f5f5;
        }
        code {
            background-color: #f4f4f4;
            padding: 2pt 4pt;
            border-radius: 3pt;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
        }
        pre {
            background-color: #f4f4f4;
            padding: 10pt;
            border-radius: 4pt;
            overflow-x: auto;
            page-break-inside: avoid;
        }
        blockquote {
            border-left: 4px solid #3949ab;
            padding-left: 12pt;
            margin: 8pt 0;
            color: #555;
            font-style: italic;
        }
        hr {
            border: none;
            border-top: 2px solid #ddd;
            margin: 16pt 0;
        }
        strong {
            color: #1a237e;
            font-weight: bold;
        }
        .metadata {
            background-color: #f5f5f5;
            padding: 10pt;
            border-radius: 4pt;
            margin-bottom: 16pt;
            font-size: 10pt;
        }
    </style>
    """
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Business Requirements Document</title>
        {css_style}
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """
    
    return html_content

def save_brd(brd_content, project_name, project_context=""):
    """Save BRD to markdown and PDF files"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = project_name.replace(' ', '_')
    md_filename = f"BRD_{safe_name}_{timestamp}.md"
    pdf_filename = f"BRD_{safe_name}_{timestamp}.pdf"
    
    try:
        # Add document metadata at the top
        metadata = f"""---
Generated By: AIBA (AI Business Analyst)
Generation Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Project: {project_name}
Document Type: Business Requirements Document (BRD)
---

"""
        
        full_content = metadata + brd_content + f"\n\n---\n*Document generated by AIBA on {datetime.now().strftime("%B %d, %Y at %H:%M:%S")}*\n"
        
        # Save markdown file
        with open(md_filename, "w", encoding="utf-8") as f:
            f.write(full_content)
        
        print(f"\n✅ BRD saved successfully!")
        print(f"📁 Markdown File: {md_filename}")
        print(f"📄 Size: {os.path.getsize(md_filename)} bytes")
        
        # Generate PDF if supported
        if PDF_SUPPORT:
            try:
                print(f"\n🔄 Generating PDF...")
                # Import WeasyPrint here to handle system library issues gracefully
                try:
                    # Set library path for macOS Homebrew installations
                    import os
                    if 'DYLD_LIBRARY_PATH' not in os.environ:
                        homebrew_lib = '/opt/homebrew/lib'
                        if os.path.exists(homebrew_lib):
                            os.environ['DYLD_LIBRARY_PATH'] = homebrew_lib
                    
                    from weasyprint import HTML
                except (ImportError, OSError) as import_error:
                    print(f"⚠️  WeasyPrint not available: {import_error}")
                    print(f"💡 Install system dependencies for WeasyPrint or use markdown file only.")
                    return md_filename, None
                
                html_content = markdown_to_html(full_content)
                HTML(string=html_content).write_pdf(pdf_filename)
                print(f"✅ PDF generated successfully!")
                print(f"📁 PDF File: {pdf_filename}")
                print(f"📄 Size: {os.path.getsize(pdf_filename)} bytes")
                return md_filename, pdf_filename
            except Exception as pdf_error:
                print(f"⚠️  Could not generate PDF: {pdf_error}")
                print(f"💡 Markdown file saved successfully. PDF generation skipped.")
                return md_filename, None
        else:
            print(f"💡 Install 'markdown' and 'weasyprint' to generate PDF files.")
            return md_filename, None
            
    except Exception as e:
        print(f"❌ Error saving BRD: {e}")
        return None, None

def save_conversation(conversation_history, project_context, project_name):
    """Save conversation history for future reference"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Conversation_{project_name.replace(' ', '_')}_{timestamp}.json"
    
    try:
        data = {
            "project_context": project_context,
            "conversation_history": conversation_history,
            "timestamp": timestamp
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Conversation saved to: {filename}")
        return filename
    except Exception as e:
        print(f"⚠️  Could not save conversation: {e}")
        return None

def review_answers(conversation_history):
    """Display a summary of answers for review"""
    print("\n" + "="*70)
    print("📋 REVIEW YOUR ANSWERS")
    print("="*70)
    
    qa_pairs = []
    for i in range(0, len(conversation_history) - 1, 2):
        if conversation_history[i]["role"] == "assistant" and i + 1 < len(conversation_history):
            question = conversation_history[i]["content"]
            answer = conversation_history[i + 1]["content"]
            qa_pairs.append((question, answer))
    
    for idx, (question, answer) in enumerate(qa_pairs, 1):
        print(f"\n{idx}. {question}")
        print(f"   Answer: {answer[:100]}{'...' if len(answer) > 100 else ''}")
    
    print("\n" + "="*70)
    return qa_pairs

def main():
    """Main interactive BRD generation application"""
    print("\n" + "="*70)
    print("🤖 AIBA - AI Business Analyst")
    print("Interactive BRD Generator")
    print("="*70)
    print("\nWelcome! I'm AIBA, your AI Business Analyst assistant.")
    print("I'll help you gather requirements and create a comprehensive BRD.")
    print("\n💡 TIP: Answer as thoroughly as possible for the best BRD quality!")
    print("   You can always type 'skip' to move to the next question.\n")
    
    # Initialize project context
    print("📋 PROJECT SETUP")
    print("-" * 70)
    client_name = input("Client Name (e.g., PWC): ").strip() or "PWC"
    company_name = input("Company Name (e.g., Supervity): ").strip() or "Supervity"
    project_topic = input("Project Topic/Objective: ").strip() or "AI Solutions for System Automation"
    
    project_context = f"""
Client: {client_name}
Company: {company_name}
Project Topic: {project_topic}
Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    
    print(f"\n✅ Project initialized:")
    print(f"   Client: {client_name}")
    print(f"   Company: {company_name}")
    print(f"   Topic: {project_topic}\n")
    
    # Initialize conversation
    conversation_history = []
    print("="*70)
    print("💬 CONVERSATION MODE")
    print("="*70)
    print("\nI'll ask you questions about the project. You can:")
    print("  - Answer the questions")
    print("  - Type 'skip' to skip a question")
    print("  - Type 'done' when you're ready to generate the BRD")
    print("  - Type 'quit' to exit\n")
    
    # Key questions to ask
    key_questions = [
        "What is the main problem or challenge that this AI automation solution aims to solve?",
        "What are the current processes or systems that need to be automated?",
        "Who are the primary users/stakeholders who will benefit from this solution?",
        "What are the key business objectives and expected outcomes?",
        "Are there any specific AI technologies or solutions you have in mind?",
        "What are the critical success factors for this project?",
        "Are there any compliance, security, or regulatory requirements?",
        "What is the expected timeline for this project?",
        "What are the main risks or concerns you foresee?",
        "Are there any existing systems that need to integrate with the new solution?"
    ]
    
    # Start conversation
    question_index = 0
    while question_index < len(key_questions):
        question = key_questions[question_index]
        
        # Show progress
        progress = "█" * (question_index + 1) + "░" * (len(key_questions) - question_index - 1)
        print(f"\n{'='*70}")
        print(f"Progress: [{progress}] {question_index + 1}/{len(key_questions)}")
        print(f"{'='*70}")
        print(f"\n❓ Question {question_index + 1}/{len(key_questions)}:")
        print(f"   {question}\n")
        
        user_input = input("Your answer (or 'skip'/'done'/'quit'): ").strip()
        
        if user_input.lower() == 'quit':
            print("\n👋 Exiting. Goodbye!")
            return
        
        if user_input.lower() == 'done':
            print("\n✅ Moving to BRD generation...")
            break
        
        if user_input.lower() == 'skip':
            print("⏭️  Skipping this question...")
            question_index += 1
            continue
        
        if user_input:
            # Add to conversation history
            conversation_history.append({
                "role": "assistant",
                "content": question
            })
            conversation_history.append({
                "role": "user",
                "content": user_input
            })
            
            # Get AI follow-up or acknowledgment
            try:
                follow_up_prompt = f"Based on the answer: '{user_input}', provide a brief acknowledgment and ask a relevant follow-up question if needed, or say 'Thank you, let's move to the next question.'"
                ai_response, _ = get_ai_response(follow_up_prompt, conversation_history)
                print(f"\n💬 AIBA: {ai_response}\n")
            except Exception as e:
                print(f"⚠️  Could not get AI response: {e}\n")
            
            question_index += 1
    
    # Review answers before proceeding
    if conversation_history:
        review_answers(conversation_history)
        review = input("\nWould you like to review/edit your answers? (yes/no): ").strip().lower()
        if review == 'yes':
            print("\n💡 You can add more information in the next section, or type 'done' to proceed.")
    
    # Allow additional questions
    print("\n" + "="*70)
    print("💭 ADDITIONAL INFORMATION")
    print("="*70)
    print("\nYou can now provide any additional information or ask questions.")
    print("Type 'done' when finished, 'review' to see your answers, or 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == 'quit':
            print("\n👋 Exiting. Goodbye!")
            return
        
        if user_input.lower() == 'done':
            break
        
        if user_input.lower() == 'review':
            review_answers(conversation_history)
            continue
        
        if user_input:
            conversation_history.append({
                "role": "user",
                "content": user_input
            })
            
            try:
                ai_response, _ = get_ai_response(
                    "Provide a helpful response and ask a clarifying question if needed.",
                    conversation_history
                )
                print(f"\n💬 AIBA: {ai_response}\n")
            except Exception as e:
                print(f"⚠️  Could not get AI response: {e}\n")
                print("💡 Continuing anyway... You can add more information or type 'done' to proceed.\n")
    
    # Generate BRD
    print("\n" + "="*70)
    print("📊 GENERATING BRD")
    print("="*70)
    
    brd_content, model_used = generate_brd(conversation_history, project_context)
    
    if brd_content:
        print("\n" + "="*70)
        print("📄 BUSINESS REQUIREMENTS DOCUMENT")
        print("="*70)
        print(brd_content)
        print("="*70)
        
        # Save BRD and conversation
        project_name = f"{client_name}_{company_name}"
        md_filename, pdf_filename = save_brd(brd_content, project_name, project_context)
        save_conversation(conversation_history, project_context, project_name)
        
        print(f"\n✅ BRD Generation Complete!")
        if md_filename:
            print(f"📁 Markdown Document: {md_filename}")
        if pdf_filename:
            print(f"📁 PDF Document: {pdf_filename}")
        print(f"💡 You can use the conversation file to regenerate or modify the BRD later.")
    else:
        print("\n❌ Failed to generate BRD. Please try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
