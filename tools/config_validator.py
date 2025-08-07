#!/usr/bin/env python3
"""
Simple configuration validator for QueryBot.

Validates database configuration and shows current settings.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from utils.core.config import settings


def show_config():
    """Show current configuration"""
    print("=" * 50)
    print("🔧 QueryBot Configuration")
    print("=" * 50)

    # SQL Database
    print("\n📊 SQL Database:")
    db_config = settings.database
    if hasattr(db_config, 'url') and db_config.url:
        # Mask password in URL
        import re
        masked_url = re.sub(r'://([^:]+):([^@]+)@', r'://\1:***@', db_config.url)
        print(f"  URL: {masked_url}")
    else:
        print(f"  Type: {db_config.type}")
        print(f"  Host: {db_config.host}:{db_config.port}")
        print(f"  Database: {db_config.name}")
        print(f"  User: {db_config.user}")
        print(f"  Password: {'✅ Set' if db_config.password else '❌ Not set'}")

    # Vector Database
    print("\n🔍 Vector Database:")
    vector_config = settings.vector_db
    if hasattr(vector_config, 'uri') and vector_config.uri:
        # Mask sensitive parts
        masked_uri = vector_config.uri.split('@')[0] + "@***" if '@' in vector_config.uri else vector_config.uri
        print(f"  URI: {masked_uri}")
        print(f"  Token: {'✅ Set' if vector_config.token else '❌ Not set'}")
    else:
        print(f"  Host: {vector_config.host}:{vector_config.port}")
        print(f"  Database: {vector_config.database}")

    # LLM
    print("\n🤖 LLM:")
    print(f"  Model: {settings.llm.model}")
    print(f"  API Base: {settings.llm.api_base}")
    print(f"  API Key: {'✅ Set' if settings.llm.api_key else '❌ Not set'}")

    # Embedding
    print("\n📊 Embedding:")
    print(f"  Model: {settings.embedding.model}")
    print(f"  API Base: {settings.embedding.api_base}")
    print(f"  API Key: {'✅ Set' if settings.embedding.api_key else '❌ Not set'}")


def main():
    """Main function"""
    show_config()
    print("\n💡 To edit configuration:")
    print("  1. Edit the .env file")
    print("  2. Or copy from env.example: cp env.example .env")


if __name__ == "__main__":
    main()
