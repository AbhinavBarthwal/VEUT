package com.voicepay

import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

data class UpiApp(
    val packageName: String,
    val appName: String,
    val isInstalled: Boolean
)

class UPIManager(private val context: Context) {
    
    companion object {
        private const val TAG = "UPIManager"
        
        // Common UPI apps with their package names
        private val KNOWN_UPI_APPS = mapOf(
            "com.phonepe.app" to "PhonePe",
            "com.google.android.apps.nfc.payment" to "Google Pay",
            "net.one97.paytm" to "Paytm",
            "in.org.npci.upiapp" to "BHIM UPI",
            "com.amazon.mShop.android.shopping" to "Amazon Pay",
            "com.mobikwik_new" to "MobiKwik",
            "com.freecharge.android" to "Freecharge",
            "com.myairtelapp" to "Airtel Thanks",
            "com.csam.icici.bank.imobile" to "iMobile Pay",
            "com.sbi.lotusintouch" to "Yono SBI"
        )
    }
    
    private val packageManager = context.packageManager
    
    suspend fun getInstalledUpiApps(): List<UpiApp> {
        return withContext(Dispatchers.IO) {
            val installedApps = mutableListOf<UpiApp>()
            
            for ((packageName, appName) in KNOWN_UPI_APPS) {
                val isInstalled = isAppInstalled(packageName)
                if (isInstalled) {
                    installedApps.add(UpiApp(packageName, appName, true))
                }
            }
            
            Log.d(TAG, "Found ${installedApps.size} UPI apps: ${installedApps.map { it.appName }}")
            installedApps
        }
    }
    
    private fun isAppInstalled(packageName: String): Boolean {
        return try {
            packageManager.getApplicationInfo(packageName, 0)
            true
        } catch (e: PackageManager.NameNotFoundException) {
            false
        }
    }
    
    suspend fun initiatePayment(
        upiId: String,
        amount: Double,
        description: String,
        appPackage: String? = null
    ): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val paymentUri = buildUpiUri(upiId, amount, description)
                val intent = Intent(Intent.ACTION_VIEW, paymentUri)
                
                // If specific app package is provided, set it
                appPackage?.let { 
                    intent.setPackage(it)
                }
                
                // Add flags for new task
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                
                // Check if any app can handle this intent
                val resolveInfos = packageManager.queryIntentActivities(intent, 0)
                
                if (resolveInfos.isNotEmpty()) {
                    context.startActivity(intent)
                    Log.d(TAG, "Payment intent sent: $paymentUri")
                    true
                } else {
                    Log.e(TAG, "No UPI app can handle the payment intent")
                    false
                }
                
            } catch (e: Exception) {
                Log.e(TAG, "Failed to initiate payment", e)
                false
            }
        }
    }
    
    private fun buildUpiUri(upiId: String, amount: Double, description: String): Uri {
        val uriBuilder = Uri.Builder()
            .scheme("upi")
            .authority("pay")
            .appendQueryParameter("pa", upiId) // Payee address
            .appendQueryParameter("am", String.format("%.2f", amount)) // Amount
            .appendQueryParameter("cu", "INR") // Currency
            .appendQueryParameter("tn", description) // Transaction note
        
        return uriBuilder.build()
    }
    
    suspend fun checkUpiAppStatus(): Map<String, Boolean> {
        return withContext(Dispatchers.IO) {
            val statusMap = mutableMapOf<String, Boolean>()
            
            for ((packageName, appName) in KNOWN_UPI_APPS) {
                statusMap[appName] = isAppInstalled(packageName)
            }
            
            statusMap
        }
    }
    
    suspend fun openUpiApp(packageName: String): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val intent = packageManager.getLaunchIntentForPackage(packageName)
                
                if (intent != null) {
                    intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                    context.startActivity(intent)
                    Log.d(TAG, "Opened UPI app: $packageName")
                    true
                } else {
                    Log.e(TAG, "Cannot open UPI app: $packageName")
                    false
                }
                
            } catch (e: Exception) {
                Log.e(TAG, "Failed to open UPI app: $packageName", e)
                false
            }
        }
    }
    
    fun getPreferredUpiApp(): UpiApp? {
        // Simple preference logic - can be enhanced with user settings
        val preferenceOrder = listOf(
            "com.phonepe.app",
            "com.google.android.apps.nfc.payment",
            "net.one97.paytm",
            "in.org.npci.upiapp"
        )
        
        for (packageName in preferenceOrder) {
            if (isAppInstalled(packageName)) {
                val appName = KNOWN_UPI_APPS[packageName] ?: "Unknown"
                return UpiApp(packageName, appName, true)
            }
        }
        
        return null
    }
    
    suspend fun validateUpiId(upiId: String): Boolean {
        return withContext(Dispatchers.IO) {
            // Basic UPI ID validation
            val upiPattern = Regex("^[a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+$")
            val isValid = upiPattern.matches(upiId)
            
            Log.d(TAG, "UPI ID validation for '$upiId': $isValid")
            isValid
        }
    }
    
    suspend fun getUpiAppRecommendations(): List<String> {
        return withContext(Dispatchers.IO) {
            val installedApps = getInstalledUpiApps()
            
            if (installedApps.isEmpty()) {
                listOf(
                    "PhonePe - Popular and user-friendly",
                    "Google Pay - Integrated with Google services",
                    "Paytm - Wide merchant acceptance",
                    "BHIM UPI - Official NPCI app"
                )
            } else {
                listOf("You already have ${installedApps.size} UPI app(s) installed and ready to use!")
            }
        }
    }
    
    fun createPlayStoreIntent(packageName: String): Intent {
        return try {
            Intent(Intent.ACTION_VIEW, Uri.parse("market://details?id=$packageName"))
        } catch (e: Exception) {
            Intent(Intent.ACTION_VIEW, Uri.parse("https://play.google.com/store/apps/details?id=$packageName"))
        }.apply {
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        }
    }
}
