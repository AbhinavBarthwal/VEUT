package com.voicepay

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.ViewModelProvider
import java.util.*

class MainActivity : AppCompatActivity(), TextToSpeech.OnInitListener {
    
    private lateinit var tts: TextToSpeech
    private lateinit var speechRecognizer: SpeechRecognizer
    private lateinit var voicePayAgent: VoicePayAgent
    private lateinit var upiManager: UPIManager
    private lateinit var viewModel: VoicePayViewModel
    
    private lateinit var statusText: TextView
    private lateinit var startButton: Button
    private lateinit var stopButton: Button
    
    private var isListening = false
    private var ttsInitialized = false
    
    companion object {
        private const val PERMISSION_REQUEST_CODE = 123
    }
    
    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted: Boolean ->
        if (isGranted) {
            initializeSpeechComponents()
        } else {
            showToast("Microphone permission is required for voice commands")
        }
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        initializeViews()
        initializeViewModel()
        checkPermissions()
    }
    
    private fun initializeViews() {
        statusText = findViewById(R.id.status_text)
        startButton = findViewById(R.id.start_button)
        stopButton = findViewById(R.id.stop_button)
        
        startButton.setOnClickListener { startListening() }
        stopButton.setOnClickListener { stopListening() }
        
        updateUI(false)
    }
    
    private fun initializeViewModel() {
        viewModel = ViewModelProvider(this)[VoicePayViewModel::class.java]
        
        viewModel.statusMessage.observe(this) { message ->
            statusText.text = message
        }
        
        viewModel.speechResponse.observe(this) { response ->
            speak(response)
        }
        
        viewModel.isProcessing.observe(this) { isProcessing ->
            updateUI(!isProcessing && ttsInitialized)
        }
    }
    
    private fun checkPermissions() {
        when {
            ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.RECORD_AUDIO
            ) == PackageManager.PERMISSION_GRANTED -> {
                initializeSpeechComponents()
            }
            else -> {
                requestPermissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
            }
        }
    }
    
    private fun initializeSpeechComponents() {
        // Initialize Text-to-Speech
        tts = TextToSpeech(this, this)
        
        // Initialize VoicePay components
        upiManager = UPIManager(this)
        voicePayAgent = VoicePayAgent(this, upiManager)
        
        // Initialize Speech Recognizer
        if (SpeechRecognizer.isRecognitionAvailable(this)) {
            speechRecognizer = SpeechRecognizer.createSpeechRecognizer(this)
            speechRecognizer.setRecognitionListener(createRecognitionListener())
        } else {
            showToast("Speech recognition not available on this device")
        }
        
        // Welcome message
        speak("Hello! I'm your VoicePay butler assistant. Ready to help with your UPI payments.")
    }
    
    override fun onInit(status: Int) {
        if (status == TextToSpeech.SUCCESS) {
            val result = tts.setLanguage(Locale.UK) // British accent
            if (result == TextToSpeech.LANG_MISSING_DATA || result == TextToSpeech.LANG_NOT_SUPPORTED) {
                tts.setLanguage(Locale.US) // Fallback to US English
            }
            
            // Set speech rate for elderly users
            tts.setSpeechRate(0.8f)
            tts.setPitch(1.0f)
            
            ttsInitialized = true
            updateUI(true)
        } else {
            showToast("Text-to-Speech initialization failed")
        }
    }
    
    private fun startListening() {
        if (!isListening && ::speechRecognizer.isInitialized) {
            val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault())
                putExtra(RecognizerIntent.EXTRA_PROMPT, "Speak your payment command...")
                putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
                putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)
            }
            
            speechRecognizer.startListening(intent)
            isListening = true
            updateUI(false)
            statusText.text = "Listening... Please speak your command"
        }
    }
    
    private fun stopListening() {
        if (isListening && ::speechRecognizer.isInitialized) {
            speechRecognizer.stopListening()
            isListening = false
            updateUI(true)
            statusText.text = "Ready for commands"
        }
    }
    
    private fun createRecognitionListener(): RecognitionListener {
        return object : RecognitionListener {
            override fun onReadyForSpeech(params: Bundle?) {
                statusText.text = "Listening..."
            }
            
            override fun onBeginningOfSpeech() {
                statusText.text = "Processing speech..."
            }
            
            override fun onRmsChanged(rmsdB: Float) {}
            
            override fun onBufferReceived(buffer: ByteArray?) {}
            
            override fun onEndOfSpeech() {
                isListening = false
                statusText.text = "Processing command..."
            }
            
            override fun onError(error: Int) {
                isListening = false
                updateUI(true)
                
                val errorMessage = when (error) {
                    SpeechRecognizer.ERROR_AUDIO -> "Audio recording error"
                    SpeechRecognizer.ERROR_CLIENT -> "Client side error"
                    SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS -> "Insufficient permissions"
                    SpeechRecognizer.ERROR_NETWORK -> "Network error"
                    SpeechRecognizer.ERROR_NETWORK_TIMEOUT -> "Network timeout"
                    SpeechRecognizer.ERROR_NO_MATCH -> "No speech match found"
                    SpeechRecognizer.ERROR_RECOGNIZER_BUSY -> "Recognition service busy"
                    SpeechRecognizer.ERROR_SERVER -> "Server error"
                    SpeechRecognizer.ERROR_SPEECH_TIMEOUT -> "No speech input"
                    else -> "Speech recognition error"
                }
                
                statusText.text = "Ready for commands"
                speak("I'm sorry, I didn't catch that. Please try again.")
            }
            
            override fun onResults(results: Bundle?) {
                isListening = false
                updateUI(true)
                
                val matches = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                if (!matches.isNullOrEmpty()) {
                    val spokenText = matches[0]
                    statusText.text = "Processing: \"$spokenText\""
                    
                    // Process the command through VoicePay agent
                    viewModel.processVoiceCommand(spokenText)
                } else {
                    speak("I didn't hear anything. Please try again.")
                    statusText.text = "Ready for commands"
                }
            }
            
            override fun onPartialResults(partialResults: Bundle?) {}
            override fun onEvent(eventType: Int, params: Bundle?) {}
        }
    }
    
    private fun speak(text: String) {
        if (ttsInitialized && ::tts.isInitialized) {
            tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, "VoicePay")
        }
    }
    
    private fun updateUI(enabled: Boolean) {
        startButton.isEnabled = enabled && !isListening
        stopButton.isEnabled = isListening
    }
    
    private fun showToast(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }
    
    override fun onDestroy() {
        super.onDestroy()
        
        if (::tts.isInitialized) {
            tts.stop()
            tts.shutdown()
        }
        
        if (::speechRecognizer.isInitialized) {
            speechRecognizer.destroy()
        }
    }
    
    override fun onPause() {
        super.onPause()
        if (isListening) {
            stopListening()
        }
    }
}
