VEUT - Voice enabled upi transactions

VoiceUPI is an accessibility and security-focused wrapper built to assist **elderly and low-literacy users** in performing safe UPI transactions using **voice commands** and **gesture/biometric confirmations**. It connects to existing UPI apps like BHIM, PhonePe, or Paytm — acting as a trusted, voice-first assistant layer.

---

## 🧩 Features

### 1️⃣ Voice Capture
- Multilingual voice input using Android’s SpeechRecognizer API
- Continuous or push-to-talk mode
- Converts commands like:  
  `"Send ₹1000 to Ramesh"`

### 2️⃣ Intent Extraction
- Lightweight NLP to parse `amount`, `recipient`, and `action`
- Supports:
  - `send_money`
  - `check_balance`
  - `report_fraud`
  - `cancel_transaction`

### 3️⃣ Assistant Replies
- Text-to-speech feedback in user's regional language
- Examples:
  - `"You are sending ₹1000 to Ramesh. Tap and hold to confirm."`
  - `"This contact is not verified. Transaction blocked for safety."`

### 4️⃣ Biometric + Gesture Confirmation
- Uses device fingerprint API or screen tap-and-hold gesture to approve transactions
- Protects against accidental or fraudulent actions

### 5️⃣ SOS Safety Layer
- If amount > ₹X (e.g. ₹5000), alert family via SMS or push notification
- VoiceUPI pauses and says:
  > `"This is a high-value payment. Shall I alert your family?"`

### 6️⃣ Frontend
- Built in Kotlin (for Android)
- Large buttons, minimal text, and full voice guidance
- Dark mode and accessibility font support

### 7️⃣ Integration with UPI Apps
- Works with:
  - BHIM, PhonePe, GPay, Paytm (via deep links)
- Example:
```kotlin
val intent = Intent(Intent.ACTION_VIEW)
intent.data = Uri.parse("upi://pay?pa=ram@upi&pn=Ramesh&am=1000")
startActivity(intent)
