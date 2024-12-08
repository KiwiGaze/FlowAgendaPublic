# events/services/llm_config.py
import json
import os
from pathlib import Path
from django.conf import settings
from typing import Dict, Any

class LLMConfig:
    """Configuration manager for LLM services"""
    
    def __init__(self):
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load LLM configuration from llm_config.json"""
        # First check Django settings for custom path
        config_path = getattr(settings, 'LLM_CONFIG_PATH', None)
        
        if not config_path:
            # Default to project root directory
            config_path = Path(settings.BASE_DIR) / 'llm_config.json'

        try:
            with open(config_path) as f:
                config = json.load(f)
                
            # Validate required fields
            required_fields = ['provider']
            for field in required_fields:
                if field not in config:
                    raise ValueError(f"Missing required field '{field}' in config")
                    
            return config
            
        except FileNotFoundError:
            raise FileNotFoundError(f"LLM config file not found at {config_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in config file at {config_path}")

    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """Get configuration for specific provider"""
        if provider not in self.config:
            raise ValueError(f"Provider '{provider}' not found in config")
        return self.config[provider]

    @property 
    def provider(self) -> str:
        """Get currently configured provider"""
        return self.config['provider']