# Windows Setup Guide - YouTube Channel RAG

## Issue: GCC Compiler Error

If you see an error like:
```
NumPy requires GCC >= 8.4
```

This is a **Windows MinGW compiler issue**. Your system has an old GCC compiler. Here are the solutions:

---

## ✅ Solution 1: Quick Fix (Recommended)

Run the Windows setup script we created:

```bash
# Make sure you're in the venv first
venv\Scripts\activate

# Run the setup script
python setup_windows.py
```

This script will:
1. ✅ Upgrade pip (crucial for Windows)
2. ✅ Clear pip cache
3. ✅ Install only pre-built binary wheels (no compilation needed)

---

## ✅ Solution 2: Manual Fix

If the script doesn't work, run these commands manually:

```bash
# Activate venv
venv\Scripts\activate

# Upgrade pip (very important!)
python -m pip install --upgrade pip

# Clear cache
pip cache purge

# Install with binary wheels only
pip install --only-binary=:all: -r requirements.txt
```

---

## ✅ Solution 3: Use Miniconda (If solutions 1-2 fail)

**Why Miniconda?** It comes with pre-compiled packages for Windows (no GCC needed).

### Steps:
1. **Download Miniconda**: https://docs.conda.io/projects/miniconda/en/latest/
2. **Run installer** and choose "Add to PATH"
3. **Close and reopen PowerShell**
4. **Create environment**:
   ```bash
   conda create -n youtube-rag python=3.11
   ```
5. **Activate it**:
   ```bash
   conda activate youtube-rag
   ```
6. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
7. **Run the app**:
   ```bash
   streamlit run app.py
   ```

---

## ✅ Solution 4: Install Visual C++ Build Tools (For Future Use)

If you want to avoid compiler issues forever:

1. Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Run installer → Select "Desktop development with C++"
3. Wait for installation (~10 minutes)
4. Then: `pip install -r requirements.txt`

---

## Why Does This Happen on Windows?

- **Linux/Mac**: Come with GCC compilers built-in
- **Windows**: Doesn't include C++ compilers
- **Solution**: Use pre-built binaries (wheels) instead of compiling from source

---

## Verification After Install

Once installation succeeds, verify everything:

```bash
python verify_setup.py
```

Should show all ✅ checks passing.

---

## Still Having Issues?

Try this debug command to see what pip is doing:

```bash
pip install -vv -r requirements.txt
```

And share the error output if problems persist.

---

## Your Fastest Path Forward

1. Try `python setup_windows.py` first (takes 2-3 minutes)
2. If that fails, install Miniconda (takes 5 minutes total)
3. Then you're done forever—no more compiler issues!
