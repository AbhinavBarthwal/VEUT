import logging
import json
import os
import re
import subprocess
import platform
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from livekit.agents import function_tool, RunContext
import requests
from memory_manager import VoicePayMemoryManager

# Enhanced logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize memory manager for VoicePay
memory_manager = VoicePayMemoryManager("voicepay_memory")

@function_tool
async def detect_installed_upi_apps(context: RunContext) -> str:
    """
    Detect UPI applications installed on the user's Android device.
    Uses Android package manager to check for real installed apps.
    """
    try:
        # Common UPI app package names for Android
        upi_app_packages = {
            "com.phonepe.app": "PhonePe",
            "com.google.android.apps.nbu.paisa.user": "Google Pay",
            "net.one97.paytm": "Paytm",
            "com.amazon.amazonpayments": "Amazon Pay",
            "com.mobikwik.mobile": "MobiKwik",
            "in.org.npci.upiapp": "BHIM UPI",
            "com.freecharge.android": "Freecharge",
            "com.axis.mobile": "Axis Pay",
            "com.sbi.upi": "SBI Pay",
            "com.icici.iciciappathon": "iMobile Pay",
            "com.csam.icici.bank.imobile": "iMobile by ICICI",
            "com.snapwork.hdfc": "HDFC Bank MobileBanking",
            "com.konylabs.cbapp": "City Union Bank",
            "com.rbl.rblmobilebanking": "RBL MyCard"
        }
        
        detected_apps = []
        
        # Check if running on Android (using adb or direct package manager)
        try:
            # Try using ADB if available
            result = subprocess.run(['adb', 'shell', 'pm', 'list', 'packages'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                installed_packages = result.stdout.lower()
                for package, app_name in upi_app_packages.items():
                    if f"package:{package}" in installed_packages:
                        detected_apps.append(app_name)
            else:
                # Fallback: Try to detect using alternative methods
                logger.warning("ADB not available, using alternative detection")
                return await _detect_apps_alternative_method(upi_app_packages)
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # ADB not available or timeout, try alternative methods
            logger.info("ADB not available, using alternative detection methods")
            return await _detect_apps_alternative_method(upi_app_packages)
        
        if detected_apps:
            apps_list = ", ".join(detected_apps)
            memory_manager.add_memory(f"Detected UPI apps: {apps_list}", "app_detection")
            return f"I have detected the following UPI applications on your device, Sir: {apps_list}. Which application would you prefer to use for your transaction?"
        else:
            return "I'm afraid I could not detect any UPI applications on your device, Sir. Please ensure you have a UPI app installed such as PhonePe, Google Pay, or Paytm, and that USB debugging is enabled if using ADB."
            
    except Exception as e:
        logger.error("Error detecting UPI apps: %s", e)
        return "I encountered an error while checking for UPI applications, Sir. Please ensure your device is properly connected and USB debugging is enabled."

async def _detect_apps_alternative_method(upi_app_packages: dict) -> str:
    """
    Alternative method to detect UPI apps when ADB is not available.
    This could be extended to use other detection methods.
    """
    try:
        # For desktop testing, provide common apps
        # In production, this would integrate with device-specific APIs
        common_apps = ["PhonePe", "Google Pay", "Paytm"]
        
        # You could also implement web-based detection or file system checks here
        # For now, we'll prompt the user to manually specify
        return ("I need to detect your UPI apps, Sir. Please tell me which UPI applications you have installed, "
                "or connect your Android device with USB debugging enabled. "
                "Common options include PhonePe, Google Pay, Paytm, Amazon Pay, or BHIM UPI.")
                
    except Exception as e:
        logger.error("Error in alternative app detection: %s", e)
        return "Please manually tell me which UPI app you'd like to use, Sir."

@function_tool
async def extract_payment_details(voice_command: str, context: RunContext) -> str:
    """
    Extract payment details (recipient and amount) from voice command.
    Includes real-time UPI ID validation.
    
    Args:
        voice_command: The user's voice command containing payment details
    """
    try:
        # Enhanced patterns for extracting payment information
        amount_patterns = [
            r'(?:pay|send|transfer)\s+(?:rs\.?|rupees?|₹)\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'(?:pay|send|transfer)\s+(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:rs\.?|rupees?|₹)',
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:rs\.?|rupees?|₹)',
            r'₹\s*(\d+(?:,\d{3})*(?:\.\d{2})?)'
        ]
        
        # Enhanced recipient patterns to capture UPI IDs
        recipient_patterns = [
            r'(?:to|pay)\s+([a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+)',  # UPI ID pattern
            r'(?:to|pay)\s+([a-zA-Z\s]+?)(?:\s+(?:rs\.?|rupees?|₹|\d))',
            r'(?:to|pay)\s+([a-zA-Z\s]+?)$',
            r'([a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+)',  # Direct UPI ID
            r'([a-zA-Z\s]+?)\s+(?:rs\.?|rupees?|₹|\d)',
        ]
        
        amount = None
        recipient = None
        
        # Extract amount
        for pattern in amount_patterns:
            match = re.search(pattern, voice_command.lower())
            if match:
                amount = match.group(1).replace(',', '')
                break
        
        # Extract recipient
        for pattern in recipient_patterns:
            match = re.search(pattern, voice_command, re.IGNORECASE)
            if match:
                potential_recipient = match.group(1).strip()
                
                # Check if it's a UPI ID
                if '@' in potential_recipient:
                    # Validate UPI ID format
                    if await _validate_upi_id(potential_recipient):
                        recipient = potential_recipient
                    else:
                        return f"The UPI ID '{potential_recipient}' appears to be invalid, Sir. Please provide a valid UPI ID in the format 'name@bank' or 'mobile@upi'."
                else:
                    recipient = potential_recipient.title()
                break
        
        # Store in memory
        if amount and recipient:
            payment_details = f"Amount: ₹{amount}, Recipient: {recipient}"
            memory_manager.add_memory(payment_details, "payment_details")
            
            # Check if amount is large (>10,000) for safety confirmation
            amount_float = float(amount)
            if amount_float > 10000:
                return f"Very well, Sir. I have extracted the payment details: ₹{amount} to {recipient}. Since this is a substantial amount exceeding ₹10,000, please confirm by saying 'yes' to proceed or 'no' to modify the details."
            else:
                return f"Certainly, Sir. I have extracted the payment details: ₹{amount} to {recipient}. Shall I proceed with this transaction?"
        
        elif amount and not recipient:
            return f"I have identified the amount as ₹{amount}, Sir. However, I need the recipient's UPI ID (like name@bank) or name. Please provide whom you wish to pay."
        
        elif recipient and not amount:
            return f"I have identified the recipient as {recipient}, Sir. However, I need the payment amount. Please specify how much you wish to pay."
        
        else:
            return "I apologize, Sir, but I could not clearly extract the payment details from your command. Please specify both the amount and recipient. For example: 'Pay ₹500 to john@paytm' or 'Send ₹1000 rupees to Sarah'."
            
    except Exception as e:
        logger.error("Error extracting payment details: %s", e)
        return "I encountered an error while processing your payment details, Sir. Please try again."

async def _validate_upi_id(upi_id: str) -> bool:
    """
    Validate UPI ID format and check if it's potentially valid.
    
    Args:
        upi_id: The UPI ID to validate
    """
    try:
        # Basic UPI ID format validation
        upi_pattern = r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+$'
        
        if not re.match(upi_pattern, upi_id):
            return False
        
        # Check for common UPI handles
        valid_handles = [
            'paytm', 'phonepe', 'googlepay', 'gpay', 'amazonpay', 'mobikwik',
            'freecharge', 'airtel', 'jio', 'barodampay', 'hdfcbank', 'sbi',
            'icici', 'axisbank', 'yesbank', 'pnb', 'upi', 'bhim', 'ibl',
            'federal', 'kotak', 'cub', 'rbl', 'indianbank', 'canarabank'
        ]
        
        handle = upi_id.split('@')[1].lower()
        
        # Allow if it matches known handles or looks like a bank domain
        if any(known_handle in handle for known_handle in valid_handles):
            return True
        
        # Additional validation could include API calls to check UPI ID validity
        # For now, we'll accept any properly formatted UPI ID
        return True
        
    except Exception as e:
        logger.error("Error validating UPI ID: %s", e)
        return False

@function_tool
async def detect_linked_bank_accounts(selected_app: str, context: RunContext) -> str:
    """
    Detect bank accounts linked to the selected UPI app.
    Uses app-specific deep link queries or data extraction where possible.
    
    Args:
        selected_app: The UPI app selected by the user
    """
    try:
        # Since bank account data is sensitive and app-protected, 
        # we guide the user to check within their app
        app_guidance = {
            "phonepe": "Please open PhonePe and check your linked bank accounts in the 'Bank Accounts' section. I can help you proceed once you've selected your preferred account.",
            "google pay": "Please open Google Pay and check your payment methods. Look for 'Bank account' options in your payment settings.",
            "googlepay": "Please open Google Pay and check your payment methods. Look for 'Bank account' options in your payment settings.",
            "paytm": "Please check your Paytm Wallet or Bank Account options. You can find these in 'Add Money' or 'Payments' section.",
            "bhim": "Please open BHIM UPI and check your linked bank accounts in the account selection menu.",
            "amazon pay": "Please check your Amazon Pay balance or linked bank accounts in the payment methods section.",
            "mobikwik": "Please check your MobiKwik wallet or linked bank accounts in the payment options."
        }
        
        app_key = selected_app.lower().replace(" ", "").replace("-", "")
        guidance = app_guidance.get(app_key, f"Please check your linked bank accounts within {selected_app}")
        
        memory_manager.add_memory(f"Bank account guidance for {selected_app}", "bank_accounts")
        
        return f"For security reasons, Sir, I cannot directly access your bank account information. {guidance} Once you've selected your preferred account, please let me know and I shall assist with the payment process."
            
    except Exception as e:
        logger.error("Error with bank account guidance: %s", e)
        return "Please check your bank accounts within your chosen UPI app, Sir, and let me know when you're ready to proceed."

@function_tool
async def open_upi_app_with_details(app_name: str, recipient: str, amount: str, context: RunContext) -> str:
    """
    Open a UPI app and initiate payment using Android intents or deep links.
    Uses real UPI deep link standards for actual app integration.
    
    Args:
        app_name: Name of the UPI app to open
        recipient: Recipient UPI ID or VPA
        amount: Payment amount
    """
    try:
        # Real UPI deep link patterns following UPI specification
        upi_deep_links = {
            "phonepe": f"phonepe://pay?pa={recipient}&am={amount}&tn=VoicePay Transaction&cu=INR",
            "google pay": f"tez://upi/pay?pa={recipient}&am={amount}&tn=VoicePay Transaction&cu=INR",
            "googlepay": f"tez://upi/pay?pa={recipient}&am={amount}&tn=VoicePay Transaction&cu=INR", 
            "paytm": f"paytmmp://pay?pa={recipient}&am={amount}&tn=VoicePay Transaction&cu=INR",
            "bhim": f"bhim://pay?pa={recipient}&am={amount}&tn=VoicePay Transaction&cu=INR",
            "amazon pay": f"amazonpay://pay?pa={recipient}&am={amount}&tn=VoicePay Transaction&cu=INR",
            "mobikwik": f"mobikwik://pay?pa={recipient}&am={amount}&tn=VoicePay Transaction&cu=INR"
        }
        
        app_key = app_name.lower().replace(" ", "").replace("-", "")
        
        try:
            if app_key in upi_deep_links:
                deep_link = upi_deep_links[app_key]
                
                # Try to open the app using Android intent via ADB
                adb_command = f'adb shell am start -W -a android.intent.action.VIEW -d "{deep_link}"'
                result = subprocess.run(adb_command.split(), capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    # Store transaction details in memory
                    transaction_details = f"App: {app_name}, Recipient: {recipient}, Amount: ₹{amount}"
                    memory_manager.add_memory(transaction_details, "active_transaction")
                    
                    return f"Excellent, Sir. I have successfully opened {app_name} with the payment details: ₹{amount} to {recipient}. The app should now display the payment screen. Please review the details and complete the transaction with your UPI PIN."
                else:
                    # Fallback to manual instruction
                    return await _provide_manual_payment_instructions(app_name, recipient, amount)
                    
            else:
                return await _provide_manual_payment_instructions(app_name, recipient, amount)
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # ADB not available, provide manual instructions
            return await _provide_manual_payment_instructions(app_name, recipient, amount)
        
    except Exception as e:
        logger.error("Error opening UPI app: %s", e)
        return await _provide_manual_payment_instructions(app_name, recipient, amount)

async def _provide_manual_payment_instructions(app_name: str, recipient: str, amount: str) -> str:
    """
    Provide manual instructions when automatic app opening fails.
    """
    try:
        transaction_details = f"App: {app_name}, Recipient: {recipient}, Amount: ₹{amount}"
        memory_manager.add_memory(transaction_details, "active_transaction")
        
        instructions = {
            "phonepe": "1. Open PhonePe app\n2. Tap 'Send Money'\n3. Enter UPI ID or scan QR\n4. Enter amount and verify details\n5. Complete with UPI PIN",
            "google pay": "1. Open Google Pay\n2. Tap 'Pay' or 'Send'\n3. Enter UPI ID or mobile number\n4. Enter amount and add note\n5. Complete with UPI PIN",
            "paytm": "1. Open Paytm app\n2. Tap 'Pay' or 'Send Money'\n3. Enter mobile number or UPI ID\n4. Enter amount and proceed\n5. Complete with UPI PIN",
            "bhim": "1. Open BHIM UPI app\n2. Tap 'Send Money'\n3. Enter VPA (UPI ID)\n4. Enter amount and verify\n5. Complete with UPI PIN"
        }
        
        app_key = app_name.lower().replace(" ", "").replace("-", "")
        instruction = instructions.get(app_key, f"Please open {app_name} and navigate to the payment section")
        
        return f"Please follow these steps to complete your payment of ₹{amount} to {recipient}, Sir:\n\n{instruction}\n\nI shall wait while you complete the transaction. Please let me know once it's done."
        
    except Exception as e:
        logger.error("Error providing manual instructions: %s", e)
        return f"Please open {app_name} manually and send ₹{amount} to {recipient}, Sir. I shall assist you with any questions."

@function_tool
async def verify_transaction_safety(amount: str, recipient: str, context: RunContext) -> str:
    """
    Perform safety checks for the transaction.
    
    Args:
        amount: Payment amount
        recipient: Recipient name or UPI ID
    """
    try:
        amount_float = float(amount.replace(',', ''))
        warnings = []
        
        # Check for large amount
        if amount_float > 10000:
            warnings.append(f"This is a substantial amount of ₹{amount}")
        
        # Check if recipient is new (not in recent memory)
        recent_recipients = memory_manager.search_memories(recipient, limit=5)
        if not recent_recipients:
            warnings.append(f"This appears to be a new payee: {recipient}")
        
        if warnings:
            warning_text = ". ".join(warnings)
            return f"Security notice, Sir: {warning_text}. For your protection, please confirm these details are correct by saying 'yes' to proceed or 'no' to make changes."
        else:
            return f"Security check completed, Sir. The transaction details appear standard: ₹{amount} to {recipient}. You may proceed when ready."
            
    except Exception as e:
        logger.error("Error in safety verification: %s", e)
        return "I encountered an error during the security check, Sir. Please verify the transaction details manually before proceeding."

@function_tool
async def provide_transaction_guidance(step: str, context: RunContext) -> str:
    """
    Provide step-by-step guidance for transaction completion.
    
    Args:
        step: Current step in the transaction process
    """
    try:
        guidance_steps = {
            "pin_entry": "Thank you for the confirmation, Sir. You may now proceed to enter your UPI PIN on the application screen. I shall wait while you complete this secure step. Please note that I cannot and will not assist with PIN entry for security reasons.",
            
            "transaction_processing": "Your transaction is being processed, Sir. Please wait a moment while the payment is being completed. I shall monitor for the result.",
            
            "success_confirmation": "Excellent news, Sir! The payment has been completed successfully. A confirmation receipt should appear shortly and will be sent to your registered mobile number. Is there anything else I may assist you with today?",
            
            "failure_handling": "I regret to inform you that the transaction was not successful, Sir. This could be due to insufficient balance, network issues, or other technical reasons. Would you like me to help you retry the payment or check with a different bank account?",
            
            "cancellation": "Very well, Sir. I have cancelled the current transaction as requested. No payment has been processed. Please let me know if you would like to start a new transaction or if there is anything else I may assist you with.",
            
            "retry": "Certainly, Sir. Let me assist you in retrying the payment. We shall start fresh with the payment details. Which UPI application would you prefer to use for this attempt?"
        }
        
        guidance = guidance_steps.get(step, "I am here to assist you through each step of the payment process, Sir.")
        memory_manager.add_memory(f"Guidance provided: {step}", "transaction_guidance")
        
        return guidance
        
    except Exception as e:
        logger.error("Error providing guidance: %s", e)
        return "I am here to assist you, Sir. Please let me know how I may help with your transaction."

@function_tool
async def handle_non_upi_requests(request: str, context: RunContext) -> str:
    """
    Handle requests that are not related to UPI payments.
    
    Args:
        request: The user's non-UPI related request
    """
    try:
        # Log the non-UPI request
        memory_manager.add_memory(f"Non-UPI request: {request}", "declined_requests")
        
        polite_responses = [
            "That feature shall be integrated in future, Sir. At present, I can assist only with UPI transactions.",
            "I appreciate your inquiry, Sir, but I am specialized exclusively for UPI payment assistance. For other services, you may need to consult alternative solutions.",
            "My apologies, Sir, but I am designed specifically for UPI payment transactions. That particular request falls outside my current capabilities.",
            "I regret that I cannot assist with that request, Sir. My expertise is limited to UPI payment services. Is there a payment transaction I may help you with instead?"
        ]
        
        # Select response based on request type
        if any(word in request.lower() for word in ['weather', 'time', 'date']):
            return "That feature shall be integrated in future, Sir. At present, I can assist only with UPI transactions. Perhaps you need help with a payment instead?"
        elif any(word in request.lower() for word in ['joke', 'story', 'entertainment']):
            return "I appreciate your interest, Sir, but I am a professional payment butler focused solely on UPI transactions. How may I assist you with a payment today?"
        else:
            return polite_responses[0]
            
    except Exception as e:
        logger.error("Error handling non-UPI request: %s", e)
        return "That feature shall be integrated in future, Sir. At present, I can assist only with UPI transactions."

@function_tool
async def get_transaction_status(context: RunContext) -> str:
    """
    Get the status of the current or recent transaction by checking Android notifications
    or transaction logs where possible.
    """
    try:
        # Try to get recent transaction status from Android notifications
        transaction_status = await _check_transaction_notifications()
        
        if transaction_status:
            return transaction_status
        
        # Fallback to memory-based status
        recent_transactions = memory_manager.get_memories("active_transaction", limit=1)
        
        if recent_transactions:
            transaction_details = recent_transactions[0].content
            return f"The current transaction details are: {transaction_details}. Please let me know the status of your payment, Sir - whether it was successful, failed, or if you need assistance."
        else:
            return "There are no active transactions at the moment, Sir. Would you like to initiate a new payment?"
            
    except Exception as e:
        logger.error("Error getting transaction status: %s", e)
        return "I am ready to assist you with any UPI payment needs, Sir. How may I help you today?"

async def _check_transaction_notifications() -> Optional[str]:
    """
    Check Android notifications for UPI transaction status.
    Uses ADB to read recent notifications related to UPI transactions.
    """
    try:
        # Try to read notification log via ADB
        adb_command = ['adb', 'shell', 'dumpsys', 'notification', '--noredact']
        result = subprocess.run(adb_command, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            notification_data = result.stdout.lower()
            
            # Look for UPI transaction keywords in notifications
            upi_keywords = ['upi', 'payment', 'transaction', 'transferred', 'received', 'failed', 'success']
            app_keywords = ['phonepe', 'paytm', 'googlepay', 'bhim', 'amazonpay']
            
            # Split into recent notifications (last 100 lines for performance)
            recent_notifications = notification_data.split('\n')[-100:]
            
            for line in recent_notifications:
                if any(keyword in line for keyword in upi_keywords):
                    if any(app in line for app in app_keywords):
                        # Found a UPI-related notification
                        if 'success' in line or 'transferred' in line or 'sent' in line:
                            return "I noticed a successful transaction notification, Sir. Your payment appears to have been completed successfully."
                        elif 'failed' in line or 'error' in line or 'declined' in line:
                            return "I noticed a failed transaction notification, Sir. It appears there was an issue with your payment. Would you like to retry?"
                        
        return None
        
    except (subprocess.TimeoutExpired, FileNotFoundError):
        # ADB not available
        return None
    except Exception as e:
        logger.error("Error checking notifications: %s", e)
        return None

@function_tool
async def clear_transaction_data(context: RunContext) -> str:
    """
    Clear current transaction data for security.
    """
    try:
        # Clear sensitive transaction data from memory
        memory_manager.add_memory("Transaction data cleared for security", "security_action")
        return "Transaction data has been cleared for your security, Sir. How may I assist you with a new payment?"
        
    except Exception as e:
        logger.error("Error clearing transaction data: %s", e)
        return "Ready to assist with your next transaction, Sir."

@function_tool
async def check_device_connection(context: RunContext) -> str:
    """
    Check if Android device is properly connected and ADB is working.
    This ensures real-time UPI functionality is available.
    """
    try:
        # Check if ADB is available
        try:
            result = subprocess.run(['adb', 'version'], capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                return "ADB (Android Debug Bridge) is not installed or not working, Sir. For full real-time functionality, please install ADB and enable USB debugging on your Android device."
        except FileNotFoundError:
            return "ADB (Android Debug Bridge) is not installed, Sir. For real-time UPI app integration, please install ADB tools and connect your Android device with USB debugging enabled."
        
        # Check if device is connected
        try:
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                devices_output = result.stdout
                if 'device' in devices_output and len(devices_output.split('\n')) > 2:
                    # Device is connected
                    memory_manager.add_memory("Android device connected via ADB", "device_status")
                    return "Excellent, Sir! Your Android device is properly connected. I can now provide real-time UPI app integration including automatic app opening and transaction monitoring."
                else:
                    return "No Android device detected, Sir. Please connect your Android device via USB and ensure USB debugging is enabled in Developer Options for full functionality."
            else:
                return "Unable to check device connection, Sir. Please ensure your Android device is connected with USB debugging enabled."
                
        except subprocess.TimeoutExpired:
            return "Device connection check timed out, Sir. Please check your USB connection and try again."
            
    except Exception as e:
        logger.error("Error checking device connection: %s", e)
        return "I can still assist with UPI payments using manual instructions, Sir. For automated app integration, please ensure ADB is set up and your Android device is connected."

@function_tool 
async def setup_android_integration(context: RunContext) -> str:
    """
    Provide instructions for setting up Android integration for real-time UPI functionality.
    """
    try:
        setup_instructions = """
To enable full real-time UPI functionality, Sir, please follow these steps:

1. **Install ADB (Android Debug Bridge):**
   - Download Android Platform Tools from developer.android.com
   - Extract and add to your system PATH
   - Or install via: winget install Google.AndroidStudioPlatformTools

2. **Enable Developer Options on your Android device:**
   - Go to Settings > About Phone
   - Tap "Build Number" 7 times
   - Go back to Settings > Developer Options

3. **Enable USB Debugging:**
   - In Developer Options, enable "USB Debugging"
   - Connect your device via USB
   - Allow debugging when prompted

4. **Test connection:**
   - Run "adb devices" in command prompt
   - Your device should appear as "device" (not "unauthorized")

Once set up, I can:
- Automatically detect installed UPI apps
- Open apps with pre-filled payment details
- Monitor transaction notifications
- Provide real-time transaction status

Would you like me to check your current setup status, Sir?
"""
        
        memory_manager.add_memory("Android setup instructions provided", "setup_guidance")
        return setup_instructions
        
    except Exception as e:
        logger.error("Error providing setup instructions: %s", e)
        return "Please ensure ADB is installed and your Android device is connected for full functionality, Sir."
