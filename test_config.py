#!/usr/bin/env python3
"""Test script to diagnose config loading issues."""

import json
import os
from pathlib import Path

# Set the API key environment variable
os.environ["NVIDIA_API_KEY"] = "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"

# Add project to path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from nanobot.config.loader import load_config
from nanobot.config.schema import Config

# Load config
config_path = Path.home() / ".nanobot" / "config.json"
print(f"Loading config from: {config_path}")

try:
    with open(config_path) as f:
        raw_data = json.load(f)
    print("\n✓ Config file loaded successfully")
    
    # Check custom providers
    custom_providers = raw_data.get("providers", {}).get("customProviders", [])
    print(f"\nFound {len(custom_providers)} custom provider(s)")
    
    for i, cp in enumerate(custom_providers):
        print(f"\n--- Custom Provider {i+1} ---")
        print(f"  Name: {cp.get('name')}")
        print(f"  Display Name: {cp.get('displayName')}")
        print(f"  apiKey present: {'apiKey' in cp}")
        print(f"  apiKey value: {cp.get('apiKey', 'NOT SET')[:20]}..." if cp.get('apiKey') else "  apiKey value: EMPTY")
        print(f"  apiBase: {cp.get('apiBase')}")
        print(f"  Models: {cp.get('models', [])}")
        print(f"  envKey: {cp.get('envKey')}")
        
except Exception as e:
    print(f"Error loading config: {e}")
    import traceback
    traceback.print_exc()

# Now try loading through the normal loader
print("\n" + "="*60)
print("Loading config through nanobot loader...")
print("="*60)

try:
    config = load_config()
    print("\n✓ Config loaded successfully")
    
    # Check default model
    model = config.agents.defaults.model
    print(f"\nDefault model: {model}")
    
    # Try to get provider
    provider = config.get_provider(model)
    provider_name = config.get_provider_name(model)
    
    if provider:
        print(f"\n✓ Provider found: {provider_name}")
        print(f"  API Key: {provider.api_key[:30]}..." if provider.api_key else "  API Key: NOT SET")
        print(f"  API Base: {provider.api_base}")
    else:
        print(f"\n✗ No provider found for model: {model}")
        print("\n  Checking custom providers in loaded config:")
        for cp in config.providers.custom_providers:
            print(f"    - {cp.name}: api_key={'SET' if cp.api_key else 'NOT SET'}, models={cp.models}")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
