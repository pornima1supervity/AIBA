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

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Groq models to try
models_to_try = ["llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it"]

# Key questions for the conversation
KEY_QUESTIONS = [
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

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/start-project', methods=['POST'])
def start_project():
    """Initialize a new project"""
    data = request.json
    client_name = data.get('client_name', '').strip()
    company_name = data.get('company_name', '').strip()
    project_topic = data.get('project_topic', '').strip()
    
    if not all([client_name, company_name, project_topic]):
        return jsonify({'error': 'All fields are required'}), 400
    
    project_context = f"""
Client: {client_name}
Company: {company_name}
Project Topic: {project_topic}
Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    
    return jsonify({
        'success': True,
        'project_context': project_context,
        'client_name': client_name,
        'company_name': company_name,
        'project_topic': project_topic,
        'total_questions': len(KEY_QUESTIONS)
    })

@app.route('/api/get-question', methods=['POST'])
def get_question():
    """Get the next question"""
    data = request.json
    question_index = data.get('question_index', 0)
    
    if question_index >= len(KEY_QUESTIONS):
        return jsonify({'error': 'No more questions'}), 400
    
    return jsonify({
        'question': KEY_QUESTIONS[question_index],
        'question_index': question_index,
        'total_questions': len(KEY_QUESTIONS)
    })

@app.route('/api/submit-answer', methods=['POST'])
def submit_answer():
    """Submit an answer and get AI response"""
    data = request.json
    question = data.get('question', '')
    answer = data.get('answer', '').strip()
    conversation_history = data.get('conversation_history', [])
    question_index = data.get('question_index', 0)
    
    if not answer or answer.lower() in ['skip', 'done']:
        return jsonify({
            'success': True,
            'skipped': True,
            'next_question_index': question_index + 1
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
    
    # Get AI follow-up or acknowledgment
    try:
        follow_up_prompt = f"Based on the answer: '{answer}', provide a brief acknowledgment and ask a relevant follow-up question if needed, or say 'Thank you, let's move to the next question.'"
        ai_response, _ = get_ai_response(follow_up_prompt, conversation_history)
    except Exception as e:
        ai_response = f"Thank you for your answer. Let's continue with the next question."
    
    return jsonify({
        'success': True,
        'ai_response': ai_response,
        'conversation_history': conversation_history,
        'next_question_index': question_index + 1
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
            "Provide a helpful response and ask a clarifying question if needed.",
            conversation_history
        )
    except Exception as e:
        ai_response = "Thank you for the additional information."
    
    conversation_history.append({
        "role": "assistant",
        "content": ai_response
    })
    
    return jsonify({
        'success': True,
        'ai_response': ai_response,
        'conversation_history': conversation_history
    })

@app.route('/api/generate-brd', methods=['POST'])
def generate_brd_endpoint():
    """Generate the BRD document"""
    data = request.json
    conversation_history = data.get('conversation_history', [])
    project_context = data.get('project_context', '')
    client_name = data.get('client_name', '')
    company_name = data.get('company_name', '')
    
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

