# 🎩 VoicePay - AI-Powered UPI Payment Assistant

**A sophisticated voice-driven UPI payment assistant designed specifically for visually impaired and elderly users**

VoicePay acts like a classy British butler, guiding users through UPI transactions with utmost security, accessibility, and real-time Android device integration.

---

## 🎯 **Mission**

VoicePay revolutionizes UPI (Unified Payments Interface) transactions by making them completely voice-accessible. Designed for visually impaired and elderly users who struggle with complex smartphone interfaces, VoicePay provides a secure, intuitive voice-driven payment experience.

---

## 🔒 **Security First Philosophy**

- **🔐 Never handles UPI PINs** - User enters PIN manually for complete security
- **🚫 No payment authorization** - Only assists with filling details, never submits payments
- **🗑️ No sensitive data storage** - Payment details are cleared from memory immediately
- **🗣️ Voice confirmation required** - All transactions require explicit voice confirmation
- **💰 Amount verification** - Large transactions (>₹10,000) require additional confirmation
- **⏰ Auto-timeout** - Sessions automatically expire for security
- **🔍 Security auditing** - All security events are logged for compliance

---

## 🚀 **Key Features**

### **Real-time Android Integration**
- **📱 Automatic UPI App Detection**: Detects installed UPI apps on your Android device via ADB
- **🚀 Direct App Launch**: Opens UPI apps with pre-filled payment details using Android intents
- **📊 Transaction Monitoring**: Monitors Android notifications for real-time payment status
- **✅ UPI ID Validation**: Real-time validation of UPI IDs and payment details
- **🔗 Device Security**: Secure ADB connection with USB debugging controls

### **Core UPI Assistance**
- **🔍 Smart App Detection**: PhonePe, Google Pay, Paytm, Amazon Pay, BHIM UPI, and more
- **🎤 Voice Payment Processing**: Extract recipient and amount from natural voice commands
- **🏦 Bank Account Management**: Helps choose from linked bank accounts
- **🛡️ Safety Checks**: Confirms large amounts and verifies new recipients
- **📲 Seamless App Integration**: Opens and pre-fills UPI apps with transaction details
- **👥 Transaction Guidance**: Step-by-step voice guidance through the entire payment process

### **Accessibility Features**
- **🎩 British Butler Persona**: Polite, formal interaction style addressing users as "Sir/Madam"
- **📢 Clear Voice Feedback**: Reads all details aloud for confirmation
- **🔊 Noise Cancellation**: Enhanced audio processing for crystal-clear communication
- **🐌 Adjustable Speech Rate**: Configurable speech speed for elderly users
- **📝 Verbose Guidance**: Detailed step-by-step instructions for every action
- **♿ Universal Design**: Built from ground up for accessibility compliance

### **Technical Excellence**
- **⚡ Real-time voice interaction** with LiveKit framework
- **🧠 Google Gemini AI** for advanced natural language processing
- **🔒 Secure memory management** with automatic cleanup protocols
- **⚙️ Configurable limits** for transaction amounts and safety thresholds
- **🛠️ Enhanced error handling** with accessibility-focused recovery

---

## 📱 **Android Integration Setup**

### **Prerequisites**
1. **Android Device** with UPI apps installed
2. **USB Cable** for device connection  
3. **Windows PC** with Python 3.8+
4. **ADB (Android Debug Bridge)** tools

### **Quick Setup**
```powershell
# 1. Install ADB Tools (Windows)
winget install Google.AndroidStudioPlatformTools

# 2. Enable Developer Options on Android
# Settings > About Phone > Tap "Build Number" 7 times

# 3. Enable USB Debugging  
# Settings > Developer Options > USB Debugging

# 4. Connect device and run setup checker
cd VoiceAssistant
python android_setup.py
```

### **Supported UPI Apps**
- **PhonePe** - Full deep link integration
- **Google Pay (GPay)** - Real-time app launch
- **Paytm** - Payment pre-filling
- **Amazon Pay** - Transaction monitoring
- **BHIM UPI** - Government UPI app
- **MobiKwik** - Wallet integration
- **Bank UPI Apps** - SBI Pay, ICICI iMobile, HDFC, Axis Bank, etc.

---

## 🛠 **Installation & Setup**

### **1. Clone Repository**
```bash
git clone https://github.com/AbhinavBarthwal/VEUT.git
cd VEUT/VoiceAssistant
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Environment Configuration**
```bash
cp .env.example .env
```

Edit `.env` file with your credentials:
```env
# LiveKit Configuration
LIVEKIT_URL=your_livekit_server_url
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret

# Google AI Configuration
GOOGLE_API_KEY=your_google_gemini_api_key

# VoicePay Security Settings
MAX_TRANSACTION_AMOUNT=100000
LARGE_AMOUNT_THRESHOLD=10000
SESSION_TIMEOUT_MINUTES=15
VOICEPAY_TEMPERATURE=0.3
```

### **4. Verify Setup**
```bash
# Check configuration
python manage.py check

# Test Android connection (optional)
python android_setup.py
```

---

## 🎮 **Usage Guide**

### **Starting VoicePay**
```bash
python agent.py
```

**VoicePay Greeting:**
> *"Good day, Sir. I am VoicePay, your personal UPI payment butler. I shall be delighted to assist you with your payment transactions today. How may I be of service?"*

### **Example Transaction Flow**

#### **1. Initiate Payment**
- **User:** *"I want to pay ₹500 to john@paytm"*
- **VoicePay:** *"Certainly, Sir. I have detected PhonePe and Google Pay installed. Which application would you prefer to use?"*

#### **2. App Selection**
- **User:** *"Use PhonePe"*
- **VoicePay:** *"Very well, Sir. Opening PhonePe with your payment details..."*

#### **3. Real-time Integration**
- **VoicePay:** *"Excellent, Sir. I have successfully opened PhonePe with the payment details: ₹500 to john@paytm. Please review the details and complete with your UPI PIN."*

#### **4. Transaction Monitoring**
- **VoicePay:** *"I shall monitor the transaction status. Please let me know once completed, Sir."*

### **Supported Voice Commands**

#### **Payment Commands**
```
"Pay ₹500 to john@paytm"
"Send ₹1000 to Sarah"
"Transfer ₹2500 to merchant@phonepe"
"Pay 1000 rupees to Mom"
```

#### **Device Management**
```
"Check my connected device"
"What UPI apps do I have?"
"Setup Android integration"
"Check device connection"
```

#### **Transaction Control**
```
"Cancel transaction"
"Retry payment"
"Check transaction status"
"Clear transaction data"
"Did my payment go through?"
```

---

## 🏗 **Architecture**

### **Core Components**

1. **🎭 VoicePayAssistant** (`agent.py`) - Main agent with British butler personality
2. **🔧 UPI Tools** (`tools.py`) - Real-time Android integration and UPI functions  
3. **🧠 Memory Manager** (`memory_manager.py`) - Secure memory with auto-cleanup
4. **⚙️ Configuration** (`config.py`) - Security-focused settings management
5. **💬 Prompts** (`prompts.py`) - British butler personality instructions
6. **📱 Android Setup** (`android_setup.py`) - Device integration helper

### **Real-time Android Functions**

| Function | Description |
|----------|-------------|
| `detect_installed_upi_apps()` | Uses ADB to scan installed UPI packages |
| `open_upi_app_with_details()` | Launches apps using Android intents with pre-filled data |
| `check_device_connection()` | Verifies ADB connection and device authorization |
| `get_transaction_status()` | Monitors Android notifications for payment status |
| `extract_payment_details()` | Processes voice commands with UPI ID validation |
| `verify_transaction_safety()` | Performs security checks and amount verification |
| `setup_android_integration()` | Provides device setup guidance |

### **Security Architecture**

- **🔒 Memory Isolation**: Sensitive data isolated and auto-deleted after 1 hour
- **🔐 PIN Protection**: Never handles, requests, or stores UPI PINs
- **⏰ Session Management**: Automatic timeout and cleanup protocols
- **📋 Audit Logging**: Security-focused logging for compliance and monitoring
- **🛡️ Transaction Limits**: Configurable maximum amounts and safety thresholds

---

## ⚙️ **Configuration Options**

Customize VoicePay through environment variables:

```env
# Voice & AI Settings
VOICEPAY_TEMPERATURE=0.3          # Response consistency (0.1-0.5)
SLOW_SPEECH_MODE=false            # Enable slower speech for elderly users

# Security Settings  
MAX_TRANSACTION_AMOUNT=100000     # Maximum transaction limit (₹1,00,000)
LARGE_AMOUNT_THRESHOLD=10000      # Threshold for additional confirmation (₹10,000)
SESSION_TIMEOUT_MINUTES=15        # Session timeout for security

# Accessibility Settings
ENABLE_AMOUNT_CONFIRMATION=true   # Require confirmation for all amounts
VERBOSE_GUIDANCE=true             # Detailed step-by-step instructions

# Logging & Monitoring
LOG_TRANSACTIONS=true             # Enable transaction logging for security audit
ENABLE_NOTIFICATION_MONITORING=true # Monitor Android notifications
```

---

## 🎭 **British Butler Persona**

VoicePay embodies a **sophisticated British butler** personality:

- **🎩 Exceptionally Polite**: Always addresses users as "Sir" or "Madam"
- **👔 Formal Language**: Uses proper British expressions like "Very well, Sir", "Certainly"
- **🛡️ Security Conscious**: Never compromises on financial security protocols
- **🧘 Patient & Understanding**: Designed specifically for elderly and visually impaired users
- **♿ Accessibility First**: Clear speech, confirmations, and comprehensive guidance
- **🔍 Professional**: Maintains dignity while ensuring transaction security

**Example Responses:**
> *"Very well, Sir. I shall proceed with opening PhonePe for your transaction."*
>
> *"I do apologize, Sir, but I must verify this substantial amount for your security."*
>
> *"Excellent! The transaction appears to have completed successfully, Sir."*

---

## 🔧 **Troubleshooting**

### **Android Integration Issues**

#### **"ADB not found"**
```powershell
# Install ADB
winget install Google.AndroidStudioPlatformTools

# Add to PATH if needed
$env:PATH += ";C:\Program Files\Android\platform-tools"
```

#### **"Device unauthorized"**
1. Check phone for USB debugging dialog
2. Tap "Allow" and check "Always allow from this computer"
3. Restart ADB: `adb kill-server` then `adb start-server`

#### **"No UPI apps detected"**
1. Ensure UPI apps are installed and updated
2. Check device connection: `adb devices`
3. Verify USB debugging is enabled

### **Voice Recognition Issues**
- **Speak clearly** and at moderate pace
- **Minimize background noise** for better recognition
- **Use good quality microphone** for optimal results
- **Check audio permissions** for the application

### **Transaction Problems**
- **Verify internet connectivity** on both PC and Android device
- **Ensure UPI app is logged in** and functioning
- **Check sufficient account balance** before transactions
- **Verify recipient UPI ID** format and validity

---

## 🌟 **Security Best Practices**

### **For Users**
1. **🔐 Never share your UPI PIN** with anyone, including VoicePay
2. **✅ Always verify transaction details** before confirming payments
3. **🏠 Use in a private environment** to protect sensitive information
4. **🚪 Log out from UPI apps** when not in use
5. **🚨 Report suspicious activity** to your bank immediately

### **For Developers**
1. **🔒 Secure API key management** - Never commit keys to version control
2. **🧹 Memory cleanup protocols** - Ensure sensitive data is cleared
3. **📝 Audit logging implementation** - Track all security-relevant events
4. **⏰ Session timeout enforcement** - Implement automatic session expiry
5. **🛡️ Input validation** - Sanitize all user inputs and UPI IDs

---

## 🚀 **Advanced Features**

### **Real-time Capabilities**
- **📱 Live app detection** via Android Debug Bridge (ADB)
- **🔗 Deep link integration** with major UPI applications
- **📊 Notification monitoring** for transaction status updates
- **✅ UPI ID validation** against known payment service providers
- **🔄 Automatic fallback** to manual mode when device integration unavailable

### **Accessibility Excellence**
- **🔊 Enhanced audio processing** with noise cancellation
- **📢 Clear voice feedback** for all user interactions  
- **🐌 Adjustable speech rates** for user comfort
- **💰 Large amount alerts** with special confirmation protocols
- **🔄 Error recovery guidance** when transactions fail
- **♿ Screen reader compatibility** for additional accessibility

### **Security Features**
- **🧠 Memory isolation protocols** with automatic sensitive data clearing
- **⏰ Session timeout management** with configurable time limits
- **📋 Comprehensive audit logging** for security compliance
- **🔐 PIN protection guarantee** - never handles or requests UPI PINs
- **💰 Smart amount verification** with threshold-based confirmations
- **🛡️ Real-time fraud detection** patterns and alerts

---

## 🌟 **Future Roadmap**

### **Multilingual Support**
- **🇮🇳 Hindi voice commands** and responses
- **Regional language support** - Tamil, Telugu, Bengali
- **🗣️ Accent adaptation** for better recognition

### **Enhanced Features**
- **📄 Bill payment assistance** - Utility bills, mobile recharges
- **📱 QR code reading** with voice-guided scanning
- **📊 Transaction history** with voice-accessible reports
- **🚨 Enhanced fraud detection** with AI-powered monitoring

### **Platform Expansion**
- **🍎 iOS device integration** with Shortcuts and Siri
- **💻 Web browser extension** for online payments
- **⌚ Smartwatch compatibility** for quick transactions

---

## 🤝 **Contributing**

We welcome contributions focused on accessibility and security improvements:

1. **🍴 Fork the repository** and create a feature branch
2. **🔍 Focus on UPI/accessibility** improvements in your contributions
3. **🛡️ Maintain security standards** - never compromise on financial security
4. **🧪 Add comprehensive tests** for all payment flows and edge cases
5. **📝 Submit detailed pull requests** with thorough security review

### **Contribution Areas**
- **♿ Accessibility enhancements** for disabled users
- **🔒 Security improvements** and vulnerability fixes
- **🌐 Internationalization** and localization support
- **📱 Device integration** for additional platforms
- **🧪 Test coverage** expansion for better reliability

---

## 📄 **License**

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 **Creator**

**Created by [Abhinav Barthwal](https://github.com/AbhinavBarthwal)**

*A UPI payment assistant designed to make digital payments accessible to everyone, especially visually impaired and elderly users.*

**Connect:**
- 🐙 **GitHub**: [AbhinavBarthwal](https://github.com/AbhinavBarthwal)
- 💼 **LinkedIn**: [Abhinav Barthwal](https://linkedin.com/in/abhinav-barthwal)

---

## 🙏 **Acknowledgments**

- **🎤 LiveKit** - Real-time communication infrastructure enabling voice interactions
- **🧠 Google Gemini AI** - Advanced natural language processing capabilities
- **💳 UPI Ecosystem** - Unified Payments Interface enabling digital payments in India
- **♿ Accessibility Community** - Guidance and feedback on inclusive design principles
- **🌍 Financial Inclusion Vision** - Working towards accessible digital payments for all

---

## 📊 **Project Stats**

- **🎯 Primary Focus**: UPI Payment Accessibility
- **👥 Target Users**: Visually impaired and elderly users
- **🔒 Security Level**: Enterprise-grade with PIN protection
- **📱 Platform Support**: Android (iOS planned)
- **🌐 Languages**: English (Hindi and regional languages planned)
- **♿ Accessibility**: WCAG 2.1 AA compliant design principles

---

*"Making digital payments accessible to everyone, one voice command at a time."* 🎩d UPI Transactions

**VoiceUPI** is a secure and accessible wrapper that allows **elderly users** to perform UPI transactions using only **voice and fingerprint**. No typing. No app-hopping confusion. Just speak, confirm, and pay.

This project acts as a **voice-first payment layer** that connects with any UPI app (PhonePe, GPay, BHIM) and automates the user’s journey all the way to the final UPI page — with **security confirmations** and **biometric UPI PIN entry**.

---

## 🧠 How It Works (Flow)

1. **User speaks**:  
   > "Pay ₹500 electricity bill"  
   > or  
   > "Send ₹2000 to Ramesh"

2. **VoiceUPI parses the intent**, identifies:
   - Action (send/pay)
   - Amount
   - Recipient or bill type

3. **Assistant confirms**:  
   > “You are sending ₹500 to the Electricity Board. Should I continue?”

4. **User says**: “Yes” ✅

5. **VoiceUPI opens the target UPI app** using **deep link**:
   - UPI ID prefilled
   - Amount set
   - Notes optional

6. **Fingerprint matched** (optional):
   - If correct: auto-enter UPI PIN 🔐
   - If not: fallback to manual entry

---

## 🔑 Core Features

### 🎤 1. Voice Command Recognition
- Converts speech to intent (amount + recipient or biller)
- Supports regional languages (Hindi, Tamil, Bengali, more)

### 🧠 2. Command Parsing & Intent Extraction
- Detects:
  - Transaction type (send/pay/bill)
  - Amount
  - Target UPI ID (from verified list or shopping app)

### 🗣️ 3. Spoken Confirmation
- Speaks out transaction details to avoid mistakes
- Confirms with a simple “Yes” or “No”

### 🔗 4. UPI App Deep Linking
- Opens apps like PhonePe/GPay/BHIM with pre-filled details:
```kotlin
val uri = Uri.parse("upi://pay?pa=powerboard@upi&pn=ElectricityBoard&am=500")
val intent = Intent(Intent.ACTION_VIEW, uri)
startActivity(intent)
