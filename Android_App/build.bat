@echo off
echo 🎙️ VoicePay Android Build Assistant
echo ==================================

if not exist "gradlew.bat" (
    echo ❌ gradlew.bat not found. Make sure you're in the Android_App directory.
    pause
    exit /b 1
)

echo 📋 Available commands:
echo 1. Clean project
echo 2. Build debug APK
echo 3. Install debug APK
echo 4. Run tests
echo 5. Check for UPI apps on device
echo 6. Full build and install

set /p choice=Enter your choice (1-6): 

if "%choice%"=="1" (
    echo 🧹 Cleaning project...
    gradlew.bat clean
    goto end
)

if "%choice%"=="2" (
    echo 🔨 Building debug APK...
    gradlew.bat assembleDebug
    echo 📦 APK location: app\build\outputs\apk\debug\app-debug.apk
    goto end
)

if "%choice%"=="3" (
    echo 📱 Installing debug APK to connected device...
    gradlew.bat installDebug
    goto end
)

if "%choice%"=="4" (
    echo 🧪 Running tests...
    gradlew.bat test
    goto end
)

if "%choice%"=="5" (
    echo 🔍 Checking for UPI apps on connected device...
    adb shell pm list packages | findstr /R "phonepe paytm google.*pay upi bhim mobikwik freecharge"
    goto end
)

if "%choice%"=="6" (
    echo 🚀 Full build and install...
    gradlew.bat clean assembleDebug installDebug
    echo ✅ VoicePay installed! You can now launch it on your device.
    goto end
)

echo ❌ Invalid choice. Please run the script again.

:end
echo.
echo 📚 Quick tips:
echo - Ensure microphone permission is granted
echo - Install at least one UPI app (PhonePe, Google Pay, etc.)
echo - Test voice commands in a quiet environment
echo - Check logcat for debugging: adb logcat | findstr VoicePay
pause
