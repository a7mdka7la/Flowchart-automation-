# Storyboard to Flowchart Generator

A simple web application that uploads PDF storyboards and automatically generates flowcharts using Grok AI.

## Features

- Upload PDF storyboard files
- Automatically extract text from PDFs
- Generate process steps using Grok AI
- Create flowchart descriptions
- Generate Mermaid code for flowcharts
- Open flowcharts directly in Draw.io

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and go to `http://localhost:5000`

## Usage

1. Click "Choose PDF Storyboard File" and select your PDF storyboard
2. Click "Generate Flowchart" 
3. Wait for the AI to process your storyboard (this may take a few moments)
4. View the generated steps, flowchart description, and Mermaid code
5. Click "Open Flowchart in Draw.io" to view the final flowchart

## How it works

1. Extracts text from the uploaded PDF storyboard
2. Sends the text to Grok AI with the prompt: "For the provided storyboard generate steps to follow"
3. Takes the generated steps and asks Grok AI: "Please create a flowchart representing the process, incorporating the above steps. Ensure that related steps are placed side by side."
4. Finally asks Grok AI: "Give me the mermaid code for this"
5. Opens the generated Mermaid code in Draw.io for visualization

## Requirements

- Python 3.7+
- Grok AI API key (already configured)
- Internet connection for API calls
- **Credits in your x.ai account** (visit https://console.x.ai to add credits)

## Note

The application will automatically fall back to demo mode if your Grok AI account doesn't have credits. To use the live Grok AI integration, please add credits to your x.ai account at https://console.x.ai.
