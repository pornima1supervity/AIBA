# Quick Start Guide - AIBA Web Application

## Step-by-Step Instructions

### 1. Install Dependencies

Make sure you have all required Python packages installed:

```bash
cd /Users/pornimagaikwad/Downloads/AIBA
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the project directory with your Groq API key:

```bash
# Create .env file
echo "GROQ_API_KEY=your_api_key_here" > .env
```

Or manually create `.env` file with:
```
GROQ_API_KEY=your_actual_api_key_here
```

**Get your API key from:** https://console.groq.com/

### 3. Start the Web Server

Run the Flask application:

```bash
python app.py
```

You should see output like:
```
 * Running on http://0.0.0.0:5000
 * Running on http://127.0.0.1:5000
```

### 4. Open in Browser

Open your web browser and navigate to:

**Local access:**
- http://localhost:5000
- http://127.0.0.1:5000

**Network access (from other devices):**
- http://your-computer-ip:5000

### 5. Use the Application

1. **Project Setup**: Enter Client Name, Company Name, and Project Topic
2. **Answer Questions**: Respond to 10 structured questions
3. **Add Information**: Provide any additional details
4. **Generate BRD**: Click "Generate BRD" to create your document
5. **Download**: Download the BRD as Markdown (.md) or PDF (.pdf)

### 6. Stop the Server

Press `Ctrl+C` in the terminal where the server is running.

---

## Troubleshooting

### Port Already in Use

If port 5000 is already in use, edit `app.py` and change the port:

```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change 5000 to 5001
```

### Missing Dependencies

If you get import errors, install missing packages:

```bash
pip install flask groq python-dotenv markdown weasyprint
```

### PDF Generation Not Working

On macOS, install system dependencies:

```bash
brew install pango gdk-pixbuf libffi
```

PDF generation will gracefully fail if dependencies are missing - you'll still get Markdown files.

### API Key Issues

Make sure your `.env` file is in the same directory as `app.py` and contains:
```
GROQ_API_KEY=your_key_here
```

---

## Alternative: Command Line Version

If you prefer the command-line interface instead of the web app:

```bash
python interactive_brd_generator.py
```

---

## File Structure

```
AIBA/
├── app.py                      # Flask web server (run this!)
├── interactive_brd_generator.py # CLI version
├── templates/
│   └── index.html             # Web interface
├── static/
│   ├── css/style.css          # Styles
│   └── js/app.js              # Frontend logic
└── requirements.txt           # Python dependencies
```

---

## Need Help?

Check the full documentation in `README_WEB_APP.md` for more details.

