"""
Configuration management for the VoicePay UPI Assistant.
"""
import os
from dataclasses import dataclass
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

@dataclass
class VoicePayConfig:
    """Configuration for the VoicePay UPI assistant."""
    
    # Voice and model settings
    voice: str = "Charon"  # British-sounding voice for butler persona
    temperature: float = 0.3  # Lower temperature for more consistent responses
    max_tokens: Optional[int] = None
    
    # Audio settings optimized for accessibility
    audio_enabled: bool = True
    video_enabled: bool = True
    noise_cancellation: bool = True
    speech_rate: str = "normal"  # For elderly/visually impaired users
    
    # UPI-specific settings
    max_transaction_amount: float = 100000.0  # ₹1 lakh limit
    large_amount_threshold: float = 10000.0   # ₹10,000 for confirmation
    session_timeout_minutes: int = 15         # Security timeout
    
    # Security settings
    enable_amount_confirmation: bool = True
    enable_recipient_verification: bool = True
    store_transaction_history: bool = False   # For privacy
    
    # Memory settings
    memory_retention_days: int = 0  # Don't retain sensitive data
    max_payment_memories: int = 0   # For security, don't store payment details
    
    # Accessibility features
    slow_speech_mode: bool = False
    repeat_confirmations: bool = True
    verbose_guidance: bool = True
    
    # Logging for security audit
    log_level: str = "INFO"
    log_transactions: bool = True  # For security auditing only
    
    def __post_init__(self):
        """Load environment variables after initialization."""
        # Load from environment with security considerations
        self.temperature = float(os.getenv('VOICEPAY_TEMPERATURE', self.temperature))
        self.max_transaction_amount = float(os.getenv('MAX_TRANSACTION_AMOUNT', self.max_transaction_amount))
        self.large_amount_threshold = float(os.getenv('LARGE_AMOUNT_THRESHOLD', self.large_amount_threshold))
        self.session_timeout_minutes = int(os.getenv('SESSION_TIMEOUT_MINUTES', self.session_timeout_minutes))
        
        # Audio and accessibility settings
        self.audio_enabled = os.getenv('AUDIO_ENABLED', 'true').lower() == 'true'
        self.video_enabled = os.getenv('VIDEO_ENABLED', 'true').lower() == 'true'
        self.noise_cancellation = os.getenv('NOISE_CANCELLATION', 'true').lower() == 'true'
        self.slow_speech_mode = os.getenv('SLOW_SPEECH_MODE', 'false').lower() == 'true'
        
        # Security settings
        self.enable_amount_confirmation = os.getenv('ENABLE_AMOUNT_CONFIRMATION', 'true').lower() == 'true'
        self.enable_recipient_verification = os.getenv('ENABLE_RECIPIENT_VERIFICATION', 'true').lower() == 'true'
        
        # Logging
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_transactions = os.getenv('LOG_TRANSACTIONS', 'true').lower() == 'true'

# Global configuration instance
config = VoicePayConfig()
