#!/usr/bin/env python3
"""
AI CLI Demonstration Script

This script demonstrates the key features of the AI CLI tool.
"""
import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and display its output."""
    print(f"\n🔹 {description}")
    print(f"💾 Command: {cmd}")
    print("─" * 60)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.stdout:
            print(result.stdout)
        if result.stderr and result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("⏱️ Command timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False

def main():
    print("🌟 AI CLI Tool Demo")
    print("=" * 60)
    
    # 1. Show help
    run_command("ai-cli --help", "Display main help")
    
    # 2. Show providers
    run_command("ai-cli providers", "List available AI providers")
    
    # 3. Show configuration
    run_command("ai-cli config-cmd --show", "Show current configuration")
    
    # 4. Show chat help
    run_command("ai-cli chat --help", "Show chat command options")
    
    # 5. Show MCP commands
    run_command("ai-cli mcp --help", "Show MCP integration commands")
    
    print("\n🎯 Next Steps:")
    print("1. Add your API keys to the configuration:")
    print("   ai-cli config-cmd --edit")
    print("\n2. Test chat with a provider:")
    print("   ai-cli chat 'Hello, AI!' --provider openai")
    print("\n3. Connect to GitHub/GitLab:")
    print("   ai-cli mcp connect github --token your-github-token")
    print("\n4. Search code repositories:")
    print("   ai-cli mcp search github 'function main' --owner yourorg --repo yourproject")
    
    print("\n📚 Documentation available in docs/ folder")
    print("✨ AI CLI setup complete!")

if __name__ == "__main__":
    main()