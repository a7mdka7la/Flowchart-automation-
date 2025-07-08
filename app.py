from flask import Flask, request, render_template, jsonify, send_file
import requests
import PyPDF2
import os
import json
import tempfile
import base64
import re
import time
from io import BytesIO
import webbrowser
import urllib.parse
from groq import Groq

# Load environment variables from .env file for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available in production, environment variables will be set by platform
    pass

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Add error handling for better debugging
import logging
if os.environ.get('FLASK_ENV') == 'production':
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig(level=logging.DEBUG)

# AI API configuration - UPDATED TO USE GROQ API (FREE & FAST!)
GROQ_API_KEY = os.getenv('GROQ_API_KEY')  # Get from environment variables only

# Initialize Groq client
try:
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable is required")
    client = Groq(api_key=GROQ_API_KEY)
    print(f"🚀 Groq client initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize Groq client: {e}")
    client = None

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

def call_groq_api(prompt, max_retries=3, for_mermaid=False):
    """Make API call to Groq API - FREE, FAST & Dynamic responses for any storyboard"""
    print(f"🔥 Using Groq API - FREE & FAST!")
    print(f" Prompt length: {len(prompt)} characters")
    
    if not client:
        print("❌ Groq client not initialized")
        return None
    
    # Dynamic system prompt based on request type
    if for_mermaid:
        system_content = """You are an expert Mermaid flowchart generator. Create clear, well-structured flowcharts from the provided content.

Guidelines:
- Return only Mermaid syntax (no explanations or markdown blocks)
- Start with 'flowchart TD' for top-down layout
- Use clear, descriptive labels for each step
- Include decision points where choices need to be made
- Show the logical flow from start to finish
- Use proper Mermaid syntax: A[Step] --> B[Next Step] and A{Decision?} --> |Yes| B[Action]

Generate the best possible flowchart that captures the essence and flow of the procedure."""
        temperature = 0.6  # Balanced for creativity and precision
    else:
        system_content = """You are a laboratory procedure analyst. Extract clear, organized procedures from the provided content.

Key Focus:
- Use only information from the provided content
- Start with safety procedures when mentioned
- Organize logically: Safety → Setup → Main Procedure → Cleanup
- Include decision points and alternative methods when present
- Be practical and detailed but not overly complex
- Include observations only if specifically mentioned in the content

Create a comprehensive procedure that follows the natural flow described in the content."""
        temperature = 0.7  # Higher for creative descriptions
    
    for attempt in range(max_retries):
        try:
            print(f"🌐 Making API call to Groq (attempt {attempt + 1}/{max_retries})")
            
            # Use Groq's chat completions API with dynamic system prompt
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_content
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama-3.3-70b-versatile",  # FREE Groq model - very fast!
                temperature=temperature,
                max_tokens=4000
            )
            
            print("✅ Groq API call successful!")
            content = response.choices[0].message.content
            print(f"📄 Response preview: {content[:100]}...")
            return content
            
        except Exception as e:
            print(f"❌ Groq API Error (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(1)  # Short delay before retry
                continue
            else:
                print("❌ All Groq API retry attempts failed")
                return None
    
    return None

def generate_mermaid_live_url(mermaid_code):
    """Generate Mermaid Live Editor URL"""
    try:
        # Clean the mermaid code
        clean_code = mermaid_code.strip()
        if clean_code.startswith('```mermaid'):
            clean_code = clean_code.replace('```mermaid', '').replace('```', '').strip()
        elif clean_code.startswith('```'):
            clean_code = clean_code.replace('```', '').strip()
        
        # Base64 encode for Mermaid Live
        import base64
        encoded = base64.b64encode(clean_code.encode('utf-8')).decode('utf-8')
        return f"https://mermaid.live/edit#pako:{encoded}"
    except Exception as e:
        print(f"Error generating Mermaid Live URL: {e}")
        return "https://mermaid.live/"

def generate_drawio_url(mermaid_code):
    """Generate draw.io URL - simplified approach"""
    # For reliability, just open Draw.io and let user paste manually
    return "https://app.diagrams.net/?splash=0&ui=kennedy&iconfont=1&p=mermaiddiagram"

def validate_and_fix_mermaid(mermaid_code):
    """Validate and fix common Mermaid syntax errors"""
    try:
        import re
        
        lines = mermaid_code.strip().split('\n')
        fixed_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip explanatory text lines
            if any(phrase in line.lower() for phrase in [
                'here is', 'this is', 'the following', 'note:', 'explanation', 
                'however', 'to better', 'we can use', 'this represents'
            ]):
                continue
            
            # Fix common Mermaid syntax issues
            if 'flowchart' in line:
                fixed_lines.append(line)
                continue
            
            # Fix the specific |> arrow issue that causes TAGEND errors
            line = re.sub(r'\|>', ' --> ', line)
            line = re.sub(r'<\|', ' --> ', line)
            
            # Fix incomplete arrows
            line = re.sub(r'--([^>-])', r' --> \1', line)
            
            # Clean up edge label syntax
            line = re.sub(r'\|\s*([^|]*?)\s*\|(?=[A-Z])', r'|"\1"| ', line)
            
            # Simplify complex labels that might cause issues
            # Replace problematic characters in labels
            def fix_label(match):
                node = match.group(1)
                label = match.group(2)
                # Remove or replace problematic characters
                label = label.replace('|', ' or ')
                label = label.replace('>', '')
                label = label.replace('<', '')
                label = label.replace(':', '')
                label = label.replace('&', 'and')
                label = label.replace('/', ' or ')
                return f'{node}[{label}]'
            
            # Fix node labels
            line = re.sub(r'([A-Z][0-9]*)\[([^\]]+)\]', fix_label, line)
            
            # Fix decision node labels
            def fix_decision_label(match):
                node = match.group(1)
                label = match.group(2)
                label = label.replace('|', ' or ')
                label = label.replace('>', '')
                label = label.replace('<', '')
                label = label.replace(':', '')
                label = label.replace('&', 'and')
                label = label.replace('/', ' or ')
                return f'{node}{{{label}}}'
            
            line = re.sub(r'([A-Z][0-9]*)\{([^\}]+)\}', fix_decision_label, line)
            
            # Ensure proper spacing around arrows
            line = re.sub(r'\s*-->\s*', ' --> ', line)
            
            # Only add lines that look like valid Mermaid syntax
            if ('-->' in line or 
                line.startswith(('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K')) or
                'flowchart' in line):
                fixed_lines.append(line)
        
        # Ensure we start with flowchart directive
        if fixed_lines and not any('flowchart' in line for line in fixed_lines[:3]):
            fixed_lines.insert(0, 'flowchart TD')
        
        result = '\n'.join(fixed_lines)
        return result.strip()
        
    except Exception as e:
        print(f"Error validating Mermaid code: {e}")
        return mermaid_code

def extract_mermaid_code(response_text):
    """Extract only the Mermaid code from Groq's response, removing all explanatory text"""
    try:
        import re
        
        # First, try to find all mermaid code blocks in the response
        code_blocks = []
        
        # Pattern 1: Find ```mermaid blocks
        mermaid_pattern = r'```mermaid\s*\n(.*?)\n```'
        matches = re.findall(mermaid_pattern, response_text, re.DOTALL)
        for match in matches:
            clean_code = match.strip()
            if clean_code and 'flowchart' in clean_code:
                code_blocks.append(clean_code)
        
        # Pattern 2: Find standalone flowchart blocks (without ```mermaid wrapper)
        if not code_blocks:
            lines = response_text.split('\n')
            current_block = []
            in_flowchart = False
            
            for line in lines:
                stripped = line.strip()
                
                # Start capturing when we find flowchart
                if not in_flowchart and 'flowchart TD' in stripped:
                    in_flowchart = True
                    current_block = [stripped]
                    continue
                
                # If we're in a flowchart block
                if in_flowchart:
                    # Stop conditions: empty line followed by explanatory text, or obvious explanatory phrases
                    if (not stripped or 
                        any(phrase in stripped.lower() for phrase in [
                            'however', 'this mermaid', 'here is', 'the diagram', 'to better', 
                            'we can use', 'this represents', 'making it easier', 'clearly represents',
                            'more detailed', 'even more detailed', 'version:', 'diagram:'
                        ])):
                        if current_block:
                            code_blocks.append('\n'.join(current_block))
                            current_block = []
                        in_flowchart = False
                        continue
                    
                    # Valid mermaid syntax lines
                    if (stripped and (
                        '-->' in stripped or
                        stripped.startswith(('[', '{')) or
                        '|' in stripped or
                        stripped.endswith((']', '}')) or
                        any(node in stripped for node in ['A[', 'B[', 'C[', 'D[', 'E[', 'F[', 'G[', 'H[', 'I[', 'J[', 'K['])
                    )):
                        current_block.append(stripped)
            
            # Add the last block if it exists
            if current_block and in_flowchart:
                code_blocks.append('\n'.join(current_block))
        
        # Choose the best code block (usually the most detailed one)
        if code_blocks:
            # Prefer the longest block as it's usually the most detailed
            best_block = max(code_blocks, key=len)
            return best_block.strip()
        
        # Fallback: try to extract the first flowchart we find
        lines = response_text.split('\n')
        for i, line in enumerate(lines):
            if 'flowchart TD' in line:
                result_lines = [line.strip()]
                # Take the next lines that look like mermaid syntax
                for j in range(i + 1, len(lines)):
                    next_line = lines[j].strip()
                    if (next_line and (
                        '-->' in next_line or
                        next_line.startswith(('[', '{')) or
                        '|' in next_line or
                        next_line.endswith((']', '}')) or
                        any(node in next_line for node in ['A[', 'B[', 'C[', 'D[', 'E['])
                    )):
                        result_lines.append(next_line)
                    elif not next_line or any(phrase in next_line.lower() for phrase in ['however', 'this', 'here']):
                        break
                
                if len(result_lines) > 1:  # Only return if we have more than just the flowchart line
                    return '\n'.join(result_lines)
        
        # Last resort: return the original text cleaned up
        return response_text.strip()
        
    except Exception as e:
        print(f"Error extracting mermaid code: {e}")
        return response_text.strip()

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
def handler(event, context):
    return app

if __name__ == '__main__':
    # For local development only
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    print(f"🚀 Starting Flask app on port {port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"🔑 Groq API Key configured: {'✅ YES' if GROQ_API_KEY else '❌ NO'}")
    app.run(host='0.0.0.0', port=port, debug=debug)