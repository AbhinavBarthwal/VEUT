VEUT - Voice Enabled UPI Transactions

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
