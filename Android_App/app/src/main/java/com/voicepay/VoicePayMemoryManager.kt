package com.voicepay

import android.util.Log
import kotlinx.coroutines.*
import java.util.concurrent.ConcurrentHashMap

class VoicePayMemoryManager {
    
    companion object {
        private const val TAG = "VoicePayMemoryManager"
        private const val AUTO_CLEANUP_INTERVAL_MS = 3600000L // 1 hour
        private const val DATA_RETENTION_MS = 3600000L // 1 hour
    }
    
    private val sensitiveDataStore = ConcurrentHashMap<String, SensitiveDataEntry>()
    private val regularDataStore = ConcurrentHashMap<String, Any>()
    private var cleanupJob: Job? = null
    
    data class SensitiveDataEntry(
        val data: Any,
        val timestamp: Long = System.currentTimeMillis(),
        val accessCount: Int = 0
    )
    
    init {
        startAutoCleanup()
    }
    
    private fun startAutoCleanup() {
        cleanupJob = CoroutineScope(Dispatchers.IO).launch {
            while (isActive) {
                delay(AUTO_CLEANUP_INTERVAL_MS)
                performCleanup()
            }
        }
    }
    
    fun storeSensitiveData(key: String, data: Any) {
        val entry = SensitiveDataEntry(data)
        sensitiveDataStore[key] = entry
        Log.d(TAG, "Stored sensitive data with key: $key")
        
        // Schedule auto-deletion for this specific entry
        CoroutineScope(Dispatchers.IO).launch {
            delay(DATA_RETENTION_MS)
            removeSensitiveData(key)
        }
    }
    
    fun getSensitiveData(key: String): Any? {
        val entry = sensitiveDataStore[key]
        
        if (entry != null) {
            // Update access count and timestamp
            val updatedEntry = entry.copy(
                accessCount = entry.accessCount + 1,
                timestamp = System.currentTimeMillis()
            )
            sensitiveDataStore[key] = updatedEntry
            
            Log.d(TAG, "Retrieved sensitive data with key: $key (access count: ${updatedEntry.accessCount})")
            return entry.data
        }
        
        Log.w(TAG, "Sensitive data not found for key: $key")
        return null
    }
    
    fun removeSensitiveData(key: String): Boolean {
        val removed = sensitiveDataStore.remove(key) != null
        if (removed) {
            Log.d(TAG, "Removed sensitive data with key: $key")
        }
        return removed
    }
    
    fun storeRegularData(key: String, data: Any) {
        regularDataStore[key] = data
        Log.d(TAG, "Stored regular data with key: $key")
    }
    
    fun getRegularData(key: String): Any? {
        return regularDataStore[key]
    }
    
    fun removeRegularData(key: String): Boolean {
        val removed = regularDataStore.remove(key) != null
        if (removed) {
            Log.d(TAG, "Removed regular data with key: $key")
        }
        return removed
    }
    
    fun clearSensitiveData() {
        val count = sensitiveDataStore.size
        sensitiveDataStore.clear()
        Log.d(TAG, "Cleared $count sensitive data entries")
    }
    
    fun clearRegularData() {
        val count = regularDataStore.size
        regularDataStore.clear()
        Log.d(TAG, "Cleared $count regular data entries")
    }
    
    fun clearAllData() {
        clearSensitiveData()
        clearRegularData()
        Log.d(TAG, "Cleared all data")
    }
    
    private fun performCleanup() {
        val currentTime = System.currentTimeMillis()
        val expiredKeys = mutableListOf<String>()
        
        // Find expired sensitive data
        for ((key, entry) in sensitiveDataStore) {
            if (currentTime - entry.timestamp > DATA_RETENTION_MS) {
                expiredKeys.add(key)
            }
        }
        
        // Remove expired entries
        for (key in expiredKeys) {
            sensitiveDataStore.remove(key)
            Log.d(TAG, "Auto-cleanup removed expired sensitive data: $key")
        }
        
        if (expiredKeys.isNotEmpty()) {
            Log.d(TAG, "Auto-cleanup completed: removed ${expiredKeys.size} expired entries")
        }
    }
    
    fun getMemoryStats(): Map<String, Any> {
        val stats = mapOf(
            "sensitive_data_count" to sensitiveDataStore.size,
            "regular_data_count" to regularDataStore.size,
            "cleanup_job_active" to (cleanupJob?.isActive == true),
            "oldest_sensitive_entry_age_ms" to getOldestSensitiveEntryAge(),
            "total_sensitive_access_count" to getTotalAccessCount()
        )
        
        Log.d(TAG, "Memory stats: $stats")
        return stats
    }
    
    private fun getOldestSensitiveEntryAge(): Long {
        val currentTime = System.currentTimeMillis()
        var oldestAge = 0L
        
        for (entry in sensitiveDataStore.values) {
            val age = currentTime - entry.timestamp
            if (age > oldestAge) {
                oldestAge = age
            }
        }
        
        return oldestAge
    }
    
    private fun getTotalAccessCount(): Int {
        return sensitiveDataStore.values.sumOf { it.accessCount }
    }
    
    fun securityAudit(): List<String> {
        val auditResults = mutableListOf<String>()
        val currentTime = System.currentTimeMillis()
        
        // Check for old data
        for ((key, entry) in sensitiveDataStore) {
            val age = currentTime - entry.timestamp
            if (age > DATA_RETENTION_MS * 0.8) { // Warn at 80% of retention time
                auditResults.add("WARNING: Sensitive data '$key' is ${age / 1000}s old")
            }
        }
        
        // Check memory usage
        if (sensitiveDataStore.size > 50) {
            auditResults.add("WARNING: High number of sensitive data entries: ${sensitiveDataStore.size}")
        }
        
        if (regularDataStore.size > 100) {
            auditResults.add("WARNING: High number of regular data entries: ${regularDataStore.size}")
        }
        
        // Check cleanup job
        if (cleanupJob?.isActive != true) {
            auditResults.add("ERROR: Auto-cleanup job is not active")
        }
        
        if (auditResults.isEmpty()) {
            auditResults.add("All security checks passed")
        }
        
        Log.d(TAG, "Security audit completed: ${auditResults.size} findings")
        return auditResults
    }
    
    fun forceCleanup() {
        performCleanup()
        Log.d(TAG, "Force cleanup completed")
    }
    
    fun shutdown() {
        cleanupJob?.cancel()
        clearAllData()
        Log.d(TAG, "Memory manager shutdown completed")
    }
    
    // Utility function to check if sensitive data exists and is not expired
    fun hasFreshSensitiveData(key: String): Boolean {
        val entry = sensitiveDataStore[key]
        if (entry != null) {
            val age = System.currentTimeMillis() - entry.timestamp
            return age < DATA_RETENTION_MS
        }
        return false
    }
    
    // Get data with automatic cleanup if expired
    fun getSensitiveDataWithCleanup(key: String): Any? {
        val entry = sensitiveDataStore[key]
        
        if (entry != null) {
            val age = System.currentTimeMillis() - entry.timestamp
            
            if (age > DATA_RETENTION_MS) {
                // Data is expired, remove it
                removeSensitiveData(key)
                Log.d(TAG, "Removed expired sensitive data during access: $key")
                return null
            }
            
            // Data is fresh, return it with updated access info
            return getSensitiveData(key)
        }
        
        return null
    }
}
