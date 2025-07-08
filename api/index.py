from flask import Flask, request, render_template, jsonify
import sys
import os

# Add the parent directory to Python path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all the functions from the main app
from app import (
    extract_text_from_pdf, call_groq_api, generate_mermaid_live_url, 
    generate_drawio_url, validate_and_fix_mermaid, extract_mermaid_code,
    GROQ_API_KEY, client
)

app = Flask(__name__, template_folder='../templates')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Storyboard Generator is running'}), 200

@app.route('/test-api')
def test_api():
    """Test endpoint to check if Groq API is working"""
    print("🧪 Testing Groq API key...")
    test_response = call_groq_api("Hello, please respond with 'Groq API is working perfectly!'", for_mermaid=False)
    if test_response:
        return jsonify({
            'success': True, 
            'response': test_response,
            'api_key_status': 'Groq API working!'
        })
    else:
        return jsonify({
            'success': False, 
            'error': 'Groq API test failed - check logs'
        })

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Please upload a PDF file'}), 400
    
    try:
        # Extract text from PDF
        print("📄 Extracting text from PDF...")
        pdf_text = extract_text_from_pdf(file)
        if not pdf_text:
            return jsonify({'error': 'Could not extract text from PDF'}), 400
        
        print(f"✅ Extracted {len(pdf_text)} characters from PDF")
        
        # Limit text size to avoid API limits
        if len(pdf_text) > 6000:  # Reduced limit for better reliability
            pdf_text = pdf_text[:6000] + "..."
            print(f"⚠️  Text truncated to {len(pdf_text)} characters due to API limits")
        
        # Step 1: Generate steps from storyboard using Groq
        print("🤖 Step 1: Generating steps from storyboard...")
        step1_prompt = f"""Analyze this laboratory storyboard content and extract a clear, organized procedure.

Requirements:
- Use only information from the storyboard content provided
- Start with safety procedures if mentioned
- Include all steps in logical order: Safety → Setup → Main Procedure → Cleanup
- Preserve any decision points or alternative methods mentioned
- Include observations only if specifically mentioned in the storyboard
- Be detailed but practical

Storyboard content:
{pdf_text}

Extract a comprehensive procedure that follows the natural flow described in the storyboard."""
        
        steps_response = call_groq_api(step1_prompt)
        if not steps_response:
            return jsonify({'error': 'Failed to generate steps from Groq API. Please check your API key.'}), 500
        
        print("✅ Step 1 completed: Generated steps")
        
        # Step 2: Create flowchart description using Groq
        print("🤖 Step 2: Creating flowchart representation...")
        step2_prompt = f"""Create a flowchart description that represents this laboratory procedure clearly and logically.

Focus on:
- Clear visual flow from start to finish
- Safety steps at the beginning when mentioned
- Decision points and alternative paths when present
- Logical organization of steps
- Include observations only if mentioned in the original content

Steps from storyboard:
{steps_response}

Create a flowchart description that captures the logical flow and any decision points in the procedure."""
        
        flowchart_response = call_groq_api(step2_prompt)
        if not flowchart_response:
            return jsonify({'error': 'Failed to generate flowchart description from Groq API'}), 500
        
        print("✅ Step 2 completed: Generated flowchart description")
        
        # Step 3: Get mermaid code using Groq with special Mermaid-focused prompt
        print("🤖 Step 3: Generating Mermaid code...")
        step3_prompt = f"""Convert this flowchart description to clean Mermaid syntax.

Requirements:
- Start with 'flowchart TD'
- Use clear, simple node labels
- Show the logical flow with arrows: A[Step] --> B[Next Step]
- Use decision diamonds for choices: C{{Question?}} --> |Yes| D[Action]
- Keep it clean and readable
- Follow the flowchart description provided

Flowchart description to convert:
{flowchart_response}

Generate clean Mermaid code that represents this flowchart."""
        
        mermaid_response = call_groq_api(step3_prompt, for_mermaid=True)
        if not mermaid_response:
            return jsonify({'error': 'Failed to generate mermaid code from Groq API'}), 500
        
        # Clean the response to extract only the Mermaid code
        mermaid_response = extract_mermaid_code(mermaid_response)
        
        # Validate and fix Mermaid syntax
        mermaid_response = validate_and_fix_mermaid(mermaid_response)
        
        print("✅ Step 3 completed: Generated Mermaid code")
        
        # Generate URLs for visualization
        print("🔗 Generating visualization URLs...")
        drawio_url = generate_drawio_url(mermaid_response)
        mermaid_live_url = generate_mermaid_live_url(mermaid_response)
        
        print("🎉 All steps completed successfully!")
        
        return jsonify({
            'success': True,
            'steps': steps_response,
            'flowchart_description': flowchart_response,
            'mermaid_code': mermaid_response,
            'drawio_url': drawio_url,
            'mermaid_live_url': mermaid_live_url
        })
        
    except Exception as e:
        print(f"❌ Error processing file: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

# Vercel serverless function handler
def handler(request):
    with app.app_context():
        return app.full_dispatch_request()

# For Vercel
app_handler = app
