"""
Memory management for the VoicePay UPI Assistant with enhanced security.
"""
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class VoicePayMemory:
    """Represents a memory item for VoicePay with security considerations."""
    content: str
    timestamp: datetime
    type: str  # 'app_detection', 'transaction_guidance', 'security_action', 'user_interaction'
    metadata: Optional[Dict[str, Any]] = None
    sensitive: bool = False  # Flag for sensitive data that should be cleared
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert memory to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VoicePayMemory':
        """Create memory from dictionary."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

class VoicePayMemoryManager:
    """Enhanced memory management for VoicePay with security focus."""
    
    def __init__(self, memory_dir: str = "voicepay_memory"):
        self.memory_dir = memory_dir
        self.memories: List[VoicePayMemory] = []
        self.session_start = datetime.now()
        self._ensure_memory_dir()
        self._load_memories()
        self._cleanup_old_sensitive_data()
    
    def _ensure_memory_dir(self):
        """Create memory directory if it doesn't exist."""
        os.makedirs(self.memory_dir, exist_ok=True)
    
    def _load_memories(self):
        """Load existing memories from files."""
        try:
            memory_file = os.path.join(self.memory_dir, "memories.json")
            if os.path.exists(memory_file):
                with open(memory_file, 'r') as f:
                    data = json.load(f)
                    self.memories = [VoicePayMemory.from_dict(mem) for mem in data]
                logger.info(f"Loaded {len(self.memories)} VoicePay memories")
        except Exception as e:
            logger.error(f"Error loading memories: {e}")
            self.memories = []
    
    def _save_memories(self):
        """Save memories to file."""
        try:
            memory_file = os.path.join(self.memory_dir, "memories.json")
            with open(memory_file, 'w') as f:
                json.dump([mem.to_dict() for mem in self.memories], f, indent=2)
        except Exception as e:
            logger.error(f"Error saving memories: {e}")
    
    def _cleanup_old_sensitive_data(self):
        """Remove old sensitive data for security."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=1)  # Remove sensitive data older than 1 hour
            original_count = len(self.memories)
            
            self.memories = [
                mem for mem in self.memories 
                if not (mem.sensitive and mem.timestamp < cutoff_time)
            ]
            
            removed_count = original_count - len(self.memories)
            if removed_count > 0:
                logger.info(f"Cleaned up {removed_count} old sensitive memory items")
                self._save_memories()
                
        except Exception as e:
            logger.error(f"Error during sensitive data cleanup: {e}")
    
    def add_memory(self, content: str, memory_type: str = "user_interaction", 
                   metadata: Optional[Dict[str, Any]] = None, sensitive: bool = False):
        """Add a new memory with security considerations."""
        
        # Don't store certain sensitive information
        sensitive_keywords = ['pin', 'password', 'otp', 'cvv', 'account number']
        if any(keyword in content.lower() for keyword in sensitive_keywords):
            logger.warning("Attempted to store sensitive data - blocked for security")
            return
        
        # Mark payment details as sensitive
        if memory_type in ['payment_details', 'active_transaction', 'bank_accounts']:
            sensitive = True
        
        memory = VoicePayMemory(
            content=content,
            timestamp=datetime.now(),
            type=memory_type,
            metadata=metadata or {},
            sensitive=sensitive
        )
        
        self.memories.append(memory)
        self._save_memories()
        logger.info(f"Added {memory_type} memory: {content[:50]}...")
        
        # Auto-cleanup if too many memories
        if len(self.memories) > 100:
            self._cleanup_old_memories()
    
    def _cleanup_old_memories(self):
        """Remove old non-essential memories to maintain performance."""
        try:
            # Keep only the most recent 50 memories, prioritizing important types
            important_types = ['security_action', 'transaction_guidance']
            
            important_memories = [m for m in self.memories if m.type in important_types]
            other_memories = [m for m in self.memories if m.type not in important_types]
            
            # Sort by timestamp (most recent first)
            important_memories.sort(key=lambda m: m.timestamp, reverse=True)
            other_memories.sort(key=lambda m: m.timestamp, reverse=True)
            
            # Keep recent important memories and some other memories
            self.memories = important_memories[:30] + other_memories[:20]
            self._save_memories()
            
        except Exception as e:
            logger.error(f"Error during memory cleanup: {e}")
    
    def get_memories(self, memory_type: Optional[str] = None, limit: int = 10, 
                     include_sensitive: bool = False) -> List[VoicePayMemory]:
        """Get recent memories, optionally filtered by type."""
        filtered_memories = self.memories
        
        if memory_type:
            filtered_memories = [m for m in self.memories if m.type == memory_type]
        
        if not include_sensitive:
            filtered_memories = [m for m in filtered_memories if not m.sensitive]
        
        # Sort by timestamp (most recent first) and limit
        sorted_memories = sorted(filtered_memories, key=lambda m: m.timestamp, reverse=True)
        return sorted_memories[:limit]
    
    def search_memories(self, query: str, limit: int = 5, 
                       include_sensitive: bool = False) -> List[VoicePayMemory]:
        """Search memories by content with security filtering."""
        query_lower = query.lower()
        matching_memories = []
        
        for m in self.memories:
            if not include_sensitive and m.sensitive:
                continue
            if query_lower in m.content.lower():
                matching_memories.append(m)
        
        # Sort by timestamp (most recent first) and limit
        sorted_memories = sorted(matching_memories, key=lambda m: m.timestamp, reverse=True)
        return sorted_memories[:limit]
    
    def clear_sensitive_data(self):
        """Clear all sensitive data from memory for security."""
        try:
            original_count = len(self.memories)
            self.memories = [m for m in self.memories if not m.sensitive]
            removed_count = original_count - len(self.memories)
            
            self._save_memories()
            logger.info(f"Cleared {removed_count} sensitive memory items for security")
            
            return f"Cleared {removed_count} sensitive items from memory"
            
        except Exception as e:
            logger.error(f"Error clearing sensitive data: {e}")
            return "Error occurred while clearing sensitive data"
    
    def get_session_summary(self) -> str:
        """Get a summary of the current session."""
        try:
            session_memories = [m for m in self.memories if m.timestamp >= self.session_start]
            
            summary = {
                "session_duration": str(datetime.now() - self.session_start),
                "total_interactions": len(session_memories),
                "memory_types": {}
            }
            
            for memory in session_memories:
                if memory.type in summary["memory_types"]:
                    summary["memory_types"][memory.type] += 1
                else:
                    summary["memory_types"][memory.type] = 1
            
            return json.dumps(summary, indent=2)
            
        except Exception as e:
            logger.error(f"Error generating session summary: {e}")
            return "Error generating session summary"

# Create alias for backward compatibility
MemoryManager = VoicePayMemoryManager

# Global memory manager instance
memory_manager = VoicePayMemoryManager()
