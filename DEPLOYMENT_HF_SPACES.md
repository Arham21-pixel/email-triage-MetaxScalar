# Complete Guide: Deploy Email Triage OpenEnv to Hugging Face Spaces

## Prerequisites

Before starting, you need:

1. **Hugging Face Account** — Create one at https://huggingface.co/join
2. **HF CLI installed** — Run: `pip install huggingface-hub`
3. **HF API Token** — Get it from https://huggingface.co/settings/tokens (create a new token with write access)
4. **Git installed** — For version control
5. **Your HF username** — Available at https://huggingface.co/settings/profile
6. **HF_TOKEN environment variable** — Your HuggingFace API token for inference

---

## STEP 1: Create a New Hugging Face Space with Docker

### Method A: Using CLI (Recommended)

```bash
# Set your HF username
$HF_USERNAME = "your-username"
$SPACE_NAME = "email-triage-env"

# Login to HuggingFace
huggingface-cli login

# Create a new Space repository (Docker)
huggingface-cli repo create \
  --type space \
  --space-sdk docker \
  $SPACE_NAME
```

### Method B: Web UI

1. Go to https://huggingface.co/spaces
2. Click **"Create new Space"**
3. Fill in:
   - **Space name**: `email-triage-env`
   - **License**: `MIT` (or your choice)
   - **Space SDK**: `Docker`
   - **Visibility**: `Public` (or `Private` if preferred)
4. Click **"Create Space"**

### Expected Output
```
✅ Space created: https://huggingface.co/spaces/{username}/email-triage-env
```

---

## STEP 2: Clone Your New Space Locally

```bash
# Set variables
$HF_USERNAME = "your-username"
$SPACE_NAME = "email-triage-env"

# Clone the Space repository
git clone https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME
cd $SPACE_NAME
```

**Expected output**: Empty directory with just `.gitattributes`

---

## STEP 3: Copy All Your Project Files

```bash
# From your project root directory, copy everything to the cloned Space

# Copy the env/ directory
Copy-Item -Path "env\*" -Destination "$SPACE_NAME\env\" -Recurse

# Copy the api/ directory
Copy-Item -Path "api\*" -Destination "$SPACE_NAME\api\" -Recurse

# Copy individual files
Copy-Item "inference.py" "$SPACE_NAME\"
Copy-Item "Dockerfile" "$SPACE_NAME\"
Copy-Item "requirements.txt" "$SPACE_NAME\"
Copy-Item "openenv.yaml" "$SPACE_NAME\"
Copy-Item "README.md" "$SPACE_NAME\"
```

Or manually copy all files:
- `env/` (entire directory)
- `api/` (entire directory)
- `inference.py`
- `Dockerfile`
- `requirements.txt`
- `openenv.yaml`
- `README.md`

---

## STEP 4: Verify Dockerfile for HF Spaces

**CRITICAL**: Your Dockerfile MUST expose port 7860 for HF Spaces.

Current Dockerfile has been updated with:
```dockerfile
EXPOSE 7860
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:7860/healthz || exit 1
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

✅ Verified and correct!

---

## STEP 5: Push to Hugging Face Spaces

Navigate to your Space directory and run these exact git commands:

```bash
cd email-triage-env

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial deployment: Email Triage OpenEnv with Docker"

# Add HF remote
git remote add origin https://huggingface.co/spaces/{YOUR_HF_USERNAME}/email-triage-env

# Push to HF (you'll be prompted for credentials)
git push -u origin main
```

Replace `{YOUR_HF_USERNAME}` with your actual HuggingFace username.

**Example for username `john-doe`:**
```bash
git remote add origin https://huggingface.co/spaces/john-doe/email-triage-env
git push -u origin main
```

**What happens next:**
- HF detects the Dockerfile
- Builds the Docker image (takes 3-5 minutes)
- Deploys the container
- Your Space goes live at: `https://huggingface.co/spaces/{username}/email-triage-env`

---

## STEP 6: Set Environment Variables in Space Settings

**⚠️ CRITICAL**: HF Spaces reads environment variables from the Space Settings page.

1. Go to your Space: `https://huggingface.co/spaces/{username}/email-triage-env`
2. Click **Settings** (gear icon, top-right)
3. Scroll to **Environment variables** section
4. Add these variables:

| Variable | Value | Example |
|----------|-------|---------|
| `API_BASE_URL` | Your LLM API endpoint | `https://router.huggingface.co/v1` |
| `MODEL_NAME` | LLM model identifier | `Qwen/Qwen2.5-72B-Instruct` |
| `HF_TOKEN` | Your HuggingFace API token | `hf_xxxxxxxxxxxx` |
| `OPENAI_API_KEY` | (Optional) OpenAI key if using | `sk-...` |

**To get your HF_TOKEN:**
1. Go to https://huggingface.co/settings/tokens
2. Click **"New token"**
3. Choose **"Read"** or **"Write"** access
4. Copy the token value
5. Paste into Space Settings under `HF_TOKEN`

5. Click **Save** for each variable
6. Space will automatically restart with new environment

---

## STEP 7: Wait for Deployment

Monitor deployment status:

1. Go to your Space URL
2. Look for status indicator (top-right)
3. States:
   - 🟡 **Building** — Docker image being built
   - 🟡 **Running** — Container starting up
   - 🟢 **Running** — Ready to use (~5 minutes)
   - 🔴 **Error** — Build/runtime failure

**Logs location:**
- Click **View logs** button on Space page
- Shows real-time build and runtime output

---

## STEP 8: Test Your Deployment

Once Space shows 🟢 **Running**, test these endpoints:

### Test 1: Health Check
```bash
curl https://{username}-email-triage-env.hf.space/healthz
```

**Expected response:**
```json
{"status":"ok","environment":"email-triage-env"}
```

### Test 2: Interactive API Docs
```
https://{username}-email-triage-env.hf.space/docs
```

Should show Swagger UI with all endpoints

### Test 3: Reset Environment
```bash
curl -X POST https://{username}-email-triage-env.hf.space/reset
```

**Expected response:**
```json
{
  "status": "reset",
  "first_email": {
    "id": "email_01",
    "sender": "...",
    "subject": "...",
    ...
  }
}
```

### Test 4: Get State
```bash
curl https://{username}-email-triage-env.hf.space/state
```

**Expected response:**
```json
{
  "current_email": {...},
  "step_count": 0,
  "total_reward": 0.0,
  "done": false
}
```

### Test 5: Submit Action
```bash
curl -X POST https://{username}-email-triage-env.hf.space/step \
  -H "Content-Type: application/json" \
  -d '{
    "email_id": "email_01",
    "priority": "urgent",
    "category": "billing",
    "reply": "Thank you for your notification."
  }'
```

---

## STEP 9: Add OpenEnv Tag

To mark your Space as an OpenEnv submission:

1. Go to Space page: `https://huggingface.co/spaces/{username}/email-triage-env`
2. Click **Settings**
3. Scroll to **Tags** section
4. Add tags: `openenv`, `email`, `classification`, `benchmark`
5. Save

---

## STEP 10: Share Your Space

Your Space is now live! Share the URL:

```
https://huggingface.co/spaces/{username}/email-triage-env
```

---

## Common Errors & Fixes

### Error 1: "Port 8000 is not accessible"

**Cause**: Dockerfile still uses port 8000 instead of 7860

**Fix**:
```dockerfile
# Change from:
EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# To:
EXPOSE 7860
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

Then push: `git add . && git commit -m "Fix port" && git push`

---

### Error 2: "Module `env` not found"

**Cause**: `__init__.py` files missing in directories

**Fix**: Create empty files:
```bash
touch env/__init__.py
touch api/__init__.py
git add env/__init__.py api/__init__.py
git commit -m "Add __init__.py files"
git push
```

---

### Error 3: "requirements.txt not found"

**Cause**: File wasn't pushed to Space repository

**Check**:
```bash
git ls-files | grep requirements.txt
```

**Fix**:
```bash
git add requirements.txt
git commit -m "Add requirements.txt"
git push
```

---

### Error 4: "ImportError: No module named 'openai'"

**Cause**: Dependency not in requirements.txt

**Fix**: Ensure `requirements.txt` contains:
```
fastapi>=0.111.0
uvicorn[standard]>=0.29.0
pydantic>=2.7.0
openai>=1.30.0
python-dotenv>=1.0.0
httpx>=0.27.0
pytest>=8.2.0
pytest-asyncio>=0.23.0
```

---

### Error 5: "Health check failed: curl exiting with code 1"

**Cause**: Application crashed or not responding

**Debug**:
1. Click **View logs** on Space page
2. Look for Python stack traces
3. Common causes:
   - Missing environment variables
   - Import errors
   - Port binding failure

**Fix**:
```bash
# Check logs real-time
# Fix the error locally
# Rebuild and push:
git add .
git commit -m "Fix error"
git push
```

---

### Error 6: "Environment variables not being read"

**Cause**: Variables set in wrong place or syntax error

**Verify**:
1. Check Space Settings page shows your variables
2. Ensure variable names match exactly:
   - `API_BASE_URL` (not `api_base_url`)
   - `MODEL_NAME` (not `model_name`)
   - `HF_TOKEN` (not `hf_token`)
3. Click **Save** after each variable
4. Wait 30 seconds for Space to restart

---

## Testing Inference.py Against Your Space

Once deployed, you can run inference against your Space:

```bash
# Set environment variables
$env:API_BASE_URL = "https://router.huggingface.co/v1"
$env:MODEL_NAME = "Qwen/Qwen2.5-72B-Instruct"
$env:HF_TOKEN = "hf_your_token_here"

# The inference script will automatically use your deployed Space
# (You'll need to modify inference.py to point to your Space URL)
```

---

## Final Checklist

- [ ] Space created on HF
- [ ] All files pushed (env/, api/, inference.py, etc.)
- [ ] Dockerfile updated for port 7860
- [ ] Environment variables set (API_BASE_URL, MODEL_NAME, HF_TOKEN)
- [ ] Space built successfully (🟢 Running)
- [ ] `/healthz` endpoint returns 200
- [ ] `/docs` endpoint loads Swagger UI
- [ ] `/reset` endpoint returns first email
- [ ] OpenEnv tag added
- [ ] Space URL shared with team

---

## Quick Reference: Your Space URLs

Once deployed:

| Purpose | URL |
|---------|-----|
| **Main Space** | `https://huggingface.co/spaces/{username}/email-triage-env` |
| **API Base** | `https://{username}-email-triage-env.hf.space` |
| **API Docs** | `https://{username}-email-triage-env.hf.space/docs` |
| **Health Check** | `https://{username}-email-triage-env.hf.space/healthz` |
| **Space Settings** | `https://huggingface.co/spaces/{username}/email-triage-env/settings` |

Replace `{username}` with your HuggingFace username.

---

## Support

- **HF Spaces Docs**: https://huggingface.co/docs/hub/spaces
- **HF API Docs**: https://huggingface.co/docs/api
- **Docker in Spaces**: https://huggingface.co/docs/hub/spaces-config-reference#docker

