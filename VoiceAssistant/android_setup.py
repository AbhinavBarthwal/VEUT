#!/usr/bin/env python3
"""
Android Setup Helper for VoicePay Real-time Integration
This script helps users set up their Android device for real-time UPI functionality.
"""

import subprocess
import sys
import os
import time
from typing import Tuple, Optional

def check_adb_installation() -> Tuple[bool, str]:
    """Check if ADB is installed and accessible."""
    try:
        result = subprocess.run(['adb', 'version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_info = result.stdout.split('\n')[0]
            return True, f"✅ ADB is installed: {version_info}"
        else:
            return False, "❌ ADB is installed but not working properly"
    except FileNotFoundError:
        return False, "❌ ADB is not installed"
    except subprocess.TimeoutExpired:
        return False, "❌ ADB command timed out"
    except Exception as e:
        return False, f"❌ Error checking ADB: {e}"

def check_device_connection() -> Tuple[bool, str, Optional[str]]:
    """Check if Android device is connected and authorized."""
    try:
        result = subprocess.run(['adb', 'devices'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            
            if not lines or all(not line.strip() for line in lines):
                return False, "❌ No devices connected", None
            
            devices = []
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        device_id, status = parts[0], parts[1]
                        devices.append((device_id, status))
            
            if not devices:
                return False, "❌ No devices detected", None
            
            # Check if any device is properly authorized
            authorized_devices = [d for d in devices if d[1] == 'device']
            unauthorized_devices = [d for d in devices if d[1] == 'unauthorized']
            
            if authorized_devices:
                device_id = authorized_devices[0][0]
                return True, f"✅ Device connected and authorized: {device_id}", device_id
            elif unauthorized_devices:
                device_id = unauthorized_devices[0][0]
                return False, f"⚠️ Device connected but unauthorized: {device_id}", device_id
            else:
                return False, f"❌ Device in unknown state: {devices[0]}", devices[0][0]
        else:
            return False, "❌ Failed to check devices", None
    except Exception as e:
        return False, f"❌ Error checking devices: {e}", None

def get_device_info(device_id: str) -> str:
    """Get basic device information."""
    try:
        # Get device model
        model_result = subprocess.run(['adb', '-s', device_id, 'shell', 'getprop', 'ro.product.model'], 
                                    capture_output=True, text=True, timeout=5)
        model = model_result.stdout.strip() if model_result.returncode == 0 else "Unknown"
        
        # Get Android version
        version_result = subprocess.run(['adb', '-s', device_id, 'shell', 'getprop', 'ro.build.version.release'], 
                                      capture_output=True, text=True, timeout=5)
        version = version_result.stdout.strip() if version_result.returncode == 0 else "Unknown"
        
        return f"📱 Device: {model}, Android {version}"
    except Exception as e:
        return f"📱 Device info unavailable: {e}"

def check_upi_apps(device_id: str) -> Tuple[bool, str]:
    """Check for installed UPI apps on the device."""
    try:
        result = subprocess.run(['adb', '-s', device_id, 'shell', 'pm', 'list', 'packages'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            return False, "❌ Failed to check installed apps"
        
        packages = result.stdout.lower()
        upi_apps = {
            "com.phonepe.app": "PhonePe",
            "com.google.android.apps.nbu.paisa.user": "Google Pay",
            "net.one97.paytm": "Paytm",
            "com.amazon.amazonpayments": "Amazon Pay",
            "in.org.npci.upiapp": "BHIM UPI",
            "com.mobikwik.mobile": "MobiKwik",
            "com.freecharge.android": "Freecharge"
        }
        
        found_apps = []
        for package, name in upi_apps.items():
            if f"package:{package}" in packages:
                found_apps.append(name)
        
        if found_apps:
            apps_list = ", ".join(found_apps)
            return True, f"💳 UPI Apps found: {apps_list}"
        else:
            return False, "❌ No UPI apps detected"
            
    except Exception as e:
        return False, f"❌ Error checking UPI apps: {e}"

def provide_setup_instructions():
    """Provide detailed setup instructions."""
    print("\n" + "="*60)
    print("🔧 ANDROID SETUP INSTRUCTIONS FOR VOICEPAY")
    print("="*60)
    
    print("\n1. 📱 ENABLE DEVELOPER OPTIONS:")
    print("   • Go to Settings > About Phone")
    print("   • Tap 'Build Number' 7 times")
    print("   • You'll see 'You are now a developer!'")
    
    print("\n2. 🔌 ENABLE USB DEBUGGING:")
    print("   • Go to Settings > Developer Options")
    print("   • Enable 'USB Debugging'")
    print("   • Enable 'USB Debugging (Security Settings)' if available")
    
    print("\n3. 🔗 CONNECT YOUR DEVICE:")
    print("   • Connect your Android device via USB cable")
    print("   • Select 'File Transfer' or 'MTP' mode when prompted")
    print("   • Allow USB debugging when dialog appears on phone")
    
    print("\n4. 💻 INSTALL ADB (if not already installed):")
    print("   • Windows: winget install Google.AndroidStudioPlatformTools")
    print("   • Or download from: developer.android.com/studio/releases/platform-tools")
    print("   • Add to system PATH")
    
    print("\n5. ✅ TEST CONNECTION:")
    print("   • Run this script again to verify setup")
    print("   • Or run 'adb devices' in command prompt")

def main():
    """Main setup checker and helper."""
    print("🚀 VoicePay Android Setup Checker")
    print("-" * 40)
    
    # Check ADB installation
    adb_ok, adb_msg = check_adb_installation()
    print(f"\n{adb_msg}")
    
    if not adb_ok:
        print("\n❗ ADB is required for real-time UPI functionality")
        provide_setup_instructions()
        return
    
    # Check device connection
    device_ok, device_msg, device_id = check_device_connection()
    print(f"{device_msg}")
    
    if not device_ok:
        if "unauthorized" in device_msg:
            print("\n❗ Please check your phone and allow USB debugging")
            print("   Look for a dialog asking to 'Allow USB debugging?'")
            print("   Check 'Always allow from this computer' and tap 'OK'")
            
            print("\n⏳ Waiting 10 seconds for authorization...")
            time.sleep(10)
            
            # Check again
            device_ok, device_msg, device_id = check_device_connection()
            print(f"\n{device_msg}")
        
        if not device_ok:
            provide_setup_instructions()
            return
    
    # If device is connected, get more info
    if device_id:
        device_info = get_device_info(device_id)
        print(f"{device_info}")
        
        # Check UPI apps
        upi_ok, upi_msg = check_upi_apps(device_id)
        print(f"{upi_msg}")
        
        if not upi_ok:
            print("\n💡 Consider installing UPI apps like PhonePe, Google Pay, or Paytm")
    
    # Final status
    print("\n" + "="*50)
    if device_ok:
        print("🎉 SETUP COMPLETE! VoicePay is ready for real-time UPI functionality!")
        print("\nYou can now:")
        print("• Automatically detect installed UPI apps")
        print("• Open apps with pre-filled payment details")
        print("• Monitor transaction notifications")
        print("• Get real-time transaction status")
    else:
        print("⚠️  Setup incomplete. Follow the instructions above to enable full functionality.")
        print("   VoicePay will still work with manual instructions.")
    print("="*50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check your setup and try again.")
