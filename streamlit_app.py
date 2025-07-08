import streamlit as st
import PyPDF2
import os
import base64
import re
from groq import Groq
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="PDF to Flowchart Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2563eb;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #f0f9ff;
        border-left: 4px solid #2563eb;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        background-color: #fef2f2;
        border-left: 4px solid #ef4444;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Groq client
@st.cache_resource
def init_groq_client():
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        st.error("⚠️ GROQ_API_KEY environment variable not found. Please set it in Streamlit Cloud secrets.")
        return None
    try:
        client = Groq(api_key=api_key)
        return client
    except Exception as e:
        st.error(f"❌ Failed to initialize Groq client: {e}")
        return None

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return None

def call_groq_api(client, prompt, for_mermaid=False):
    """Make API call to Groq API"""
    if not client:
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
        temperature = 0.6
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
        temperature = 0.7
    
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=temperature,
            max_tokens=4000
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Groq API Error: {e}")
        return None

def extract_mermaid_code(response_text):
    """Extract only the Mermaid code from response"""
    lines = response_text.split('\n')
    mermaid_lines = []
    in_flowchart = False
    
    for line in lines:
        stripped = line.strip()
        if 'flowchart TD' in stripped:
            in_flowchart = True
            mermaid_lines = [stripped]
            continue
        
        if in_flowchart:
            if (stripped and (
                '-->' in stripped or
                stripped.startswith(('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K')) or
                any(char in stripped for char in ['[', ']', '{', '}'])
            )):
                mermaid_lines.append(stripped)
            elif not stripped or any(phrase in stripped.lower() for phrase in ['however', 'this', 'here']):
                break
    
    return '\n'.join(mermaid_lines) if mermaid_lines else response_text.strip()

def generate_mermaid_live_url(mermaid_code):
    """Generate Mermaid Live Editor URL"""
    try:
        clean_code = mermaid_code.strip()
        if clean_code.startswith('```mermaid'):
            clean_code = clean_code.replace('```mermaid', '').replace('```', '').strip()
        
        encoded = base64.b64encode(clean_code.encode('utf-8')).decode('utf-8')
        return f"https://mermaid.live/edit#pako:{encoded}"
    except Exception:
        return "https://mermaid.live/"

# Main app
def main():
    # Header
    st.markdown('<h1 class="main-header">📊 PDF to Flowchart Generator</h1>', unsafe_allow_html=True)
    st.markdown('<div class="success-box">🤖 <strong>Powered by Groq AI</strong> - Fast, free, and accurate flowchart generation</div>', unsafe_allow_html=True)
    
    # Initialize Groq client
    client = init_groq_client()
    
    if not client:
        st.stop()
    
    # File upload
    st.subheader("📄 Upload PDF Storyboard")
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload a laboratory storyboard or procedure document in PDF format"
    )
    
    if uploaded_file is not None:
        # Show file details
        st.success(f"✅ File uploaded: {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
        
        # Process button
        if st.button("🚀 Generate Flowchart", type="primary"):
            with st.spinner("🔄 Processing PDF and generating flowchart..."):
                
                # Step 1: Extract text
                st.info("📄 Extracting text from PDF...")
                pdf_text = extract_text_from_pdf(uploaded_file)
                
                if not pdf_text:
                    st.error("❌ Could not extract text from PDF. Please check if the PDF contains readable text.")
                    st.stop()
                
                # Limit text size
                if len(pdf_text) > 6000:
                    pdf_text = pdf_text[:6000] + "..."
                
                st.success(f"✅ Extracted {len(pdf_text)} characters from PDF")
                
                # Step 2: Generate steps
                st.info("🤖 Step 1: Generating procedure steps...")
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
                
                steps_response = call_groq_api(client, step1_prompt)
                if not steps_response:
                    st.error("❌ Failed to generate steps. Please check your API key.")
                    st.stop()
                
                # Step 3: Generate flowchart description
                st.info("🤖 Step 2: Creating flowchart description...")
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
                
                flowchart_response = call_groq_api(client, step2_prompt)
                if not flowchart_response:
                    st.error("❌ Failed to generate flowchart description.")
                    st.stop()
                
                # Step 4: Generate Mermaid code
                st.info("🤖 Step 3: Generating Mermaid code...")
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
                
                mermaid_response = call_groq_api(client, step3_prompt, for_mermaid=True)
                if not mermaid_response:
                    st.error("❌ Failed to generate Mermaid code.")
                    st.stop()
                
                # Clean the Mermaid code
                mermaid_code = extract_mermaid_code(mermaid_response)
                
                # Display results
                st.success("🎉 Flowchart generated successfully!")
                
                # Results tabs
                tab1, tab2, tab3, tab4 = st.tabs(["📋 Steps", "📊 Description", "💻 Mermaid Code", "🔗 Visualize"])
                
                with tab1:
                    st.subheader("Generated Procedure Steps")
                    st.write(steps_response)
                
                with tab2:
                    st.subheader("Flowchart Description")
                    st.write(flowchart_response)
                
                with tab3:
                    st.subheader("Mermaid Code")
                    st.code(mermaid_code, language='text')
                    if st.button("📋 Copy Mermaid Code"):
                        st.write("Code copied to clipboard! (Use Ctrl+A, Ctrl+C to copy manually)")
                
                with tab4:
                    st.subheader("Visualize Flowchart")
                    mermaid_url = generate_mermaid_live_url(mermaid_code)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.link_button(
                            "🌊 Open in Mermaid Live",
                            mermaid_url,
                            help="View and edit the flowchart in Mermaid Live Editor"
                        )
                    
                    with col2:
                        st.link_button(
                            "🎨 Open Draw.io",
                            "https://app.diagrams.net/?splash=0&ui=kennedy&iconfont=1&p=mermaiddiagram",
                            help="Open Draw.io and paste the Mermaid code"
                        )
                    
                    st.info("💡 **Tip**: Click 'Mermaid Live' for instant visualization, or use Draw.io by pasting the Mermaid code above.")

if __name__ == "__main__":
    main()
