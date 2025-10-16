# Deployment Guide - Fakemon Card Simulator

## Overview
- **Backend**: Render (FastAPI + PyTorch)
- **Frontend**: Vercel (Static HTML/CSS/JS)

---

## Part 1: Deploy Backend to Render

### Step 1: Push Your Code to GitHub

First, make sure all changes are committed and pushed:

```bash
git add .
git commit -m "Add deployment configuration for Render and Vercel"
git push origin main
```

### Step 2: Create Render Account & Deploy

1. Go to [https://render.com](https://render.com)
2. Click "Get Started for Free" (or "Sign In" if you have an account)
3. Sign up with GitHub
4. After logging in, click "New +" → "Web Service"
5. Connect your GitHub repository: `fakemon-card-simulator`
6. Configure the service:
   - **Name**: `fakemon-backend` (or any name you like)
   - **Region**: Choose closest to you (e.g., Oregon/Ohio)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Docker`
   - **Instance Type**: `Free`
7. Click "Create Web Service"

### Step 3: Wait for Build

- Render will build your Docker container (this takes 5-10 minutes)
- Watch the logs in the Render dashboard
- Once you see "Generator loaded!" and "Application startup complete", it's ready!

### Step 4: Get Your Backend URL

- In Render dashboard, you'll see your service URL (e.g., `https://fakemon-backend-xxxx.onrender.com`)
- **COPY THIS URL** - you'll need it for the frontend!
- Test it by visiting: `https://your-backend-url.onrender.com/` (should show `{"status":"online"}`)

---

## Part 2: Update Frontend Configuration

### Step 1: Update API URL in Frontend

Open `js/generate.js` and replace line 1:

**Change from:**
```javascript
const API_URL = 'http://localhost:8000';
```

**Change to:**
```javascript
const API_URL = 'https://YOUR-RENDER-URL.onrender.com';
```

(Replace `YOUR-RENDER-URL` with your actual Render backend URL)

### Step 2: Commit the Change

```bash
git add js/generate.js
git commit -m "Update API URL to production backend"
git push origin main
```

---

## Part 3: Deploy Frontend to Vercel

### Step 1: Deploy to Vercel

From your project root directory:

```bash
vercel --prod
```

### Step 2: Follow Prompts

- Should auto-detect your existing project configuration
- Press Enter to confirm deployment
- Wait for deployment to complete (~30 seconds)

### Step 3: Get Your Frontend URL

- Vercel will provide a URL like: `https://fakemon-card-simulator.vercel.app`
- **COPY THIS URL**

---

## Part 4: Update Backend CORS (Optional but Recommended)

### Step 1: Add Environment Variable in Render

1. Go to Render dashboard → Your service
2. Click "Environment" in left sidebar
3. Add new environment variable:
   - **Key**: `FRONTEND_URL`
   - **Value**: `https://your-vercel-url.vercel.app`
4. Click "Save Changes"
5. Service will automatically redeploy (takes ~2-3 minutes)

---

## Part 5: Test Your Deployed App!

1. Visit your Vercel URL: `https://your-app.vercel.app`
2. Navigate to "Generate" page
3. Click "Generate Card"
4. Wait ~10-20 seconds (first request might be slow due to cold start)
5. You should see a generated Pokemon card!

---

## Troubleshooting

### Backend Issues

**Problem**: "Generator loaded!" not appearing in Render logs
- **Solution**: Check that `backend/checkpoints/gan_checkpoint.pth` exists in your repo

**Problem**: 500 error when generating cards
- **Solution**: Check Render logs for error messages. Most likely OOM (out of memory) - free tier has 512MB RAM

**Problem**: Very slow first request (30+ seconds)
- **Solution**: This is normal! Render free tier has cold starts. Subsequent requests will be faster.

### Frontend Issues

**Problem**: "Failed to generate card" error
- **Solution**: Check that API_URL in `js/generate.js` matches your Render URL exactly (with https://)

**Problem**: CORS error in browser console
- **Solution**: Add your Vercel URL to `FRONTEND_URL` environment variable in Render

### General Tips

- Render free tier spins down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds (cold start)
- Keep the backend "warm" by pinging it every 10 minutes (optional)

---

## URLs to Save

- **Frontend (Vercel)**: https://______________________.vercel.app
- **Backend (Render)**: https://______________________.onrender.com
- **GitHub Repo**: https://github.com/OliverGrabner/fakemon-card-simulator

---

## Updating Your App

When you make changes:

```bash
# Make your changes, then:
git add .
git commit -m "Description of changes"
git push origin main

# Both Render and Vercel will auto-deploy on push!
```

No need to manually redeploy - both platforms auto-deploy when you push to GitHub!
