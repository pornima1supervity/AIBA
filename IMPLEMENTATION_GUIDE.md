# AIBA Agent Improvements - Implementation Guide

## Quick Start: Implementing Improvements

This guide provides step-by-step instructions for implementing the most impactful improvements to AIBA.

---

## 🎯 Priority 1: Answer Quality Validation (Week 1)

### Step 1: Integrate Answer Validation

1. **Import the validation module** in `app.py`:
```python
from answer_validation import validate_answer_quality, generate_probing_question
```

2. **Update `submit_answer()` function** in `app.py`:
```python
@app.route('/api/submit-answer', methods=['POST'])
def submit_answer():
    # ... existing code ...
    
    # Add validation before processing
    validation_result = validate_answer_quality(
        answer=answer,
        question=question,
        question_type=conversation_phase,
        conversation_context=conversation_history[-10:]  # Last 10 messages
    )
    
    # If answer quality is low, return feedback
    if not validation_result['is_valid']:
        return jsonify({
            'success': False,
            'validation': validation_result,
            'message': 'Please provide a more detailed answer.'
        }), 400
    
    # If should probe, generate probing question
    if validation_result['should_probe']:
        probe_question = generate_probing_question(
            answer, question, validation_result, conversation_history
        )
        if probe_question:
            # Add probing question to response
            pass
    
    # ... rest of existing code ...
```

3. **Update frontend** (`static/js/app.js`):
```javascript
// In handleSubmitAnswer(), handle validation errors
if (!data.success && data.validation) {
    alert(data.validation.feedback);
    // Optionally show validation details in UI
    return;
}
```

### Benefits
- ✅ Higher quality answers
- ✅ Better requirements capture
- ✅ Reduced BRD revisions

---

## 🎯 Priority 2: Requirements Completeness Scoring (Week 2)

### Step 1: Add Completeness Endpoint

1. **Add new endpoint** in `app.py`:
```python
from requirements_completeness import calculate_completeness_score, get_completeness_dashboard

@app.route('/api/completeness', methods=['POST'])
def check_completeness():
    """Check requirements completeness"""
    data = request.json
    conversation_history = data.get('conversation_history', [])
    project_type = data.get('project_type', 'ai_ml')
    project_context = data.get('project_context', '')
    
    result = calculate_completeness_score(
        conversation_history, 
        project_type, 
        project_context
    )
    
    dashboard = get_completeness_dashboard(result)
    
    return jsonify({
        'success': True,
        'completeness': dashboard
    })
```

2. **Call from frontend** periodically:
```javascript
// In app.js, add function to check completeness
async function checkCompleteness() {
    try {
        const response = await fetch(`${API_BASE}/api/completeness`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                conversation_history: state.conversationHistory,
                project_type: 'ai_ml',
                project_context: state.projectContext
            })
        });
        
        const data = await response.json();
        if (data.success) {
            updateCompletenessUI(data.completeness);
        }
    } catch (error) {
        console.error('Error checking completeness:', error);
    }
}

// Call after each answer submission
// In handleSubmitAnswer(), after success:
checkCompleteness();
```

3. **Add UI component** in `templates/index.html`:
```html
<!-- Add to conversation step -->
<div id="completeness-dashboard" class="completeness-dashboard" style="display: none;">
    <h3>Requirements Completeness</h3>
    <div class="overall-score">
        <div class="score-circle" id="overall-score-circle">
            <span id="overall-score-text">0%</span>
        </div>
        <p id="overall-message">Gathering requirements...</p>
    </div>
    <div class="section-scores" id="section-scores"></div>
    <div class="recommendations" id="recommendations"></div>
</div>
```

### Benefits
- ✅ Users know what's missing
- ✅ Better BRD quality
- ✅ Reduced discovery time

---

## 🎯 Priority 3: Enhanced Error Handling (Week 1-2)

### Step 1: Create Error Handler Module

Create `error_handler.py`:
```python
import time
import logging
from functools import wraps

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def retry_with_backoff(max_retries=3, base_delay=1, max_delay=60):
    """Decorator for retrying with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = base_delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    error_str = str(e).lower()
                    
                    # Don't retry on certain errors
                    if any(x in error_str for x in ['invalid', 'not_found', '400', '401']):
                        raise e
                    
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                        time.sleep(delay)
                        delay = min(delay * 2, max_delay)
                    else:
                        logger.error(f"All {max_retries} attempts failed")
            
            raise last_exception
        return wrapper
    return decorator

def handle_api_error(error, context=""):
    """Convert API errors to user-friendly messages"""
    error_str = str(error).lower()
    
    if "rate_limit" in error_str or "429" in error_str:
        return {
            "user_message": "API rate limit reached. Please wait a moment and try again.",
            "technical": "Rate limit exceeded",
            "retry_after": 60
        }
    elif "quota" in error_str or "insufficient" in error_str:
        return {
            "user_message": "API quota exceeded. Please check your API key limits.",
            "technical": "Quota exceeded",
            "retry_after": None
        }
    elif "timeout" in error_str:
        return {
            "user_message": "Request timed out. Please try again.",
            "technical": "Timeout",
            "retry_after": 5
        }
    else:
        return {
            "user_message": "An error occurred. Please try again or contact support.",
            "technical": str(error),
            "retry_after": 5
        }
```

### Step 2: Apply to API Calls

Update `customer_research.py`:
```python
from error_handler import retry_with_backoff, handle_api_error

@retry_with_backoff(max_retries=3)
def research_customer(customer_name, company_name=None):
    try:
        # ... existing code ...
    except Exception as e:
        error_info = handle_api_error(e, f"Researching {customer_name}")
        logger.error(f"Research error: {error_info['technical']}")
        # Return user-friendly error
        return None, None
```

### Benefits
- ✅ Better reliability
- ✅ User-friendly errors
- ✅ Automatic retries

---

## 🎯 Priority 4: Session Persistence (Week 2-3)

### Step 1: Add Database

1. **Install SQLite** (already in Python):
```bash
# No installation needed, SQLite is built-in
```

2. **Create database schema** (`database.py`):
```python
import sqlite3
import json
from datetime import datetime
from uuid import uuid4

def init_database():
    """Initialize database tables"""
    conn = sqlite3.connect('aiba_sessions.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            client_name TEXT,
            company_name TEXT,
            project_topic TEXT,
            customer_research TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            status TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            role TEXT,
            content TEXT,
            timestamp TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def save_session(session_id, client_name, company_name, project_topic, customer_research):
    """Save or update session"""
    conn = sqlite3.connect('aiba_sessions.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO sessions 
        (id, client_name, company_name, project_topic, customer_research, updated_at, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (session_id, client_name, company_name, project_topic, customer_research, 
          datetime.now(), 'active'))
    
    conn.commit()
    conn.close()

def save_conversation_message(session_id, role, content):
    """Save conversation message"""
    conn = sqlite3.connect('aiba_sessions.db')
    cursor = conn.cursor()
    
    message_id = str(uuid4())
    cursor.execute('''
        INSERT INTO conversations (id, session_id, role, content, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (message_id, session_id, role, content, datetime.now()))
    
    conn.commit()
    conn.close()

def load_session(session_id):
    """Load session and conversation"""
    conn = sqlite3.connect('aiba_sessions.db')
    cursor = conn.cursor()
    
    # Get session
    cursor.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
    session = cursor.fetchone()
    
    if not session:
        return None
    
    # Get conversation
    cursor.execute('SELECT role, content FROM conversations WHERE session_id = ? ORDER BY timestamp', 
                   (session_id,))
    messages = [{'role': row[0], 'content': row[1]} for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        'session': session,
        'conversation': messages
    }
```

3. **Update app.py** to use database:
```python
from database import init_database, save_session, save_conversation_message, load_session

# Initialize on startup
init_database()

@app.route('/api/start-project', methods=['POST'])
def start_project():
    # ... existing code ...
    
    # Generate session ID
    session_id = str(uuid4())
    
    # Save session
    save_session(session_id, client_name, company_name, project_topic, customer_research)
    
    return jsonify({
        'success': True,
        'session_id': session_id,  # Return to frontend
        # ... rest of response ...
    })
```

### Benefits
- ✅ No data loss
- ✅ Session recovery
- ✅ History tracking

---

## 📊 Testing Your Improvements

### Test Answer Validation
```python
# Test script
from answer_validation import validate_answer_quality

result = validate_answer_quality(
    answer="We need automation",
    question="What are your primary business objectives?",
    question_type="discovery"
)
assert result['is_valid'] == False  # Should be invalid (too vague)
```

### Test Completeness Scoring
```python
# Test script
from requirements_completeness import calculate_completeness_score

conversation = [
    {"role": "assistant", "content": "What are your objectives?"},
    {"role": "user", "content": "Automate customer service"}
]

result = calculate_completeness_score(conversation, "ai_ml")
assert 0 <= result['overall_score'] <= 1
```

---

## 🚀 Deployment Checklist

- [ ] Test all new features locally
- [ ] Update requirements.txt if needed
- [ ] Add error logging
- [ ] Update documentation
- [ ] Test error scenarios
- [ ] Performance testing
- [ ] User acceptance testing

---

## 📝 Next Steps

1. **Week 1**: Implement answer validation and error handling
2. **Week 2**: Add completeness scoring and session persistence
3. **Week 3**: UI improvements and testing
4. **Week 4**: Documentation and deployment

---

## 💡 Tips

- Start with one improvement at a time
- Test thoroughly before moving to next
- Get user feedback early
- Keep backward compatibility
- Document changes

---

*For detailed improvement roadmap, see `AGENT_IMPROVEMENTS.md`*

