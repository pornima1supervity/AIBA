from flask import Flask, render_template, request, jsonify, send_file
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq

# Import BRD generation functions
from interactive_brd_generator import (
    get_ai_response, 
    generate_brd, 
    save_brd, 
    save_conversation,
    extract_conversation_summary
)

# Import customer research and adaptive questioning
from customer_research import (
    research_customer,
    generate_adaptive_question,
    determine_conversation_phase,
    should_continue_phase
)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Groq models to try
models_to_try = ["llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it"]

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/start-project', methods=['POST'])
def start_project():
    """Initialize a new project and research customer"""
    data = request.json
    client_name = data.get('client_name', '').strip()
    company_name = data.get('company_name', '').strip()
    project_topic = data.get('project_topic', '').strip()
    
    if not client_name:
        return jsonify({'error': 'Customer name is required'}), 400
    
    # Research customer
    print(f"🔍 Researching customer: {client_name} ({company_name})")
    customer_research, research_model = research_customer(client_name, company_name)
    
    project_context = f"""
Client: {client_name}
Company: {company_name if company_name else 'Not specified'}
Project Topic: {project_topic if project_topic else 'To be discovered'}
Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Customer Research: {customer_research[:500] if customer_research else 'Research in progress...'}
"""
    
    return jsonify({
        'success': True,
        'project_context': project_context,
        'client_name': client_name,
        'company_name': company_name or 'Not specified',
        'project_topic': project_topic or 'To be discovered',
        'customer_research': customer_research,
        'research_model': research_model,
        'conversation_phase': 'discovery'
    })

@app.route('/api/get-question', methods=['POST'])
def get_question():
    """Generate adaptive question based on conversation phase and history"""
    data = request.json
    conversation_history = data.get('conversation_history', [])
    customer_research = data.get('customer_research', '')
    conversation_phase = data.get('conversation_phase', 'discovery')
    total_exchanges = len([msg for msg in conversation_history if msg.get('role') == 'user'])
    
    # Determine phase if not provided
    if not conversation_phase:
        conversation_phase = determine_conversation_phase(conversation_history, total_exchanges)
    
    # Get project topic if available
    project_topic = data.get('project_topic', '')
    
    # Generate adaptive question - pass full customer research and project topic
    print(f"💭 Generating {conversation_phase} question (exchange #{total_exchanges + 1})")
    print(f"📊 Using customer research: {len(customer_research) if customer_research else 0} characters")
    print(f"🎯 Project topic: {project_topic[:100] if project_topic else 'Not provided'}")
    question, model_used = generate_adaptive_question(
        conversation_history, 
        customer_research,  # Pass full research, not truncated
        phase=conversation_phase,
        project_topic=project_topic  # Pass project topic
    )
    
    if not question:
        return jsonify({'error': 'Failed to generate question'}), 500
    
    return jsonify({
        'question': question,
        'conversation_phase': conversation_phase,
        'total_exchanges': total_exchanges + 1,
        'model_used': model_used
    })

@app.route('/api/submit-answer', methods=['POST'])
def submit_answer():
    """Submit an answer and get adaptive follow-up"""
    data = request.json
    question = data.get('question', '')
    answer = data.get('answer', '').strip()
    conversation_history = data.get('conversation_history', [])
    customer_research = data.get('customer_research', '')
    conversation_phase = data.get('conversation_phase', 'discovery')
    
    if not answer or answer.lower() in ['skip', 'done']:
        # Move to next phase or continue
        total_exchanges = len([msg for msg in conversation_history if msg.get('role') == 'user'])
        new_phase = determine_conversation_phase(conversation_history, total_exchanges + 1)
        return jsonify({
            'success': True,
            'skipped': True,
            'conversation_phase': new_phase
        })
    
    # Add to conversation history
    conversation_history.append({
        "role": "assistant",
        "content": question
    })
    conversation_history.append({
        "role": "user",
        "content": answer
    })
    
    # Get consultative follow-up or probing question
    try:
        total_exchanges = len([msg for msg in conversation_history if msg.get('role') == 'user'])
        
        # Determine if we should probe deeper or move on
        should_probe = should_continue_phase(conversation_history, conversation_phase)
        
        if should_probe and total_exchanges < 12:  # Allow probing up to 12 exchanges
            # Generate a probing follow-up question - MBB style, project-focused
            customer_research_context = customer_research[:500] if customer_research else ""
            follow_up_prompt = f"""
You are a senior MBB consultant. Based on this answer about the PROJECT: "{answer}"

Company Context (DO NOT ask about this - it's already known):
{customer_research_context}

Ask ONE strategic follow-up question about THIS PROJECT that:
- Probes deeper into PROJECT-specific business impact or root causes
- Uses consultative techniques (5 Whys, hypothesis testing)
- Focuses on THIS PROJECT's value creation and success metrics
- Is direct, professional, and project-focused
- DO NOT ask about general company information

Output ONLY the question. No acknowledgments or filler.
"""
            ai_response, _ = get_ai_response(follow_up_prompt, conversation_history)
            # Clean up response - remove any filler
            if ai_response:
                ai_response = ai_response.strip()
                # Remove common filler if present
                if any(ai_response.lower().startswith(phrase) for phrase in ["thank you", "thanks", "got it", "i see", "that's helpful"]):
                    # Extract just the question part
                    lines = ai_response.split('\n')
                    question_line = [l for l in lines if '?' in l]
                    if question_line:
                        ai_response = question_line[0].strip()
        else:
            # Move to next question silently
            ai_response = None
    except Exception as e:
        print(f"Error generating follow-up: {e}")
        ai_response = None  # Skip response on error
    
    # Determine next phase
    total_exchanges = len([msg for msg in conversation_history if msg.get('role') == 'user'])
    new_phase = determine_conversation_phase(conversation_history, total_exchanges)
    
    return jsonify({
        'success': True,
        'ai_response': ai_response,
        'conversation_history': conversation_history,
        'conversation_phase': new_phase,
        'total_exchanges': total_exchanges,
        'should_continue': total_exchanges < 15  # Max 15 exchanges before BRD generation
    })

@app.route('/api/add-additional-info', methods=['POST'])
def add_additional_info():
    """Add additional information to the conversation"""
    data = request.json
    user_input = data.get('user_input', '').strip()
    conversation_history = data.get('conversation_history', [])
    
    if not user_input:
        return jsonify({'error': 'Input is required'}), 400
    
    conversation_history.append({
        "role": "user",
        "content": user_input
    })
    
    try:
        ai_response, _ = get_ai_response(
            "If clarification is needed, ask ONE direct question. Otherwise, respond with a brief one-sentence acknowledgment without filler words.",
            conversation_history
        )
        # Clean up - only keep if it's a question or very brief
        if ai_response:
            if '?' not in ai_response and len(ai_response) > 40:
                ai_response = None  # Skip verbose acknowledgments
    except Exception as e:
        ai_response = None  # Skip response on error
    
    # Only add to history if meaningful
    if ai_response and ai_response.strip():
        conversation_history.append({
            "role": "assistant",
            "content": ai_response
        })
    
    # Only add AI response if it exists and is meaningful
    if ai_response:
        conversation_history.append({
            "role": "assistant",
            "content": ai_response
        })
    
    return jsonify({
        'success': True,
        'ai_response': ai_response if ai_response else None,
        'conversation_history': conversation_history
    })

@app.route('/api/generate-brd', methods=['POST'])
def generate_brd_endpoint():
    """Generate the BRD document"""
    data = request.json
    conversation_history = data.get('conversation_history', [])
    project_context = data.get('project_context', '')
    customer_research = data.get('customer_research', '')
    client_name = data.get('client_name', '')
    company_name = data.get('company_name', '')
    
    # Enhance project context with customer research
    if customer_research:
        project_context += f"\n\nCustomer Research Insights:\n{customer_research}"
    
    try:
        brd_content, model_used = generate_brd(conversation_history, project_context)
        
        if not brd_content:
            return jsonify({'error': 'Failed to generate BRD'}), 500
        
        # Save BRD and conversation
        project_name = f"{client_name}_{company_name}"
        
        try:
            md_filename, pdf_filename = save_brd(brd_content, project_name, project_context)
        except Exception as save_error:
            print(f"ERROR saving BRD: {save_error}")
            import traceback
            traceback.print_exc()
            # Still return the content even if save failed
            md_filename = None
            pdf_filename = None
        
        # Ensure md_filename is set - generate it if save_brd failed
        if not md_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = project_name.replace(' ', '_')
            md_filename = f"BRD_{safe_name}_{timestamp}.md"
            print(f"WARNING: save_brd returned None, attempting to save file directly: {md_filename}")
            
            # Try to save the file directly as fallback
            try:
                metadata = f"""---
Generated By: AIBA (AI Business Analyst)
Generation Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Project: {project_name}
Document Type: Business Requirements Document (BRD)
---

"""
                full_content = metadata + brd_content + f"\n\n---\n*Document generated by AIBA on {datetime.now().strftime("%B %d, %Y at %H:%M:%S")}*\n"
                
                with open(md_filename, "w", encoding="utf-8") as f:
                    f.write(full_content)
                print(f"✅ Fallback save successful: {md_filename}")
            except Exception as fallback_error:
                print(f"ERROR in fallback save: {fallback_error}")
                import traceback
                traceback.print_exc()
        
        conversation_file = save_conversation(conversation_history, project_context, project_name)
        
        response_data = {
            'success': True,
            'brd_content': brd_content,
            'md_filename': md_filename,
            'pdf_filename': pdf_filename,
            'conversation_file': conversation_file,
            'model_used': model_used
        }
        
        print(f"BRD Generation Response: md_filename={md_filename}, pdf_filename={pdf_filename}")
        
        return jsonify(response_data)
    except Exception as e:
        print(f"ERROR in generate_brd_endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/convert-to-pdf', methods=['POST'])
def convert_to_pdf():
    """Convert markdown to PDF on demand"""
    try:
        data = request.json
        md_filename = data.get('md_filename')
        brd_content = data.get('brd_content', '')
        
        if not md_filename:
            return jsonify({'error': 'md_filename is required'}), 400
        
        # Read markdown file if content not provided
        if not brd_content:
            file_path = os.path.join(os.getcwd(), md_filename)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    brd_content = f.read()
            else:
                return jsonify({'error': 'Markdown file not found'}), 404
        
        # Generate PDF filename
        pdf_filename = md_filename.replace('.md', '.pdf')
        
        # Import PDF generation functions
        from interactive_brd_generator import markdown_to_html
        
        # Set library path for macOS Homebrew installations
        if 'DYLD_LIBRARY_PATH' not in os.environ:
            homebrew_lib = '/opt/homebrew/lib'
            if os.path.exists(homebrew_lib):
                os.environ['DYLD_LIBRARY_PATH'] = homebrew_lib
        
        try:
            from weasyprint import HTML
            html_content = markdown_to_html(brd_content)
            HTML(string=html_content).write_pdf(pdf_filename)
            
            return jsonify({
                'success': True,
                'pdf_filename': pdf_filename
            })
        except (ImportError, OSError) as e:
            return jsonify({'error': f'PDF generation not available: {str(e)}'}), 500
        except Exception as e:
            return jsonify({'error': f'Error generating PDF: {str(e)}'}), 500
            
    except Exception as e:
        print(f"ERROR in convert_to_pdf: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<path:filename>')
def download_file(filename):
    """Download generated files"""
    try:
        # Decode URL-encoded filename
        from urllib.parse import unquote
        filename = unquote(filename)
        
        file_path = os.path.join(os.getcwd(), filename)
        
        # Debug logging
        print(f"Download request for: {filename}")
        print(f"Full path: {file_path}")
        print(f"File exists: {os.path.exists(file_path)}")
        
        if not os.path.exists(file_path):
            print(f"ERROR: File not found at {file_path}")
            return jsonify({'error': f'File not found: {filename}'}), 404
        
        # Get the original filename for download
        original_filename = os.path.basename(filename)
        
        # Determine MIME type based on extension
        if filename.endswith('.pdf'):
            mimetype = 'application/pdf'
        elif filename.endswith('.md'):
            mimetype = 'text/markdown'
        else:
            mimetype = 'application/octet-stream'
        
        print(f"Sending file: {original_filename} (MIME: {mimetype})")
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=original_filename,
            mimetype=mimetype
        )
    except Exception as e:
        print(f"ERROR in download_file: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

