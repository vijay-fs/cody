#!/usr/bin/env python3
"""
Demo script to show the new interactive AI CLI features
"""

print("🤖 AI CLI Interactive Demo")
print("=" * 50)

print("\n📋 Available Commands:")
print("1. Basic usage:")
print("   ai                    # Enters interactive mode")
print("   ai chat 'Hello'       # Single chat command")
print("   ai providers          # Show provider status")
print("   ai config --show      # Show configuration")

print("\n🎮 Interactive Mode Commands:")
print("   /help                 # Show help")
print("   /mcp                  # Configure MCP services")
print("   /mcp add              # Add GitHub/GitLab token")
print("   /mcp status           # Show MCP status")
print("   /mcp test github      # Test GitHub connection")
print("   /providers            # Show AI providers")
print("   /config               # Show configuration")
print("   /exit                 # Exit interactive mode")

print("\n💬 Chat Examples (in interactive mode):")
print("   Hello, how are you?")
print("   Explain Python decorators --provider claude")
print("   Write a function --stream")
print("   What is machine learning? --provider openai")

print("\n🔧 MCP Token Configuration:")
print("1. Enter interactive mode: ai")
print("2. Type: /mcp add")
print("3. Choose: github")
print("4. Follow the setup instructions")
print("5. Paste your GitHub token")
print("6. Test with: /mcp test github")

print("\n🚀 Quick Start:")
print("1. Type: ai")
print("2. Type: /mcp add")
print("3. Configure your GitHub token")
print("4. Start chatting!")

print("\n✨ Try it now:")
print("   ai                    # Start interactive mode")
print("   ai chat 'Hello!'      # Quick single message")

print("\n📚 Your GitHub token is already configured!")
print("You can test it with: ai mcp search github 'hello world'")