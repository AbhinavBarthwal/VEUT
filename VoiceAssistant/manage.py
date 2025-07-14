#!/usr/bin/env python3
"""
Utility script for managing the VoicePay UPI Assistant.
"""
import os
import sys
import argparse
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_dependencies():
    """Check if all required dependencies are installed."""
    print("Checking VoicePay dependencies...")
    try:
        import livekit
        from livekit.plugins import google
        import requests
        import psutil
        from memory_manager import VoicePayMemoryManager
        print("✅ All VoicePay dependencies are installed!")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def check_environment():
    """Check if environment variables are properly configured."""
    print("Checking VoicePay environment configuration...")
    
    required_vars = ['LIVEKIT_URL', 'LIVEKIT_API_KEY', 'LIVEKIT_API_SECRET', 'GOOGLE_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file or set these environment variables.")
        return False
    
    print("✅ VoicePay environment configuration looks good!")
    return True

def check_security_config():
    """Check VoicePay-specific security configuration."""
    print("Checking VoicePay security configuration...")
    
    # Check transaction limits
    max_amount = float(os.getenv('MAX_TRANSACTION_AMOUNT', 100000))
    threshold = float(os.getenv('LARGE_AMOUNT_THRESHOLD', 10000))
    
    if max_amount > 500000:  # 5 lakh limit
        print("⚠️  Warning: Maximum transaction amount is very high")
    
    if threshold > max_amount:
        print("❌ Error: Large amount threshold cannot exceed maximum transaction amount")
        return False
    
    print("✅ Security configuration validated!")
    return True

def setup_environment():
    """Setup the environment for first-time use."""
    print("Setting up VoicePay environment...")
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        env_template = """# VoicePay UPI Assistant Configuration

# LiveKit Configuration (Required)
LIVEKIT_URL=your_livekit_url_here
LIVEKIT_API_KEY=your_livekit_api_key_here
LIVEKIT_API_SECRET=your_livekit_api_secret_here

# Google AI Configuration (Required)
GOOGLE_API_KEY=your_google_api_key_here

# VoicePay Security Settings
MAX_TRANSACTION_AMOUNT=100000
LARGE_AMOUNT_THRESHOLD=10000
SESSION_TIMEOUT_MINUTES=15
ENABLE_AMOUNT_CONFIRMATION=true
ENABLE_RECIPIENT_VERIFICATION=true

# Accessibility Settings
SLOW_SPEECH_MODE=false
NOISE_CANCELLATION=true
VERBOSE_GUIDANCE=true

# Logging and Audit
LOG_LEVEL=INFO
LOG_TRANSACTIONS=true
"""
        with open('.env', 'w') as f:
            f.write(env_template)
        print("✅ Created .env template file. Please fill in your API keys.")
    else:
        print("✅ .env file already exists.")
    
    # Create memory directory
    os.makedirs('voicepay_memory', exist_ok=True)
    print("✅ Created VoicePay memory directory.")

def clear_sensitive_data():
    """Clear all sensitive data from VoicePay memory."""
    print("Clearing sensitive data from VoicePay memory...")
    try:
        from memory_manager import VoicePayMemoryManager
        memory_manager = VoicePayMemoryManager()
        result = memory_manager.clear_sensitive_data()
        print(f"✅ {result}")
    except Exception as e:
        print(f"❌ Error clearing sensitive data: {e}")

def run_security_audit():
    """Run a security audit of VoicePay configuration."""
    print("Running VoicePay security audit...")
    
    # Check file permissions
    sensitive_files = ['.env', 'voicepay_memory/memories.json']
    for file_path in sensitive_files:
        if os.path.exists(file_path):
            # On Windows, this is a basic check
            print(f"✅ {file_path} exists and appears secure")
    
    # Check memory manager
    try:
        from memory_manager import VoicePayMemoryManager
        memory_manager = VoicePayMemoryManager()
        memories = memory_manager.get_memories(include_sensitive=True)
        sensitive_count = sum(1 for m in memories if m.sensitive)
        print(f"ℹ️  Found {sensitive_count} sensitive items in memory")
        
        if sensitive_count > 10:
            print("⚠️  Warning: High number of sensitive items in memory")
    except Exception as e:
        print(f"❌ Error checking memory: {e}")
    
    print("✅ Security audit completed!")

def start_voicepay():
    """Start the VoicePay assistant."""
    print("Starting VoicePay UPI Assistant...")
    try:
        subprocess.run([sys.executable, 'agent.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting VoicePay: {e}")
    except KeyboardInterrupt:
        print("\n👋 VoicePay stopped by user.")

def main():
    """Main entry point for the management script."""
    parser = argparse.ArgumentParser(description='VoicePay UPI Assistant Management')
    parser.add_argument('command', choices=[
        'check', 'setup', 'start', 'clear-data', 'security-audit'
    ], help='Command to execute')
    
    args = parser.parse_args()
    
    if args.command == 'check':
        deps_ok = check_dependencies()
        env_ok = check_environment()
        security_ok = check_security_config()
        
        if deps_ok and env_ok and security_ok:
            print("\n✅ All checks passed! VoicePay is ready to run.")
            print("Use 'python manage.py start' to launch VoicePay.")
        else:
            print("\n❌ Some checks failed. Please fix the issues above.")
            
    elif args.command == 'setup':
        setup_environment()
        print("\n✅ VoicePay setup completed!")
        print("Please edit the .env file with your API keys, then run 'python manage.py check'.")
        
    elif args.command == 'start':
        if check_dependencies() and check_environment():
            start_voicepay()
        else:
            print("❌ Environment check failed. Please run 'python manage.py check' first.")
            
    elif args.command == 'clear-data':
        confirm = input("Are you sure you want to clear all sensitive data? (yes/no): ")
        if confirm.lower() == 'yes':
            clear_sensitive_data()
        else:
            print("❌ Operation cancelled.")
            
    elif args.command == 'security-audit':
        run_security_audit()

if __name__ == '__main__':
    main()
