"""
YouTube Channel RAG - Windows Setup Helper
Resolves compiler and dependency issues on Windows
"""

import subprocess
import sys
import os

def run_command(cmd, description=""):
    """Run a shell command and report status."""
    print(f"\n{'='*60}")
    print(f"▶️  {description}")
    print(f"{'='*60}")
    print(f"Command: {cmd}\n")
    
    result = subprocess.run(cmd, shell=True, cwd=os.getcwd())
    
    if result.returncode != 0:
        print(f"\n❌ Error running: {description}")
        return False
    else:
        print(f"\n✅ Success: {description}")
        return True

def main():
    print("\n" + "="*60)
    print("YouTube Channel RAG - Windows Setup")
    print("="*60)
    
    steps = [
        ("python -m pip install --upgrade pip", "Upgrading pip (important for Windows)"),
        ("pip cache purge", "Clearing pip cache"),
        ("pip install --only-binary=:all: -r requirements.txt", "Installing dependencies (binary wheels only)"),
    ]
    
    failed_steps = []
    
    for cmd, desc in steps:
        if not run_command(cmd, desc):
            failed_steps.append(desc)
    
    print("\n" + "="*60)
    if failed_steps:
        print("⚠️  Some steps failed:")
        for step in failed_steps:
            print(f"  - {step}")
        print("\nTroubleshooting:")
        print("1. Make sure you're in a Python 3.9+ virtual environment")
        print("2. Try: pip install --prefer-binary -r requirements.txt")
        print("3. If still failing, use Miniconda:")
        print("   - Download: https://docs.conda.io/projects/miniconda/")
        print("   - conda create -n youtube-rag python=3.11")
        print("   - conda activate youtube-rag")
        print("   - pip install -r requirements.txt")
        return False
    else:
        print("✅ All dependencies installed successfully!")
        print("\n📝 Next steps:")
        print("1. Copy .env.template to .env")
        print("2. Add your OpenAI API key to .env")
        print("3. Run: streamlit run app.py")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
