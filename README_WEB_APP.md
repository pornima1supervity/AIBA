# AIBA Web Application

A professional web-based interface for the AIBA (AI Business Analyst) BRD Generator.

## Features

- 🎨 **Modern, Professional UI** - Clean and intuitive interface designed for stakeholder meetings
- 💬 **Interactive Conversation** - Real-time chat interface for requirements gathering
- 📊 **Progress Tracking** - Visual progress bar showing question completion
- 📄 **Automatic BRD Generation** - Generates comprehensive Business Requirements Documents
- 📑 **Multiple Formats** - Download BRD as Markdown (.md) or PDF (.pdf)
- 🔄 **Session Management** - Start new projects easily

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure you have a `.env` file with your Groq API key:
```
GROQ_API_KEY=your_api_key_here
```

3. (Optional) For PDF generation on macOS, install system dependencies:
```bash
brew install pango gdk-pixbuf libffi
```

## Running the Application

Start the Flask web server:
```bash
python app.py
```

The application will be available at:
- **Local**: http://localhost:5000
- **Network**: http://0.0.0.0:5000 (accessible from other devices on your network)

## Usage

### Step 1: Project Setup
- Enter Client Name (e.g., PWC)
- Enter Company Name (e.g., Supervity)
- Enter Project Topic/Objective
- Click "Start Conversation"

### Step 2: Requirements Gathering
- Answer 10 structured questions about your project
- Each answer is processed by AIBA for follow-up questions
- Use "Skip" to move to the next question
- Progress bar shows completion status

### Step 3: Additional Information
- Add any extra details or ask questions
- AIBA will respond and help clarify requirements
- Click "Generate BRD" when ready

### Step 4: BRD Generation
- The system processes your requirements
- A comprehensive BRD is generated automatically

### Step 5: Download
- Preview the generated BRD
- Download as Markdown (.md) file
- Download as PDF (.pdf) file (if available)
- Start a new project if needed

## File Structure

```
AIBA/
├── app.py                      # Flask web application
├── interactive_brd_generator.py # BRD generation logic
├── templates/
│   └── index.html             # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css          # Professional styling
│   └── js/
│       └── app.js             # Frontend JavaScript
└── requirements.txt           # Python dependencies
```

## API Endpoints

- `GET /` - Main application page
- `POST /api/start-project` - Initialize new project
- `POST /api/get-question` - Get next question
- `POST /api/submit-answer` - Submit answer and get AI response
- `POST /api/add-additional-info` - Add additional information
- `POST /api/generate-brd` - Generate BRD document
- `GET /api/download/<filename>` - Download generated files

## Browser Compatibility

- Chrome/Edge (recommended)
- Firefox
- Safari
- Mobile browsers (responsive design)

## Troubleshooting

### PDF Generation Not Working
- Ensure system dependencies are installed (see Installation)
- Check that WeasyPrint can access required libraries
- PDF generation will gracefully fail and only Markdown will be available

### API Errors
- Verify your GROQ_API_KEY is set in `.env` file
- Check your Groq API quota/credits
- Ensure internet connection is active

### Port Already in Use
- Change the port in `app.py`: `app.run(port=5001)`
- Or kill the process using port 5000

## Tips for Best Results

1. **Be Thorough**: Provide detailed answers for better BRD quality
2. **Use Additional Info**: Add context in the additional information section
3. **Review Before Generating**: Make sure all important details are included
4. **Save Conversations**: Conversation history is saved as JSON for future reference

## Support

For issues or questions, check the main README_BRD_GENERATOR.md file.

