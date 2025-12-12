
let state = {
    currentStep: 'project-setup',
    projectContext: null,
    clientName: '',
    companyName: '',
    projectTopic: '',
    conversationHistory: [],
    questionIndex: 0,
    totalQuestions: 10,
    brdData: null
};

// API Base URL
const API_BASE = '';

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
});

function initializeEventListeners() {
    // Project setup form
    const projectForm = document.getElementById('project-setup-form');
    if (projectForm) {
        projectForm.addEventListener('submit', handleProjectSetup);
    }
    
    // Answer submission
    const submitBtn = document.getElementById('submit-answer-btn');
    if (submitBtn) {
        submitBtn.addEventListener('click', handleSubmitAnswer);
    }
    
    const skipBtn = document.getElementById('skip-btn');
    if (skipBtn) {
        skipBtn.addEventListener('click', handleSkipQuestion);
    }
    
    // Additional info
    const addInfoBtn = document.getElementById('add-info-btn');
    if (addInfoBtn) {
        addInfoBtn.addEventListener('click', handleAddAdditionalInfo);
    }
    
    const proceedBtn = document.getElementById('proceed-to-brd-btn');
    if (proceedBtn) {
        proceedBtn.addEventListener('click', handleGenerateBRD);
    }
    
    // Downloads
    const downloadMdBtn = document.getElementById('download-md-btn');
    if (downloadMdBtn) {
        downloadMdBtn.addEventListener('click', handleDownloadMD);
    }
    
    const downloadPdfBtn = document.getElementById('download-pdf-btn');
    if (downloadPdfBtn) {
        downloadPdfBtn.addEventListener('click', handleDownloadPDF);
    }
    
    const newProjectBtn = document.getElementById('new-project-btn');
    if (newProjectBtn) {
        newProjectBtn.addEventListener('click', handleNewProject);
    }
    
    // Enter key handlers
    const answerInput = document.getElementById('answer-input');
    if (answerInput) {
        answerInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                e.preventDefault();
                handleSubmitAnswer();
            }
        });
    }
    
    const additionalInput = document.getElementById('additional-input');
    if (additionalInput) {
        additionalInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                e.preventDefault();
                handleAddAdditionalInfo();
            }
        });
    }
}

// Step Management
function showStep(stepId) {
    document.querySelectorAll('.step').forEach(step => {
        step.classList.remove('active');
    });
    document.getElementById(stepId).classList.add('active');
    state.currentStep = stepId;
}

function updateProgress(current, total) {
    const percentage = (current / total) * 100;
    document.getElementById('progress-fill').style.width = `${percentage}%`;
    document.getElementById('progress-text').textContent = `Question ${current}/${total}`;
}

// Project Setup
async function handleProjectSetup(e) {
    e.preventDefault();
    
    const formData = {
        client_name: document.getElementById('client_name').value,
        company_name: document.getElementById('company_name').value,
        project_topic: document.getElementById('project_topic').value
    };
    
    try {
        const response = await fetch(`${API_BASE}/api/start-project`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: `HTTP ${response.status}` }));
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            state.projectContext = data.project_context;
            state.clientName = data.client_name;
            state.companyName = data.company_name;
            state.projectTopic = data.project_topic;
            state.totalQuestions = data.total_questions;
            
            showStep('step-conversation');
            loadNextQuestion();
        } else {
            alert('Error: ' + (data.error || 'Failed to start project'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    }
}

// Question Management
async function loadNextQuestion() {
    // Check if we have completed all questions
    if (state.questionIndex >= state.totalQuestions) {
        showStep('step-additional-info');
        displayAdditionalInfoWelcome();
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/get-question`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                question_index: state.questionIndex
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        if (data.question) {
            displayQuestion(data.question, data.question_index);
            updateProgress(data.question_index + 1, data.total_questions);
        } else {
            // No more questions, move to additional info
            showStep('step-additional-info');
            displayAdditionalInfoWelcome();
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred loading the question: ' + error.message);
    }
}

function displayQuestion(question, index) {
    const questionDiv = document.getElementById('current-question');
    if (questionDiv) {
        questionDiv.innerHTML = `
            <h3>Question ${index + 1}/${state.totalQuestions}</h3>
            <p>${question}</p>
        `;
    }
    
    const answerInput = document.getElementById('answer-input');
    if (answerInput) {
        answerInput.value = '';
        answerInput.focus();
    }
}

// Answer Submission
async function handleSubmitAnswer() {
    const answerInput = document.getElementById('answer-input');
    if (!answerInput) {
        console.error('Answer input element not found');
        return;
    }
    
    const answer = answerInput.value.trim();
    
    if (!answer) {
        alert('Please enter an answer or click Skip.');
        return;
    }
    
    const questionElement = document.querySelector('#current-question p');
    if (!questionElement) {
        alert('Question not found. Please refresh the page.');
        return;
    }
    
    const question = questionElement.textContent;
    
    try {
        const response = await fetch(`${API_BASE}/api/submit-answer`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                question: question,
                answer: answer,
                conversation_history: state.conversationHistory,
                question_index: state.questionIndex
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            // Add messages to conversation
            addMessage('assistant', question);
            addMessage('user', answer);
            
            if (data.ai_response) {
                addMessage('assistant', data.ai_response);
            }
            
            state.conversationHistory = data.conversation_history || state.conversationHistory;
            state.questionIndex = data.next_question_index;
            
            // Move to next question or additional info
            if (state.questionIndex >= state.totalQuestions) {
                setTimeout(() => {
                    showStep('step-additional-info');
                    displayAdditionalInfoWelcome();
                }, 1000);
            } else {
                setTimeout(() => {
                    loadNextQuestion();
                }, 1000);
            }
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred submitting your answer: ' + (error.message || 'Unknown error'));
    }
}

async function handleSkipQuestion() {
    // Add skip to conversation history if there is a current question
    const currentQuestionDiv = document.getElementById('current-question');
    if (currentQuestionDiv && currentQuestionDiv.querySelector('p')) {
        const question = currentQuestionDiv.querySelector('p').textContent;
        state.conversationHistory.push({
            "role": "assistant",
            "content": question
        });
        state.conversationHistory.push({
            "role": "user",
            "content": "skip"
        });
    }
    
    state.questionIndex++;
    
    if (state.questionIndex >= state.totalQuestions) {
        showStep('step-additional-info');
        displayAdditionalInfoWelcome();
    } else {
        loadNextQuestion();
    }
}

// Additional Information
function displayAdditionalInfoWelcome() {
    const messagesDiv = document.getElementById('additional-messages');
    messagesDiv.innerHTML = `
        <div class="message assistant">
            <p class="message-content">Great! You've completed all the structured questions. Feel free to add any additional information or ask questions. When you're ready, click "Generate BRD" to create your Business Requirements Document.</p>
        </div>
    `;
}

async function handleAddAdditionalInfo() {
    const input = document.getElementById('additional-input').value.trim();
    
    if (!input) {
        alert('Please enter some information.');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/add-additional-info`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_input: input,
                conversation_history: state.conversationHistory
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            addAdditionalMessage('user', input);
            if (data.ai_response) {
                addAdditionalMessage('assistant', data.ai_response);
            }
            state.conversationHistory = data.conversation_history || state.conversationHistory;
            document.getElementById('additional-input').value = '';
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred: ' + (error.message || 'Unknown error'));
    }
}

// BRD Generation
async function handleGenerateBRD() {
    showStep('step-brd-generation');
    
    try {
        const response = await fetch(`${API_BASE}/api/generate-brd`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                conversation_history: state.conversationHistory,
                project_context: state.projectContext,
                client_name: state.clientName,
                company_name: state.companyName
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            state.brdData = data;
            displayBRDResult(data);
        } else {
            alert('Error generating BRD: ' + (data.error || 'Unknown error'));
            showStep('step-additional-info');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred generating the BRD: ' + (error.message || 'Unknown error'));
        showStep('step-additional-info');
    }
}

function displayBRDResult(data) {
    showStep('step-brd-result');
    
    const previewDiv = document.getElementById('brd-preview');
    if (previewDiv) {
        previewDiv.textContent = data.brd_content;
    }
    
    // Show PDF download button if PDF was generated
    const pdfBtn = document.getElementById('download-pdf-btn');
    if (pdfBtn) {
        if (data.pdf_filename) {
            pdfBtn.style.display = 'inline-flex';
        } else {
            pdfBtn.style.display = 'none';
        }
    }
    
    // Debug logging
    console.log('BRD Generation Result:', {
        md_filename: data.md_filename,
        pdf_filename: data.pdf_filename,
        has_content: !!data.brd_content,
        success: data.success,
        full_data: data
    });
    
    // Show alert if filenames are missing
    if (!data.md_filename) {
        console.warn('WARNING: md_filename is missing from response');
        console.warn('Response data:', JSON.stringify(data, null, 2));
        
        // Try to generate filename from project data if available
        if (state.clientName && state.companyName) {
            const timestamp = new Date().toISOString().replace(/[-:]/g, '').split('.')[0].replace('T', '_');
            const projectName = `${state.clientName}_${state.companyName}`.replace(/\s+/g, '_');
            const generatedFilename = `BRD_${projectName}_${timestamp}.md`;
            console.log('Generated fallback filename:', generatedFilename);
            data.md_filename = generatedFilename;
            state.brdData.md_filename = generatedFilename;
        } else {
            alert('Warning: Markdown filename not received. Download may not work. Please check server logs.');
        }
    }
}

// Downloads
async function handleDownloadMD() {
    // Download PDF instead of markdown
    if (!state.brdData) {
        alert('BRD data not available. Please generate the BRD first.');
        return;
    }
    
    // Prefer PDF if available, otherwise try to generate it from markdown
    let filename = state.brdData.pdf_filename;
    
    if (!filename && state.brdData.md_filename) {
        // If PDF doesn't exist, try to convert markdown to PDF on the fly
        console.log('PDF not available, attempting to convert markdown to PDF...');
        try {
            const response = await fetch(`${API_BASE}/api/convert-to-pdf`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    md_filename: state.brdData.md_filename,
                    brd_content: state.brdData.brd_content
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.pdf_filename) {
                    filename = data.pdf_filename;
                    state.brdData.pdf_filename = filename;
                }
            }
        } catch (error) {
            console.error('Error converting to PDF:', error);
        }
    }
    
    if (!filename) {
        alert('PDF file not available. PDF generation may have failed or is not supported.\n\nPlease check the server logs for details.');
        return;
    }
    
    try {
        console.log('Downloading PDF file:', filename);
        
        const downloadUrl = `${API_BASE}/api/download/${encodeURIComponent(filename)}`;
        console.log('Download URL:', downloadUrl);
        
        // Use fetch to download the file as blob
        const response = await fetch(downloadUrl);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: `HTTP ${response.status}` }));
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        
        // Create a temporary anchor element to trigger download
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        
        // Clean up
        setTimeout(() => {
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
        }, 100);
        
        console.log('Download started successfully');
    } catch (error) {
        console.error('Download error:', error);
        alert('Error downloading PDF: ' + (error.message || 'Unknown error') + '\n\nPlease check the browser console for details.');
    }
}

async function handleDownloadPDF() {
    if (!state.brdData || !state.brdData.pdf_filename) {
        alert('PDF file not available. PDF generation may have failed or is not supported.');
        return;
    }
    
    try {
        const filename = state.brdData.pdf_filename;
        console.log('Downloading PDF file:', filename);
        
        const downloadUrl = `${API_BASE}/api/download/${encodeURIComponent(filename)}`;
        console.log('Download URL:', downloadUrl);
        
        // Use fetch to download the file as blob
        const response = await fetch(downloadUrl);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: `HTTP ${response.status}` }));
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        
        // Create a temporary anchor element to trigger download
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        
        // Clean up
        setTimeout(() => {
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
        }, 100);
        
        console.log('Download started successfully');
    } catch (error) {
        console.error('Download error:', error);
        alert('Error downloading PDF: ' + (error.message || 'Unknown error') + '\n\nPlease check the browser console for details.');
    }
}

function handleNewProject() {
    // Reset state
    state = {
        currentStep: 'project-setup',
        projectContext: null,
        clientName: '',
        companyName: '',
        projectTopic: '',
        conversationHistory: [],
        questionIndex: 0,
        totalQuestions: 10,
        brdData: null
    };
    
    // Reset forms
    document.getElementById('project-setup-form').reset();
    document.getElementById('conversation-messages').innerHTML = '';
    document.getElementById('additional-messages').innerHTML = '';
    document.getElementById('brd-preview').textContent = '';
    document.getElementById('download-pdf-btn').style.display = 'none';
    
    showStep('step-project-setup');
}

// Message Display
function addMessage(role, content) {
    const messagesDiv = document.getElementById('conversation-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    messageDiv.innerHTML = `<p class="message-content">${escapeHtml(content)}</p>`;
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function addAdditionalMessage(role, content) {
    const messagesDiv = document.getElementById('additional-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    messageDiv.innerHTML = `<p class="message-content">${escapeHtml(content)}</p>`;
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

