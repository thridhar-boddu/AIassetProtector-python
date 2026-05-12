# ============================================================
# AssetGuardian Backend — Local Development Runner (Python)
# ============================================================
# Required environment variables (set in your shell or .env):
#   ALLOWED_ORIGINS   e.g. http://localhost:5173
#   AI_SERVICE_URL    e.g. http://localhost:8000  (optional)
# ============================================================

# Setup Virtual Environment if missing
if (!(Test-Path "venv")) {
    Write-Host "Creating Virtual Environment..."
    python -m venv venv
}

# Activate Virtual Environment and Install Requirements
Write-Host "Installing Requirements..."
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run FastAPI
Write-Host "Starting AssetGuardian Backend (Python FastAPI)..." -ForegroundColor Cyan
python main.py
