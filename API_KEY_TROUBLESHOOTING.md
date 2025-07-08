# API Key Troubleshooting Guide

## Error: ASCII Encoding Issue with Groq API Key

If you're seeing an error like `'ascii' codec can't encode character '\u0417'`, this means your API key contains non-ASCII characters (like Cyrillic letters), which shouldn't happen with a valid Groq API key.

### Step 1: Check Your API Key

1. **Go to your Streamlit Cloud app**
2. **Click the debug section**: "🔧 Debug API Key (Click if you have encoding errors)"
3. **Click "Debug API Key"** to see detailed information about your key

### Step 2: Fix the API Key

#### Option A: Re-copy the API Key
1. Go to [Groq Console](https://console.groq.com/keys)
2. **Create a new API key** (don't reuse the old one)
3. **Carefully copy the new key** (make sure no extra characters are included)
4. **Update it in Streamlit Cloud secrets**

#### Option B: Manual Check
1. **Groq API keys should:**
   - Start with `gsk_`
   - Only contain letters (a-z, A-Z), numbers (0-9), underscores (_), and dashes (-)
   - Be exactly 56 characters long
   - Look like: `gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

2. **If your key has:**
   - Cyrillic characters (З, П, А, etc.)
   - Special Unicode characters
   - Extra spaces or line breaks
   - **Then it's corrupted and needs to be replaced**

### Step 3: Update in Streamlit Cloud

1. Go to your Streamlit Cloud app settings
2. Navigate to **Secrets**
3. Update the `GROQ_API_KEY` with the clean, new key
4. **Save** and wait for the app to redeploy

### Step 4: Verify

After updating:
1. The app should now initialize without encoding errors
2. You should see "✅ Groq API key is valid and working!"
3. You can upload PDFs and generate flowcharts

### Prevention

- Always copy API keys directly from the official console
- Avoid copying from text editors that might add Unicode formatting
- Don't copy from PDFs or images (use text sources only)
- Test immediately after setting up

### Still Having Issues?

If the problem persists:
1. Try creating a completely new Groq account
2. Generate a fresh API key
3. Use a plain text editor (like Notepad) to verify the key format
4. Contact Groq support if the key format is still incorrect

---

**Note**: This issue is specific to corrupted API keys and not a problem with the application code itself.
