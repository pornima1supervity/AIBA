# AIBA - Interactive BRD Generator

An intelligent Business Requirements Document (BRD) generator that uses AI to conduct interactive conversations with stakeholders and automatically generate comprehensive BRDs.

## Features

- 🤖 **AI-Powered Conversations**: Uses Groq AI models to have natural conversations
- 📋 **Structured Question Flow**: Asks 10 key questions covering all aspects of a project
- 💬 **Interactive Follow-ups**: AIBA can ask clarifying questions based on your answers
- 📄 **Comprehensive BRD Generation**: Creates detailed BRDs with all standard sections
- 💾 **Auto-Save**: Saves both BRD and conversation history
- 📊 **Progress Tracking**: Visual progress indicator during the conversation
- 🔍 **Answer Review**: Review your answers before generating the BRD

## Requirements

- Python 3.7+
- Groq API key (get one at https://console.groq.com/)
- Required packages: `groq`, `python-dotenv`
- Optional (for PDF generation): `markdown`, `weasyprint`

## Installation

1. Install required packages:
```bash
pip install groq python-dotenv
```

2. (Optional) Install PDF generation libraries:
```bash
pip install markdown weasyprint
```

**Note:** PDF generation requires `weasyprint` which may need additional system dependencies:
- **macOS**: `brew install cairo pango gdk-pixbuf libffi`
- **Ubuntu/Debian**: `sudo apt-get install python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0`
- **Windows**: Usually works with pip install, but may need GTK+ runtime

2. Set up your `.env` file:
```env
GROQ_API_KEY=your_groq_api_key_here
```

## Usage

Run the application:
```bash
python interactive_brd_generator.py
```

### Example Session

1. **Project Setup**:
   - Client Name: `PWC`
   - Company Name: `Supervity`
   - Project Topic: `AI Solutions for System Automation`

2. **Answer Questions**: The AI will ask 10 structured questions about:
   - Problem statement
   - Current processes
   - Stakeholders
   - Business objectives
   - AI technologies
   - Success factors
   - Compliance/security
   - Timeline
   - Risks
   - Integration requirements

3. **Additional Information**: Add any extra details or ask questions

4. **Review**: Review your answers before generating the BRD

5. **BRD Generation**: The system generates a comprehensive BRD automatically

### Commands

During the conversation, you can use:
- `skip` - Skip the current question
- `done` - Finish answering questions and proceed to BRD generation
- `review` - Review all your answers (in additional information section)
- `quit` - Exit the application

## Output Files

The application generates multiple files:

1. **BRD Markdown Document**: `BRD_ClientName_CompanyName_YYYYMMDD_HHMMSS.md`
   - Comprehensive Business Requirements Document in Markdown format
   - Always generated

2. **BRD PDF Document**: `BRD_ClientName_CompanyName_YYYYMMDD_HHMMSS.pdf`
   - Professional PDF version of the BRD
   - Generated if `markdown` and `weasyprint` libraries are installed
   - Includes proper formatting, tables, and styling

3. **Conversation History**: `Conversation_ClientName_CompanyName_YYYYMMDD_HHMMSS.json`
   - Complete conversation history for future reference or regeneration

## BRD Structure

The generated BRD includes:

1. Executive Summary
2. Project Background
3. Stakeholders
4. Business Objectives
5. Functional Requirements
6. Non-Functional Requirements
7. Scope (In/Out of Scope, Assumptions, Constraints)
8. Timeline & Milestones
9. Risks & Mitigation
10. Success Metrics

## Example Use Case

**Scenario**: PWC is supervising Supervity company's project to automate their system using AI solutions.

**Process**:
1. Start the application
2. Enter: Client = PWC, Company = Supervity, Topic = AI Solutions for System Automation
3. Answer questions about:
   - What processes need automation
   - What AI solutions are being considered
   - Who are the stakeholders
   - What are the success criteria
   - Timeline and budget constraints
   - Security and compliance requirements
4. Review answers
5. Generate BRD

## Tips for Best Results

- **Be Specific**: Provide detailed answers for better BRD quality
- **Think Comprehensively**: Consider all aspects of the project
- **Use Skip Wisely**: Skip only if you truly don't have information
- **Review Before Generating**: Always review your answers before final BRD generation
- **Add Context**: Use the additional information section to provide context

## Troubleshooting

**API Key Issues**:
- Make sure `GROQ_API_KEY` is set in your `.env` file
- Verify your API key is valid at https://console.groq.com/

**Model Errors**:
- The application automatically tries multiple models if one fails
- Check your Groq account for rate limits or quota issues

**Generation Errors**:
- Ensure you've answered at least a few questions
- Check your internet connection
- Verify API key has sufficient quota

## Future Enhancements

Potential features to add:
- Export to PDF/Word formats
- Web interface version
- Multi-language support
- Template customization
- Integration with project management tools

## License

This is a proof-of-concept application for demonstration purposes.
