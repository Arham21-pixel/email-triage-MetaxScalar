# Quick Git Commands for HF Spaces Deployment

## Replace These Variables First

```powershell
# Set your values here
$HF_USERNAME = "your-actual-username"  # Get from https://huggingface.co/settings/profile
$SPACE_NAME = "email-triage-env"
$HF_TOKEN = "hf_xxxxxxxxxxxxx"  # Get from https://huggingface.co/settings/tokens
```

---

## One-Time Setup (Do Once)

### Step 1: Login to HuggingFace
```bash
huggingface-cli login
# Paste your HF_TOKEN when prompted
```

### Step 2: Create Space (Web UI or CLI)

**Option A - CLI:**
```bash
huggingface-cli repo create --type space --space-sdk docker email-triage-env
```

**Option B - Web UI:**
Visit https://huggingface.co/spaces and click "Create new Space"

---

## Deployment Flow (Copy & Paste)

### Step 1: Clone Your Space
```bash
# Navigate to a directory where you want the Space repo
cd ~\Documents

# Clone the Space
git clone https://huggingface.co/spaces/{YOUR_HF_USERNAME}/email-triage-env
cd email-triage-env
```

**Example:**
```bash
git clone https://huggingface.co/spaces/john-doe/email-triage-env
cd email-triage-env
```

---

### Step 2: Copy Your Project Files
Copy all these to the cloned directory:
- `env/` (entire folder)
- `api/` (entire folder)
- `inference.py`
- `Dockerfile`
- `requirements.txt`
- `openenv.yaml`
- `README.md`

---

### Step 3: Push to HF Spaces

```bash
# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial deployment: Email Triage OpenEnv with Docker"

# Add remote (replace YOUR_HF_USERNAME)
git remote add origin https://huggingface.co/spaces/YOUR_HF_USERNAME/email-triage-env

# Push
git push -u origin main
```

**Full example for username `john-doe`:**
```bash
git init
git add .
git commit -m "Initial deployment: Email Triage OpenEnv with Docker"
git remote add origin https://huggingface.co/spaces/john-doe/email-triage-env
git push -u origin main
```

---

## Updating Your Space (After Initial Push)

### If you make changes locally:

```bash
git add .
git commit -m "Update: [describe changes]"
git push
```

**Examples:**
```bash
# Fixed a bug
git add . && git commit -m "Fix: email parsing error" && git push

# Updated requirements
git add requirements.txt && git commit -m "Update dependencies" && git push

# Added new endpoint
git add api/main.py && git commit -m "Add new /metrics endpoint" && git push
```

---

## Verify Push Success

```bash
# List all committed files
git ls-files

# Check remote URL
git remote -v

# Check last commits
git log --oneline -5
```

**Expected output for `git remote -v`:**
```
origin  https://huggingface.co/spaces/{username}/email-triage-env (fetch)
origin  https://huggingface.co/spaces/{username}/email-triage-env (push)
```

---

## After Push: What Happens Next

1. HuggingFace detects Dockerfile
2. Builds Docker image (takes 3-5 minutes)
3. Deploys container to Space
4. Space becomes live at: `https://huggingface.co/spaces/{username}/email-triage-env`

### Monitor Build:
1. Go to your Space URL
2. Click **View logs** to see real-time build output

### Check Status:
- 🟡 Building/Running = Still deploying
- 🟢 Running = Ready to use
- 🔴 Error = Something failed (check logs)

---

## Set Environment Variables

After deployment, go to Space Settings:

```
https://huggingface.co/spaces/{username}/email-triage-env/settings
```

Add these variables:
- `API_BASE_URL` = `https://router.huggingface.co/v1`
- `MODEL_NAME` = `Qwen/Qwen2.5-72B-Instruct`
- `HF_TOKEN` = Your HF token from https://huggingface.co/settings/tokens

Click **Save** after each one.

---

## Test Your Deployment

Once Space is 🟢 Running:

```bash
$SPACE_URL = "https://{username}-email-triage-env.hf.space"

# Test 1: Health check
curl $SPACE_URL/healthz

# Test 2: Open docs
# Visit: $SPACE_URL/docs

# Test 3: Reset
curl -X POST $SPACE_URL/reset

# Test 4: Get state
curl $SPACE_URL/state

# Test 5: Submit action
curl -X POST $SPACE_URL/step `
  -H "Content-Type: application/json" `
  -d '{"email_id":"email_01","priority":"urgent","category":"billing"}'
```

---

## Common Git Errors & Fixes

### Error: "fatal: not a git repository"
```bash
# Solution: Initialize git
git init
git add .
git commit -m "Initial commit"
git remote add origin https://huggingface.co/spaces/YOUR_USERNAME/email-triage-env
git push -u origin main
```

### Error: "fatal: 'origin' does not appear to be..."
```bash
# Solution: Check remote
git remote -v

# If missing, add it:
git remote add origin https://huggingface.co/spaces/YOUR_USERNAME/email-triage-env
git push -u origin main
```

### Error: "Everything up-to-date"
```bash
# Your changes are already pushed. To update:
# 1. Make a change to a file
# 2. Run: git add . && git commit -m "message" && git push
```

### Error: Authentication failed
```bash
# Solution: Login again
huggingface-cli login
# Then retry your git push
```

---

## Your Space URL Template

Once deployed, replace `{username}`:

```
https://huggingface.co/spaces/{username}/email-triage-env

Examples:
https://huggingface.co/spaces/john-doe/email-triage-env
https://huggingface.co/spaces/alice-smith/email-triage-env
https://huggingface.co/spaces/your-team/email-triage-env
```

---

## Quick Checklist

- [ ] HF account created
- [ ] HF API token generated
- [ ] HF CLI installed: `pip install huggingface-hub`
- [ ] Space created on HF
- [ ] Cloned Space locally
- [ ] Copied all project files
- [ ] Ran git commands (init, add, commit, remote, push)
- [ ] Space is building (check logs)
- [ ] Space is 🟢 Running
- [ ] Environment variables set
- [ ] Endpoints tested and working

---

## Need Help?

- **Build fails?** Click "View logs" on Space page
- **Environment variables not working?** Make sure you click **Save** in Settings
- **API not responding?** Check Space is 🟢 Running, not 🔴 Error
- **Port issues?** Verify Dockerfile uses port 7860
- **Git connection issues?** Run `huggingface-cli login` again
