#!/bin/bash

# VoicePay Android Build Script

echo "🎙️ VoicePay Android Build Assistant"
echo "=================================="

# Check if gradlew exists
if [ ! -f "./gradlew" ]; then
    echo "❌ gradlew not found. Make sure you're in the Android_App directory."
    exit 1
fi

# Make gradlew executable
chmod +x ./gradlew

echo "📋 Available commands:"
echo "1. Clean project"
echo "2. Build debug APK"
echo "3. Install debug APK"
echo "4. Run tests"
echo "5. Check for UPI apps on device"
echo "6. Full build and install"

read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        echo "🧹 Cleaning project..."
        ./gradlew clean
        ;;
    2)
        echo "🔨 Building debug APK..."
        ./gradlew assembleDebug
        echo "📦 APK location: app/build/outputs/apk/debug/app-debug.apk"
        ;;
    3)
        echo "📱 Installing debug APK to connected device..."
        ./gradlew installDebug
        ;;
    4)
        echo "🧪 Running tests..."
        ./gradlew test
        ;;
    5)
        echo "🔍 Checking for UPI apps on connected device..."
        adb shell pm list packages | grep -E "(phonepe|paytm|google.*pay|upi|bhim|mobikwik|freecharge)"
        ;;
    6)
        echo "🚀 Full build and install..."
        ./gradlew clean assembleDebug installDebug
        echo "✅ VoicePay installed! You can now launch it on your device."
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        ;;
esac

echo ""
echo "📚 Quick tips:"
echo "- Ensure microphone permission is granted"
echo "- Install at least one UPI app (PhonePe, Google Pay, etc.)"
echo "- Test voice commands in a quiet environment"
echo "- Check logcat for debugging: adb logcat | grep VoicePay"
