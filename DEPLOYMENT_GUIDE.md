# Toyota Financial Services - Railway Deployment Guide

## 🚀 Complete Deployment Steps for Railway

### Prerequisites

- GitHub account
- Railway account (free tier available)
- Google Gemini API key

---

## Step 1: Prepare Your Repository

### 1.1 Push to GitHub

```bash
# Initialize git if not already done
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial commit: Toyota Financial Services app"

# Create GitHub repository and push
git remote add origin https://github.com/YOUR_USERNAME/toyota-financial-services.git
git branch -M main
git push -u origin main
```

### 1.2 Verify Files

Ensure these files are in your repository:

- ✅ `Dockerfile`
- ✅ `.dockerignore`
- ✅ `railway.toml`
- ✅ `requirements.txt`
- ✅ `run.py`
- ✅ `src/app.py`
- ✅ `src/chatbot_service.py`
- ✅ `src/templates/` (all HTML files)
- ✅ `data/` (CSV files)

---

## Step 2: Deploy to Railway

### 2.1 Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Connect your GitHub account

### 2.2 Deploy from GitHub

1. **Click "New Project"**
2. **Select "Deploy from GitHub repo"**
3. **Choose your repository**: `toyota-financial-services`
4. **Railway will automatically detect the Dockerfile**

### 2.3 Configure Environment Variables

In Railway dashboard, go to **Variables** tab and add:

```bash
# Required: Google Gemini API Key
GEMINI_API_KEY=your_actual_gemini_api_key_here

# Optional: Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
```

### 2.4 Deploy

1. **Click "Deploy"**
2. **Wait for build to complete** (2-3 minutes)
3. **Railway will provide a URL** like: `https://toyota-financial-services-production.up.railway.app`

---

## Step 3: Test Your Deployment

### 3.1 Basic Health Check

Visit your Railway URL:

```
https://your-app-name.up.railway.app
```

### 3.2 Test Key Features

1. **Home Page**: Should load with navbar and vehicle listings
2. **AI Chatbot**: Visit `/chatbot` and test the conversation flow
3. **API Endpoints**: Test `/api/chatbot/start`

### 3.3 Test Chatbot Functionality

```bash
# Test chatbot API
curl -X POST https://your-app-name.up.railway.app/api/chatbot/start \
  -H "Content-Type: application/json"
```

---

## Step 4: Custom Domain (Optional)

### 4.1 Add Custom Domain

1. **Go to Railway Dashboard**
2. **Click on your project**
3. **Go to Settings → Domains**
4. **Add your custom domain**
5. **Update DNS records** as instructed

---

## Step 5: Monitoring & Maintenance

### 5.1 Monitor Logs

- **Railway Dashboard → Deployments → View Logs**
- **Monitor for errors and performance**

### 5.2 Environment Variables Management

- **Add/Update variables** in Railway dashboard
- **Restart deployment** after changing variables

### 5.3 Updates

```bash
# Make changes to your code
git add .
git commit -m "Update: Add new feature"
git push origin main

# Railway will automatically redeploy
```

---

## 🔧 Troubleshooting

### Common Issues:

#### 1. Build Failures

```bash
# Check Dockerfile syntax
docker build -t test-app .

# Test locally
docker run -p 5002:5002 test-app
```

#### 2. Environment Variables

- **Verify GEMINI_API_KEY is set**
- **Check variable names match exactly**
- **Restart deployment after adding variables**

#### 3. Port Issues

- **Railway automatically sets PORT environment variable**
- **App listens on 0.0.0.0:PORT**

#### 4. Static Files

- **Ensure all templates are in src/templates/**
- **Check file paths in app.py**

---

## 📊 Performance Optimization

### Production Settings:

```python
# In app.py - already configured
debug = os.environ.get('FLASK_ENV') == 'development'
port = int(os.environ.get('PORT', 5002))
```

### Railway Configuration:

```toml
# railway.toml - already created
[build]
builder = "dockerfile"

[deploy]
startCommand = "python run.py"
healthcheckPath = "/"
healthcheckTimeout = 300
restartPolicyType = "always"
```

---

## 🎯 Final Checklist

Before going live:

- [ ] **GitHub repository** is public/accessible
- [ ] **GEMINI_API_KEY** is set in Railway
- [ ] **All templates** are included
- [ ] **CSV data files** are present
- [ ] **Dockerfile** builds successfully
- [ ] **Health check** passes
- [ ] **Chatbot API** responds correctly
- [ ] **All pages** load without errors
- [ ] **Navbar** works on all pages
- [ ] **Validation** works in chatbot

---

## 🚀 Your App is Live!

Once deployed, your Toyota Financial Services application will be available at:

```
https://your-app-name.up.railway.app
```

**Key Features Available:**

- ✅ AI Financial Advisor Chatbot
- ✅ Vehicle Database & Browsing
- ✅ Personalized Financing Recommendations
- ✅ Interactive Survey & Validation
- ✅ Responsive Design
- ✅ Professional UI/UX

**Railway Benefits:**

- ✅ **Free tier** available
- ✅ **Automatic deployments** from GitHub
- ✅ **Custom domains** supported
- ✅ **Environment variables** management
- ✅ **Built-in monitoring**
- ✅ **Easy scaling**

---

## 📞 Support

If you encounter issues:

1. **Check Railway logs** for error messages
2. **Verify environment variables** are set correctly
3. **Test locally** with Docker first
4. **Check GitHub repository** has all files

Your Toyota Financial Services application is now ready for production! 🎉
