import yaml
import os
from typing import Dict, List

class ContextSystemConfig:
    """Configuration manager for the context system"""

    def __init__(self, config_file: str = 'config/context_system.yaml'):
        self.config = {}
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                self.config = yaml.safe_load(f)

    def _merge_configs(self, base: Dict, override: Dict):
        """Recursively merge configuration dictionaries"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_configs(base[key], value)
            else:
                base[key] = value

    def get(self, key_path: str, default=None):
        """Get configuration value using dot notation (e.g., 'redis.host')"""
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value

    def get_agent_config(self, agent_name: str) -> Dict:
        """Get configuration for a specific agent"""
        return self.config.get('agents', {}).get(agent_name, {})

    def get_redis_config(self) -> Dict:
        """Get Redis configuration"""
        return self.config.get('redis', {})

    def get_knowledge_config(self) -> Dict:
        """Get knowledge management configuration"""
        return self.config.get('knowledge_management', {})

    def save_config(self, config_file: str):
        """Save current configuration to file"""
        with open(config_file, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False, indent=2)
