package com.voicepay

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.launch

class VoicePayViewModel(application: Application) : AndroidViewModel(application) {
    
    private lateinit var voicePayAgent: VoicePayAgent
    private lateinit var upiManager: UPIManager
    private var isInitialized = false
    
    private val _statusMessage = MutableLiveData<String>()
    val statusMessage: LiveData<String> = _statusMessage
    
    private val _speechResponse = MutableLiveData<String>()
    val speechResponse: LiveData<String> = _speechResponse
    
    private val _isProcessing = MutableLiveData<Boolean>()
    val isProcessing: LiveData<Boolean> = _isProcessing
    
    private val _upiApps = MutableLiveData<List<UpiApp>>()
    val upiApps: LiveData<List<UpiApp>> = _upiApps
    
    init {
        initialize()
    }
    
    private fun initialize() {
        if (!isInitialized) {
            upiManager = UPIManager(getApplication())
            voicePayAgent = VoicePayAgent(getApplication(), upiManager)
            isInitialized = true
            
            _statusMessage.value = "VoicePay initialized and ready"
            
            // Load UPI apps
            refreshUpiApps()
        }
    }
    
    fun processVoiceCommand(command: String) {
        if (!isInitialized) {
            _speechResponse.value = "VoicePay is not ready yet. Please try again in a moment."
            return
        }
        
        _isProcessing.value = true
        _statusMessage.value = "Processing: \"$command\""
        
        viewModelScope.launch {
            try {
                val response = voicePayAgent.processCommand(command)
                _speechResponse.value = response
                _statusMessage.value = "Command processed"
                
            } catch (e: Exception) {
                _speechResponse.value = "I apologize, but I encountered an error. Please try again."
                _statusMessage.value = "Error processing command"
                
            } finally {
                _isProcessing.value = false
            }
        }
    }
    
    fun refreshUpiApps() {
        viewModelScope.launch {
            try {
                val apps = upiManager.getInstalledUpiApps()
                _upiApps.value = apps
                
                val message = if (apps.isNotEmpty()) {
                    "Found ${apps.size} UPI app(s): ${apps.joinToString(", ") { it.appName }}"
                } else {
                    "No UPI apps found. Please install PhonePe, Google Pay, or another UPI app."
                }
                
                _statusMessage.value = message
                
            } catch (e: Exception) {
                _statusMessage.value = "Error checking UPI apps"
            }
        }
    }
    
    fun openUpiApp(packageName: String) {
        viewModelScope.launch {
            try {
                val success = upiManager.openUpiApp(packageName)
                val appName = _upiApps.value?.find { it.packageName == packageName }?.appName ?: "UPI app"
                
                _statusMessage.value = if (success) {
                    "Opened $appName"
                } else {
                    "Failed to open $appName"
                }
                
            } catch (e: Exception) {
                _statusMessage.value = "Error opening UPI app"
            }
        }
    }
    
    fun checkUpiAppStatus() {
        viewModelScope.launch {
            try {
                val statusMap = upiManager.checkUpiAppStatus()
                val installedCount = statusMap.values.count { it }
                
                _statusMessage.value = "UPI apps status: $installedCount installed out of ${statusMap.size} checked"
                
            } catch (e: Exception) {
                _statusMessage.value = "Error checking UPI app status"
            }
        }
    }
    
    fun validateUpiId(upiId: String, callback: (Boolean) -> Unit) {
        viewModelScope.launch {
            try {
                val isValid = upiManager.validateUpiId(upiId)
                callback(isValid)
                
            } catch (e: Exception) {
                callback(false)
            }
        }
    }
    
    fun getUpiRecommendations(callback: (List<String>) -> Unit) {
        viewModelScope.launch {
            try {
                val recommendations = upiManager.getUpiAppRecommendations()
                callback(recommendations)
                
            } catch (e: Exception) {
                callback(listOf("Error getting recommendations"))
            }
        }
    }
    
    fun makePayment(upiId: String, amount: Double, description: String, appPackage: String? = null) {
        _isProcessing.value = true
        _statusMessage.value = "Initiating payment..."
        
        viewModelScope.launch {
            try {
                val success = upiManager.initiatePayment(upiId, amount, description, appPackage)
                
                if (success) {
                    _speechResponse.value = "Payment of ₹${amount.toInt()} initiated. Please complete the transaction in your UPI app."
                    _statusMessage.value = "Payment initiated successfully"
                } else {
                    _speechResponse.value = "Payment initiation failed. Please try again."
                    _statusMessage.value = "Payment failed"
                }
                
            } catch (e: Exception) {
                _speechResponse.value = "Payment failed due to an error. Please try again."
                _statusMessage.value = "Payment error"
                
            } finally {
                _isProcessing.value = false
            }
        }
    }
    
    fun getMemoryStats(callback: (Map<String, Any>) -> Unit) {
        viewModelScope.launch {
            try {
                if (::voicePayAgent.isInitialized) {
                    // Access memory manager through agent if needed
                    val stats = mapOf(
                        "agent_initialized" to true,
                        "upi_manager_initialized" to ::upiManager.isInitialized,
                        "apps_loaded" to (_upiApps.value?.size ?: 0)
                    )
                    callback(stats)
                } else {
                    callback(mapOf("agent_initialized" to false))
                }
                
            } catch (e: Exception) {
                callback(mapOf("error" to (e.message ?: "Unknown error")))
            }
        }
    }
    
    fun clearSession() {
        viewModelScope.launch {
            try {
                if (::voicePayAgent.isInitialized) {
                    voicePayAgent.cleanup()
                }
                _statusMessage.value = "Session cleared for security"
                _speechResponse.value = "Your session has been cleared. Ready for new commands."
                
            } catch (e: Exception) {
                _statusMessage.value = "Error clearing session"
            }
        }
    }
    
    override fun onCleared() {
        super.onCleared()
        
        if (::voicePayAgent.isInitialized) {
            voicePayAgent.cleanup()
        }
    }
}
