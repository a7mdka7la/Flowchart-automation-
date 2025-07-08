# 🚀 Render Deployment Guide - Free Web Deployment

Your Flask PDF-to-Flowchart app is **100% ready** for Render deployment! This guide will get you live on the web in 5 minutes.

## ✅ Pre-Deployment Checklist

Your project is already configured with:
- ✅ Clean code (no API keys in repository)
- ✅ Environment variable handling for `GROQ_API_KEY`
- ✅ `render.yaml` configuration file
- ✅ `requirements.txt` with all dependencies
- ✅ `Dockerfile` for containerized builds
- ✅ Production-ready Flask app (`app.py`)

## 🎯 Step-by-Step Deployment

### Step 1: Open Render Dashboard
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Sign up or log in with your GitHub account

### Step 2: Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub account (if not already connected)
3. Select repository: `a7mdka7la/Flowchart-automation-`
4. Click **"Connect"**

### Step 3: Configure Service (Auto-Detected)
Render will automatically detect your `render.yaml` file. Verify these settings:
- **Service Name**: `flowchart-automation`
- **Environment**: `Python 3`
- **Plan**: **Free** (perfect for this project)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python app.py`

### Step 4: Set Environment Variable (CRITICAL!)
1. In the service configuration, scroll to **"Environment Variables"**
2. Add this variable:
   - **Key**: `GROQ_API_KEY`
   - **Value**: Your actual Groq API key (get it from [console.groq.com](https://console.groq.com))

> 🔐 **Important**: Never put your API key in the code. Render stores it securely as an environment variable.

### Step 5: Deploy
1. Click **"Create Web Service"**
2. Render will:
   - Clone your repository
   - Install dependencies from `requirements.txt`
   - Build and start your application
   - Provide you with a live URL (e.g., `https://flowchart-automation.onrender.com`)

## 🌐 Your Live App URL

After deployment, your app will be available at:
```
https://flowchart-automation-[random].onrender.com
```

## 📋 What Your App Does

- **Upload PDF storyboards** → Extract text using PyPDF2
- **AI Processing** → Groq API (free, fast AI) analyzes content
- **Generate Steps** → Extract laboratory procedures
- **Create Flowcharts** → Generate Mermaid code
- **Visualize** → Open in Mermaid Live or Draw.io

## 🔧 Troubleshooting

### If Build Fails:
1. Check **"Logs"** tab in Render dashboard
2. Common issues:
   - Missing `GROQ_API_KEY` environment variable
   - Invalid Groq API key
   - Python dependency conflicts (unlikely with current setup)

### If App Doesn't Start:
1. Check **"Events"** tab for errors
2. Verify `GROQ_API_KEY` is set correctly
3. Test API key at [console.groq.com](https://console.groq.com)

### If App Works But AI Fails:
1. Check Groq API quota at [console.groq.com](https://console.groq.com)
2. Groq offers free tier with generous limits

## 🚀 Free Hosting Benefits

- **✅ Free Forever**: Render's free tier is permanent
- **✅ Auto-Sleep**: App sleeps after 15 min of inactivity (saves resources)
- **✅ Auto-Wake**: Wakes up on first request (may take 30 seconds)
- **✅ HTTPS**: Automatic SSL certificate
- **✅ Custom Domain**: Can add your own domain later

## 🔄 Updates & Redeployment

To update your app:
1. Make changes to your code
2. Push to GitHub: `git push origin main`
3. Render automatically redeploys (takes 2-3 minutes)

## 🎉 You're Ready!

Your project is **100% deployment-ready**. Just follow the steps above and you'll have a live web app in minutes!

**Next**: Visit [Render Dashboard](https://dashboard.render.com/) and click "New +" → "Web Service" to start!
