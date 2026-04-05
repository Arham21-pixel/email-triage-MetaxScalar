# 📋 Complete HF Spaces Deployment Checklist

## Pre-Deployment (Do on Your Computer)

### Prerequisites
- [ ] Hugging Face account created (https://huggingface.co/join)
- [ ] HF CLI installed (`pip install huggingface-hub`)
- [ ] Git installed and configured
- [ ] HF API token generated (https://huggingface.co/settings/tokens)
- [ ] HF username noted (https://huggingface.co/settings/profile)

### Your Information (Fill This In)
```
HF Username: ___________________________
HF Token: ___________________________
Space Name: email-triage-env
```

### Project Files Verification
- [x] Dockerfile (updated for port 7860)
- [x] requirements.txt (all dependencies listed)
- [x] api/main.py (FastAPI with 7 endpoints)
- [x] env/models.py (Pydantic models)
- [x] env/tasks.py (30 email tasks)
- [x] env/graders.py (scoring system)
- [x] env/environment.py (OpenEnv-compatible)
- [x] inference.py (async LLM inference)
- [x] openenv.yaml (benchmark configuration)
- [x] README.md (documentation)
- [x] .gitignore (clean commits)

---

## Step 1: Create HF Space (Web UI)

**⏱ Time: 2 minutes**

### Option A: Web UI (Easiest)
1. [ ] Go to https://huggingface.co/spaces
2. [ ] Click **"Create new Space"**
3. [ ] Fill in:
   - **Space name**: `email-triage-env`
   - **License**: MIT (or your choice)
   - **Space SDK**: Docker
   - **Visibility**: Public
4. [ ] Click **"Create Space"**
5. [ ] Copy the Space URL

### Option B: CLI
```bash
huggingface-cli login
huggingface-cli repo create --type space --space-sdk docker email-triage-env
```

---

## Step 2: Clone Space Repository

**⏱ Time: 1 minute**

### Execute
```bash
# Replace YOUR_USERNAME
git clone https://huggingface.co/spaces/YOUR_USERNAME/email-triage-env
cd email-triage-env
```

### Verify
```bash
# You should see .gitattributes file
ls -la
```

- [ ] Directory created
- [ ] .gitattributes present
- [ ] Inside correct directory

---

## Step 3: Copy Your Project Files

**⏱ Time: 2 minutes**

Copy these files to your cloned directory:

### Directories
- [ ] Copy `env/` → `email-triage-env/env/`
- [ ] Copy `api/` → `email-triage-env/api/`

### Files
- [ ] Copy `inference.py`
- [ ] Copy `Dockerfile`
- [ ] Copy `requirements.txt`
- [ ] Copy `openenv.yaml`
- [ ] Copy `README.md`
- [ ] Copy `.gitignore`

### Verify Structure
```bash
ls -la
# Should show:
# env/
# api/
# Dockerfile
# requirements.txt
# openenv.yaml
# README.md
# .gitignore
# .gitattributes
```

- [ ] All files copied
- [ ] Directory structure correct

---

## Step 4: Git Commands (Push to HF)

**⏱ Time: 2 minutes**

### Initialize Git (if needed)
```bash
git init
```

### Add Files
```bash
git add .
```

- [ ] Files staged

### Commit
```bash
git commit -m "Initial deployment: Email Triage OpenEnv"
```

### Add Remote (Replace YOUR_USERNAME)
```bash
git remote add origin https://huggingface.co/spaces/YOUR_USERNAME/email-triage-env
```

### Push (You'll be prompted for HF credentials)
```bash
git push -u origin main
```

- [ ] Files pushed to HF

### Verify
```bash
git log --oneline -3
# Should show your commit
```

---

## Step 5: Monitor Build

**⏱ Time: 5-10 minutes**

### Go to Your Space
```
https://huggingface.co/spaces/YOUR_USERNAME/email-triage-env
```

### Check Status
- [ ] Status shows 🟡 **Building** (doesn't stay long)
- [ ] Status shows 🟡 **Running** (container starting)
- [ ] Status shows 🟢 **Running** (ready!)

### View Logs
- [ ] Click **"View logs"** button
- [ ] See Docker build progress
- [ ] Look for errors if build fails

### Expected Log Lines
```
Step 1/10 : FROM python:3.11-slim
Step 2/10 : LABEL maintainer="Email Triage Meta Hackathon"
...
Successfully built [hash]
Application startup complete
```

- [ ] Build successful
- [ ] Container started
- [ ] No errors in logs

---

## Step 6: Set Environment Variables

**⏱ Time: 2 minutes**

### Go to Settings
1. [ ] Click **Settings** gear icon (top-right of Space page)
2. [ ] Scroll to **Environment variables** section
3. [ ] You should see an "Add variable" button

### Add Variables

#### Variable 1: API_BASE_URL
- [ ] Name: `API_BASE_URL`
- [ ] Value: `https://router.huggingface.co/v1`
- [ ] Click **Save**

#### Variable 2: MODEL_NAME
- [ ] Name: `MODEL_NAME`
- [ ] Value: `Qwen/Qwen2.5-72B-Instruct`
- [ ] Click **Save**

#### Variable 3: HF_TOKEN
- [ ] Name: `HF_TOKEN`
- [ ] Value: (Your HF token from https://huggingface.co/settings/tokens)
- [ ] Click **Save**

#### Variable 4: OPENAI_API_KEY (Optional)
- [ ] Name: `OPENAI_API_KEY`
- [ ] Value: (Only if using OpenAI)
- [ ] Click **Save**

### Verify
- [ ] All variables show in Settings
- [ ] Space restarted after variable changes
- [ ] 🟢 Status back to Running

---

## Step 7: Test Your Deployment

**⏱ Time: 2 minutes**

### Replace This First
```powershell
$SPACE_URL = "https://YOUR_USERNAME-email-triage-env.hf.space"
```

### Test 1: Health Check
```bash
curl $SPACE_URL/healthz
```

- [ ] Returns: `{"status":"ok","environment":"email-triage-env"}`

### Test 2: Documentation
- [ ] Visit: `$SPACE_URL/docs`
- [ ] See Swagger UI
- [ ] All endpoints listed

### Test 3: Reset Environment
```bash
curl -X POST $SPACE_URL/reset
```

- [ ] Returns first email with ID "email_01"
- [ ] Status shows "reset"

### Test 4: Get State
```bash
curl $SPACE_URL/state
```

- [ ] Returns current environment state
- [ ] step_count: 0
- [ ] done: false

### Test 5: Submit Action
```bash
curl -X POST $SPACE_URL/step `
  -H "Content-Type: application/json" `
  -d '{
    "email_id": "email_01",
    "priority": "urgent",
    "category": "billing",
    "reply": "Thank you for notification"
  }'
```

- [ ] Returns reward (should be 1.0 for correct answer)
- [ ] Returns next email (email_02)
- [ ] done: false

---

## Step 8: Add OpenEnv Tag

**⏱ Time: 1 minute**

1. [ ] Go to Space Settings
2. [ ] Scroll to **Tags** section
3. [ ] Add these tags:
   - [ ] `openenv`
   - [ ] `email`
   - [ ] `classification`
   - [ ] `benchmark`
   - [ ] `nlp`
4. [ ] Save

---

## Final Verification

### Space Live Check
- [ ] Space status: 🟢 Running
- [ ] URL accessible: https://huggingface.co/spaces/{username}/email-triage-env
- [ ] API URL accessible: https://{username}-email-triage-env.hf.space

### Endpoints Working
- [ ] GET /healthz → 200 OK
- [ ] GET /docs → Swagger UI loads
- [ ] POST /reset → Returns email
- [ ] GET /state → Returns state
- [ ] POST /step → Processes action

### Environment Variables
- [ ] API_BASE_URL set
- [ ] MODEL_NAME set
- [ ] HF_TOKEN set
- [ ] All in Space Settings

### Repository
- [ ] All files pushed to HF
- [ ] .git history maintained
- [ ] Dockerfile for port 7860
- [ ] requirements.txt complete

---

## Share Your Space

### Your URLs
```
Space Page:  https://huggingface.co/spaces/{YOUR_USERNAME}/email-triage-env
API Base:    https://{YOUR_USERNAME}-email-triage-env.hf.space
Docs:        https://{YOUR_USERNAME}-email-triage-env.hf.space/docs
```

### Share With
- [ ] Send Space URL to teammates
- [ ] Add to project portfolio
- [ ] Submit to OpenEnv leaderboard
- [ ] Post in HF discussions

---

## Troubleshooting

### If Build Fails
1. [ ] Click "View logs"
2. [ ] Look for error message
3. [ ] Common causes:
   - Port not 7860 (fix Dockerfile)
   - Missing __init__.py (create in env/ and api/)
   - Dependency missing (add to requirements.txt)
4. [ ] Fix locally
5. [ ] Push again: `git add . && git commit -m "fix" && git push`

### If Tests Fail
1. [ ] Check Space is 🟢 Running
2. [ ] Check environment variables are set
3. [ ] Click "View logs" for runtime errors
4. [ ] Fix code locally
5. [ ] Push again

### If Environment Variables Don't Work
1. [ ] Verify names exactly match:
   - `API_BASE_URL` (not `api_base_url`)
   - `MODEL_NAME` (not `model_name`)
   - `HF_TOKEN` (not `hf_token`)
2. [ ] Click **Save** for each variable
3. [ ] Wait 30 seconds for Space to restart
4. [ ] Verify in Space Settings they're still there

---

## Success Criteria

You've successfully deployed when:

✅ Space created and visible on HF  
✅ All files pushed to repository  
✅ Dockerfile updated for port 7860  
✅ Space built successfully (🟢 Running)  
✅ Health check returns 200 OK  
✅ /docs loads Swagger UI  
✅ /reset returns first email  
✅ /state returns environment state  
✅ /step processes actions correctly  
✅ Environment variables set  
✅ OpenEnv tag added  
✅ Space URL working and accessible  

---

## Total Time Estimate

| Step | Time |
|------|------|
| Create Space | 2 min |
| Clone & Copy Files | 3 min |
| Git Commands | 2 min |
| Monitor Build | 5-10 min |
| Set Variables | 2 min |
| Test Endpoints | 2 min |
| Add Tags | 1 min |
| **Total** | **17-25 min** |

---

## Document References

- **DEPLOYMENT_SUMMARY.md** — Overview and next steps
- **DEPLOYMENT_HF_SPACES.md** — Full 10-step guide with details
- **QUICK_GIT_REFERENCE.md** — Git commands copy-paste ready
- **.gitignore** — Clean deployments

---

## You're All Set! 🚀

Your Email Triage OpenEnv project is ready to deploy to Hugging Face Spaces.

**Next action**: Start with Step 1 above!

Questions? Refer to DEPLOYMENT_HF_SPACES.md or contact HF support.
