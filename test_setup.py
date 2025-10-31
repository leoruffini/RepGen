"""
Test script to verify the Sales Visit Report Generator setup.

Run this script to check if all dependencies and configurations are correct.
"""

import sys
import os

def test_python_version():
    """Check Python version."""
    version = sys.version_info
    print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("  ⚠️  Warning: Python 3.10+ is recommended")
        return False
    return True

def test_imports():
    """Test if all required packages can be imported."""
    packages = {
        'streamlit': 'Streamlit',
        'assemblyai': 'AssemblyAI SDK',
        'openai': 'OpenAI SDK',
        'dotenv': 'python-dotenv'
    }
    
    all_good = True
    for package, name in packages.items():
        try:
            if package == 'dotenv':
                __import__('dotenv')
            else:
                __import__(package)
            print(f"✓ {name} is installed")
        except ImportError:
            print(f"✗ {name} is NOT installed")
            all_good = False
    
    return all_good

def test_env_file():
    """Check if .env file exists."""
    if os.path.exists('.env'):
        print("✓ .env file exists")
        return True
    else:
        print("✗ .env file NOT found")
        return False

def test_api_keys():
    """Check if API keys are set."""
    from dotenv import load_dotenv
    load_dotenv()
    
    keys_status = {
        'ASSEMBLYAI_API_KEY': bool(os.getenv('ASSEMBLYAI_API_KEY')),
        'OPENAI_API_KEY': bool(os.getenv('OPENAI_API_KEY'))
    }
    
    all_good = True
    for key, status in keys_status.items():
        if status:
            print(f"✓ {key} is set")
        else:
            print(f"✗ {key} is NOT set")
            all_good = False
    
    return all_good

def test_prompt_config():
    """Check if OpenAI prompt ID is configured."""
    # Load .env if not already loaded
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    prompt_id = os.getenv("OPENAI_PROMPT_ID")
    if prompt_id:
        print(f"✓ OPENAI_PROMPT_ID configured: {prompt_id[:20]}...")
        return True
    else:
        print("✗ OPENAI_PROMPT_ID NOT configured in .env")
        return False

def test_transcriptions_folder():
    """Check if transcriptions folder exists."""
    if os.path.exists('transcriptions'):
        print("✓ transcriptions/ folder exists")
        return True
    else:
        print("⚠️  transcriptions/ folder doesn't exist (will be created automatically)")
        return True

def main():
    """Run all tests."""
    print("=" * 60)
    print("Sales Visit Report Generator - Setup Test")
    print("=" * 60)
    print()
    
    print("1. Python Version")
    print("-" * 60)
    python_ok = test_python_version()
    print()
    
    print("2. Required Packages")
    print("-" * 60)
    imports_ok = test_imports()
    print()
    
    print("3. Configuration Files")
    print("-" * 60)
    env_ok = test_env_file()
    prompt_ok = test_prompt_config()
    trans_ok = test_transcriptions_folder()
    print()
    
    print("4. API Keys")
    print("-" * 60)
    keys_ok = test_api_keys()
    print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_tests = [python_ok, imports_ok, env_ok, prompt_ok, trans_ok, keys_ok]
    
    if all(all_tests):
        print("✅ All checks passed! You're ready to run the application.")
        print()
        print("Next step: Run the application with:")
        print("  streamlit run app.py")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print()
        if not imports_ok:
            print("To install missing packages, run:")
            print("  pip install -r requirements.txt")
        if not env_ok or not keys_ok:
            print("Make sure your .env file exists with:")
            print("  ASSEMBLYAI_API_KEY=your_key_here")
            print("  OPENAI_API_KEY=your_key_here")
    
    print()

if __name__ == "__main__":
    main()



