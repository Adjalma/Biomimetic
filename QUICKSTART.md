# Quick Start - Biomimetic Evolutionary System

## 1. First Time Setup

Run the installer:
```
.\setup.bat
```
Or use the simple launcher:
```
.\run.bat
```

## 2. Install Dependencies

If you get "No module named 'fastapi'" error:

**Option A:** Run the installer
```
.\install_essential.bat
```

**Option B:** Manual installation
```
# Create virtual environment (if not exists)
python -m venv venv

# Activate
venv\Scripts\activate.bat

# Install essential packages
pip install fastapi uvicorn pydantic numpy requests
```

## 3. Start the System

**Start everything (recommended):**
```
.\start_all.bat
```

**Or use the menu:**
```
.\run.bat
```
Then choose option 4 (Start Both).

## 4. Access the System

- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Frontend Dashboard:** http://localhost:3000

## 5. Test the API

```powershell
# Check health
curl http://localhost:8000/health

# Or in PowerShell:
Invoke-WebRequest -Uri "http://localhost:8000/health"
```

## 6. Troubleshooting

**Problem:** Script closes immediately
- Run from Command Prompt (cmd.exe), not PowerShell
- Or open a Command Prompt window first, then navigate to the folder

**Problem:** "ModuleNotFoundError: No module named 'fastapi'"
- Run `.\install_essential.bat`
- Or activate virtual environment manually and install packages

**Problem:** "primeiro. foi inesperado"
- Use the new scripts without emojis: `start_all.bat` or `run.bat`
- Already fixed in latest version (git pull)

## 7. Update from Repository

```bash
git pull origin main
```

## Need Help?

The system is now fully operational. Test the evolution API endpoints via the Swagger UI at `http://localhost:8000/docs`.