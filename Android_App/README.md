# VoicePay Android App

A voice-activated UPI payment assistant designed as a British butler for elderly and visually impaired users.

## Features

- **Voice Recognition**: Natural speech processing for payment commands
- **UPI Integration**: Works with PhonePe, Google Pay, Paytm, and other UPI apps
- **British Butler Persona**: Polite, clear, and helpful voice responses
- **Accessibility First**: Large buttons, clear speech, simplified interface
- **Security**: Automatic session cleanup, secure data handling
- **Real-time Android Integration**: Direct UPI app launching

## Voice Commands

### Payment Commands
- "Pay 500 rupees to john@paytm"
- "Send 1000 to 9876543210@ybl"
- "Transfer 250 to amit@phonepe"

### Information Commands
- "Check my UPI apps"
- "What payment apps do I have"
- "Help me with payments"

### Control Commands
- "Cancel transaction"
- "Stop listening"

## Technical Architecture

### Core Components

1. **MainActivity**: Main UI with voice input controls
2. **VoicePayAgent**: AI processing engine for command interpretation
3. **UPIManager**: Handles UPI app detection and payment initiation
4. **VoicePayMemoryManager**: Secure memory management with auto-cleanup
5. **VoicePayViewModel**: MVVM architecture for UI state management

### Key Features

- **Speech Recognition**: Android's built-in speech recognition
- **Text-to-Speech**: British accent TTS with adjustable speed
- **UPI Intent System**: Direct integration with UPI apps
- **Security**: 1-hour session timeout, sensitive data auto-cleanup
- **Error Handling**: Graceful fallbacks and user-friendly error messages

## Permissions Required

- `RECORD_AUDIO`: For voice command input
- `INTERNET`: For potential API calls
- `QUERY_ALL_PACKAGES`: To detect installed UPI apps

## Installation

1. Open Android Studio
2. Import the project
3. Sync Gradle files
4. Run on Android device (API 24+)

## Usage

1. Launch VoicePay app
2. Grant microphone permission
3. Tap "Start Listening"
4. Speak your payment command clearly
5. Confirm payment details when prompted
6. Complete transaction in your UPI app

## Supported UPI Apps

- PhonePe
- Google Pay
- Paytm
- BHIM UPI
- Amazon Pay
- MobiKwik
- Freecharge
- Airtel Thanks
- iMobile Pay
- Yono SBI

## Security Features

- Automatic session timeout (1 hour)
- Sensitive data auto-cleanup
- No permanent storage of payment details
- Secure UPI intent system
- Memory isolation for transactions

## Accessibility

- Large, high-contrast buttons
- Clear voice feedback
- Slow, clear speech output
- Simple, uncluttered interface
- Voice-first interaction model

## Development

### Building
```bash
./gradlew assembleDebug
```

### Testing
```bash
./gradlew test
```

### Running
```bash
./gradlew installDebug
```

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MainActivity  │◄──►│ VoicePayViewModel│◄──►│  VoicePayAgent  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Speech Services │    │   LiveData       │    │   UPIManager    │
│ - Recognition   │    │   - Status       │    │   - App Detection│
│ - TTS           │    │   - Responses    │    │   - Payment Init │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
                                               ┌─────────────────┐
                                               │VoicePayMemoryMgr│
                                               │ - Secure Storage│
                                               │ - Auto Cleanup  │
                                               └─────────────────┘
```

## Conversion from Python

This Android app is converted from the Python VoiceAssistant with the following mappings:

- `agent.py` → `VoicePayAgent.kt` + `VoicePayViewModel.kt`
- `tools.py` → `UPIManager.kt`
- `memory_manager.py` → `VoicePayMemoryManager.kt`
- `config.py` → Embedded in Kotlin classes
- `prompts.py` → British butler responses in VoicePayAgent

## License

This project is designed for educational and accessibility purposes.
