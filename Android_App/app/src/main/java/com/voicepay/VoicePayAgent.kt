package com.voicepay

import android.content.Context
import android.util.Log
import kotlinx.coroutines.*
import java.text.SimpleDateFormat
import java.util.*
import java.util.regex.Pattern

class VoicePayAgent(
    private val context: Context,
    private val upiManager: UPIManager
) {
    
    companion object {
        private const val TAG = "VoicePayAgent"
        private const val MAX_TRANSACTION_AMOUNT = 50000.0
        private const val SESSION_TIMEOUT_MS = 3600000L // 1 hour
    }
    
    private val memoryManager = VoicePayMemoryManager()
    private var sessionStartTime = System.currentTimeMillis()
    
    // Transaction state
    private var currentTransaction: TransactionState? = null
    
    data class TransactionState(
        val amount: Double? = null,
        val recipientUpiId: String? = null,
        val recipientName: String? = null,
        val description: String? = null,
        val confirmationPending: Boolean = false
    )
    
    suspend fun processCommand(command: String): String {
        return withContext(Dispatchers.IO) {
            try {
                // Check session timeout
                if (System.currentTimeMillis() - sessionStartTime > SESSION_TIMEOUT_MS) {
                    resetSession()
                    return@withContext "Your session has expired for security. Please start fresh."
                }
                
                val normalizedCommand = command.lowercase().trim()
                Log.d(TAG, "Processing command: $normalizedCommand")
                
                // Handle different types of commands
                when {
                    isGreeting(normalizedCommand) -> handleGreeting()
                    isPaymentCommand(normalizedCommand) -> handlePaymentCommand(normalizedCommand)
                    isConfirmationCommand(normalizedCommand) -> handleConfirmation(normalizedCommand)
                    isCancelCommand(normalizedCommand) -> handleCancel()
                    isBalanceInquiry(normalizedCommand) -> handleBalanceInquiry()
                    isHelpCommand(normalizedCommand) -> handleHelp()
                    isUpiAppsCommand(normalizedCommand) -> handleUpiAppsCheck()
                    else -> handleUnknownCommand(normalizedCommand)
                }
                
            } catch (e: Exception) {
                Log.e(TAG, "Error processing command", e)
                "I apologize, but I encountered an error processing your request. Please try again."
            }
        }
    }
    
    private fun isGreeting(command: String): Boolean {
        val greetingPatterns = listOf("hello", "hi", "hey", "good morning", "good afternoon", "good evening")
        return greetingPatterns.any { command.contains(it) }
    }
    
    private fun isPaymentCommand(command: String): Boolean {
        val paymentPatterns = listOf("pay", "send", "transfer", "give", "payment")
        return paymentPatterns.any { command.contains(it) }
    }
    
    private fun isConfirmationCommand(command: String): Boolean {
        val confirmPatterns = listOf("yes", "confirm", "proceed", "go ahead", "correct", "right")
        val denyPatterns = listOf("no", "cancel", "stop", "wrong", "incorrect")
        return confirmPatterns.any { command.contains(it) } || denyPatterns.any { command.contains(it) }
    }
    
    private fun isCancelCommand(command: String): Boolean {
        val cancelPatterns = listOf("cancel", "stop", "abort", "nevermind", "forget it")
        return cancelPatterns.any { command.contains(it) }
    }
    
    private fun isBalanceInquiry(command: String): Boolean {
        val balancePatterns = listOf("balance", "check balance", "how much", "account balance")
        return balancePatterns.any { command.contains(it) }
    }
    
    private fun isHelpCommand(command: String): Boolean {
        val helpPatterns = listOf("help", "what can you do", "commands", "how to")
        return helpPatterns.any { command.contains(it) }
    }
    
    private fun isUpiAppsCommand(command: String): Boolean {
        val upiPatterns = listOf("upi apps", "payment apps", "installed apps", "available apps")
        return upiPatterns.any { command.contains(it) }
    }
    
    private fun handleGreeting(): String {
        val greetings = listOf(
            "Good day! I'm your VoicePay butler, ready to assist with your UPI payments.",
            "Hello there! How may I help you with your payments today?",
            "Greetings! I'm here to make your UPI transactions simple and secure."
        )
        return greetings.random()
    }
    
    private suspend fun handlePaymentCommand(command: String): String {
        // Extract payment details from command
        val amount = extractAmount(command)
        val upiId = extractUpiId(command)
        val description = extractDescription(command)
        
        // Validate amount
        if (amount != null && amount > MAX_TRANSACTION_AMOUNT) {
            return "I'm afraid I cannot process payments over ₹${MAX_TRANSACTION_AMOUNT.toInt()} for security reasons. Please contact your bank for larger transactions."
        }
        
        // Build transaction state
        currentTransaction = TransactionState(
            amount = amount,
            recipientUpiId = upiId,
            description = description
        )
        
        return when {
            amount == null -> "I didn't catch the amount. Please tell me how much you'd like to pay."
            upiId == null -> "I need the recipient's UPI ID. Please provide the UPI ID for the payment."
            else -> {
                // Store sensitive data in memory manager
                memoryManager.storeSensitiveData("transaction_${System.currentTimeMillis()}", currentTransaction!!)
                
                val confirmationMessage = buildConfirmationMessage(amount, upiId, description)
                currentTransaction = currentTransaction?.copy(confirmationPending = true)
                confirmationMessage
            }
        }
    }
    
    private suspend fun handleConfirmation(command: String): String {
        val transaction = currentTransaction
        
        if (transaction == null || !transaction.confirmationPending) {
            return "There's no pending transaction to confirm. Please start a new payment."
        }
        
        return if (command.contains("yes") || command.contains("confirm") || command.contains("proceed")) {
            // Execute the payment
            executePayment(transaction)
        } else {
            // Cancel transaction
            currentTransaction = null
            "Transaction cancelled. Is there anything else I can help you with?"
        }
    }
    
    private fun handleCancel(): String {
        currentTransaction = null
        memoryManager.clearSensitiveData()
        return "Transaction cancelled. How else may I assist you today?"
    }
    
    private suspend fun handleBalanceInquiry(): String {
        // Check if UPI apps are available
        val availableApps = upiManager.getInstalledUpiApps()
        
        return if (availableApps.isNotEmpty()) {
            "I can help you check your balance. Please open your preferred UPI app to view your account balance. Would you like me to open ${availableApps.first().appName} for you?"
        } else {
            "To check your balance, you'll need to install a UPI app like PhonePe, Google Pay, or Paytm. Would you like help installing one?"
        }
    }
    
    private fun handleHelp(): String {
        return """
            I can help you with UPI payments! Here's what you can say:
            
            • "Pay 500 rupees to john@paytm" - Make a payment
            • "Send 1000 to 9876543210@ybl" - Transfer money
            • "Check my balance" - Balance inquiry
            • "What UPI apps do I have" - Check installed apps
            • "Cancel" - Cancel current transaction
            
            I'm designed to be secure and user-friendly for all ages.
        """.trimIndent()
    }
    
    private suspend fun handleUpiAppsCheck(): String {
        val installedApps = upiManager.getInstalledUpiApps()
        
        return if (installedApps.isNotEmpty()) {
            val appList = installedApps.joinToString(", ") { it.appName }
            "You have these UPI apps installed: $appList. All are ready for payments!"
        } else {
            "You don't have any UPI apps installed. I recommend installing PhonePe, Google Pay, or Paytm to make payments."
        }
    }
    
    private fun handleUnknownCommand(command: String): String {
        return "I'm not sure I understood that. I can help with UPI payments, balance checks, and app management. Say 'help' for more options."
    }
    
    private suspend fun executePayment(transaction: TransactionState): String {
        return try {
            val amount = transaction.amount ?: return "Payment failed: Missing amount"
            val upiId = transaction.recipientUpiId ?: return "Payment failed: Missing UPI ID"
            
            // Get available UPI apps
            val availableApps = upiManager.getInstalledUpiApps()
            
            if (availableApps.isEmpty()) {
                return "No UPI apps found. Please install PhonePe, Google Pay, or another UPI app to make payments."
            }
            
            // Use the first available app (can be enhanced to let user choose)
            val selectedApp = availableApps.first()
            
            // Create payment intent
            val success = upiManager.initiatePayment(
                upiId = upiId,
                amount = amount,
                description = transaction.description ?: "VoicePay Transaction",
                appPackage = selectedApp.packageName
            )
            
            currentTransaction = null // Clear transaction
            
            if (success) {
                "Payment of ₹${amount.toInt()} initiated through ${selectedApp.appName}. Please complete the transaction in the app."
            } else {
                "Payment initiation failed. Please try again or check your UPI app."
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "Payment execution failed", e)
            "Payment failed due to an error. Please try again."
        }
    }
    
    private fun extractAmount(command: String): Double? {
        // Patterns to match amounts
        val patterns = listOf(
            Pattern.compile("(\\d+(?:\\.\\d{2})?)\\s*(?:rupees?|rs?\\.?|₹)"),
            Pattern.compile("(?:rupees?|rs?\\.?|₹)\\s*(\\d+(?:\\.\\d{2})?)"),
            Pattern.compile("(\\d+(?:\\.\\d{2})?)"),
        )
        
        for (pattern in patterns) {
            val matcher = pattern.matcher(command.lowercase())
            if (matcher.find()) {
                return matcher.group(1)?.toDoubleOrNull()
            }
        }
        
        return null
    }
    
    private fun extractUpiId(command: String): String? {
        // Pattern to match UPI IDs
        val upiPattern = Pattern.compile("([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+)")
        val matcher = upiPattern.matcher(command)
        
        if (matcher.find()) {
            return matcher.group(1)
        }
        
        // Also check for phone numbers (assuming @ybl or @paytm)
        val phonePattern = Pattern.compile("(\\d{10})")
        val phoneMatcher = phonePattern.matcher(command)
        
        if (phoneMatcher.find()) {
            val phone = phoneMatcher.group(1)
            // Default to @ybl for phone numbers
            return "$phone@ybl"
        }
        
        return null
    }
    
    private fun extractDescription(command: String): String? {
        val descPatterns = listOf("for ", "description ", "note ", "memo ")
        
        for (pattern in descPatterns) {
            val index = command.lowercase().indexOf(pattern)
            if (index != -1) {
                val description = command.substring(index + pattern.length).trim()
                if (description.isNotEmpty()) {
                    return description
                }
            }
        }
        
        return null
    }
    
    private fun buildConfirmationMessage(amount: Double, upiId: String, description: String?): String {
        val amountStr = "₹${amount.toInt()}"
        val descStr = if (description.isNullOrBlank()) "" else " for $description"
        
        return "I'll send $amountStr to $upiId$descStr. Shall I proceed with this payment? Say 'yes' to confirm or 'no' to cancel."
    }
    
    private fun resetSession() {
        sessionStartTime = System.currentTimeMillis()
        currentTransaction = null
        memoryManager.clearSensitiveData()
    }
    
    fun cleanup() {
        memoryManager.clearSensitiveData()
    }
}
