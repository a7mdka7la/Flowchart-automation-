# Render Deployment Guide

## Quick Deployment Steps

1. **Connect GitHub Repository to Render:**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub account and select the repository: `https://github.com/a7mdka7la/Flowchart-automation-`

2. **Configure the Service:**
   - Render will automatically detect the `render.yaml` file
   - Service name: `flowchart-automation`
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`
   - Plan: Free

3. **Set Environment Variables:**
   - In the Render dashboard, go to your service → Environment
   - Add the following environment variable:
     - `GROQ_API_KEY`: Your actual Groq API key (keep this secret!)
   - The following are already configured in render.yaml:
     - `PORT`: 5000
     - `FLASK_ENV`: production

4. **Deploy:**
   - Click "Create Web Service"
   - Render will automatically build and deploy your application
   - Your app will be available at: `https://flowchart-automation.onrender.com` (or similar)

## Important Notes

- The deployment is completely free on Render's free tier
- Your GROQ API key is safely stored as an environment variable (not in code)
- The app will automatically restart if it goes to sleep (typical for free tier)
- No manual code changes are needed - everything is configured for deployment

## Troubleshooting

If deployment fails:
1. Check the build logs in Render dashboard
2. Ensure your GROQ_API_KEY environment variable is set
3. Verify the GitHub repository is accessible

## Repository Status

✅ Clean repository (no API keys in code)
✅ Proper environment variable handling
✅ Render configuration ready
✅ All dependencies specified
