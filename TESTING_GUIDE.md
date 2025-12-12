# AIBA Web Application - Testing Guide

## For Managers & Testers

This guide will help you quickly set up and test the AIBA (AI Business Analyst) web application.

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Clone the Repository
```bash
git clone https://github.com/pornima1supervity/AIBA.git
cd AIBA
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Set Up API Key
1. Get a free Groq API key from: https://console.groq.com/
2. Create a `.env` file in the project directory:
   ```bash
   echo "GROQ_API_KEY=your_api_key_here" > .env
   ```
   Or manually create `.env` file with:
   ```
   GROQ_API_KEY=your_actual_api_key_here
   ```

### Step 4: Start the Application
```bash
python app.py
```

### Step 5: Open in Browser
Open your browser and go to: **http://localhost:5001**

---

## 📋 Testing Checklist

### Basic Functionality
- [ ] Application loads without errors
- [ ] Project setup form accepts input
- [ ] Can start a conversation
- [ ] Questions appear one by one
- [ ] Can submit answers
- [ ] Progress bar updates correctly
- [ ] Can skip questions
- [ ] Can add additional information
- [ ] BRD generates successfully
- [ ] Can download PDF

### User Experience
- [ ] Interface is clean and professional
- [ ] Navigation is intuitive
- [ ] Error messages are clear
- [ ] Loading states are visible
- [ ] Responsive on mobile/tablet

### Edge Cases
- [ ] Empty form submission shows error
- [ ] Network errors handled gracefully
- [ ] PDF generation works (or fails gracefully)
- [ ] Can start a new project after completion

---

## 🧪 Test Scenarios

### Scenario 1: Complete BRD Generation
1. Enter:
   - Client Name: "Test Client"
   - Company Name: "Test Company"
   - Project Topic: "AI Automation System"
2. Answer all 10 questions thoroughly
3. Add additional information
4. Generate BRD
5. Download PDF
6. Verify PDF contains all information

### Scenario 2: Quick Test (Skip Questions)
1. Enter project details
2. Skip first 3 questions
3. Answer questions 4-7
4. Skip remaining questions
5. Generate BRD
6. Verify BRD is still generated

### Scenario 3: Additional Information
1. Complete project setup
2. Answer 5 questions
3. Add 3 pieces of additional information
4. Generate BRD
5. Verify additional info is included

---

## 🐛 Known Issues / Limitations

1. **PDF Generation**: Requires system dependencies on macOS
   - If PDF fails, Markdown file is still available
   - Install with: `brew install pango gdk-pixbuf libffi`

2. **API Rate Limits**: Groq API has rate limits
   - Free tier: Limited requests per minute
   - If you hit limits, wait a minute and try again

3. **Port Conflicts**: Default port is 5001
   - If port is busy, change in `app.py` line 280

---

## 📊 Expected Results

### Successful BRD Generation Should Include:
- ✅ Executive Summary
- ✅ Project Background
- ✅ Stakeholders
- ✅ Business Objectives
- ✅ Functional Requirements
- ✅ Non-Functional Requirements
- ✅ Scope (In/Out)
- ✅ Timeline & Milestones
- ✅ Risks & Mitigation
- ✅ Success Metrics

### Generated Files:
- `BRD_ClientName_CompanyName_TIMESTAMP.md` - Markdown file
- `BRD_ClientName_CompanyName_TIMESTAMP.pdf` - PDF file (if supported)
- `Conversation_ClientName_CompanyName_TIMESTAMP.json` - Conversation history

---

## 💡 Tips for Testing

1. **Use Realistic Data**: Test with actual project scenarios
2. **Test Error Handling**: Try invalid inputs, network issues
3. **Check Browser Console**: Press F12 to see any errors
4. **Review Generated BRD**: Verify quality and completeness
5. **Test on Different Browsers**: Chrome, Firefox, Safari

---

## 🆘 Troubleshooting

### Application Won't Start
- Check Python version: `python --version` (should be 3.8+)
- Verify dependencies: `pip list | grep flask`
- Check port availability: `lsof -i :5001`

### API Errors
- Verify `.env` file exists and has correct API key
- Check API key is valid at https://console.groq.com/
- Check API quota/credits

### PDF Not Generating
- Check server logs for errors
- Verify system dependencies installed
- PDF generation is optional - Markdown still works

### Download Not Working
- Check browser console (F12) for errors
- Verify files exist in project directory
- Check server logs for download errors

---

## 📞 Support

If you encounter issues:
1. Check server terminal for error messages
2. Check browser console (F12) for JavaScript errors
3. Review this guide's troubleshooting section
4. Contact the development team

---

## ✅ Feedback Form

After testing, please provide feedback on:
- [ ] Overall user experience
- [ ] BRD quality and completeness
- [ ] Any bugs or issues found
- [ ] Suggestions for improvement
- [ ] Performance concerns

---

**Thank you for testing AIBA!** 🎉

