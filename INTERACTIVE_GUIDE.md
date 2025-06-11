# 🤖 Interactive AI CLI - Complete Guide

## 🚀 How to Add OpenAI and GitHub Keys in CLI UI

### **Step 1: Enter Interactive Mode**
```bash
ai
```

This will show you the welcome screen and enter interactive mode with a prompt like:
```
AI CLI >
```

### **Step 2: Add OpenAI API Key**
In interactive mode, type:
```bash
/setup openai
```

You'll see:
1. **Setup instructions** with link to OpenAI platform
2. **Secure prompt** to enter your API key (hidden input)
3. **Automatic testing** of the key
4. **Auto-save** to configuration
5. **Optional test chat** to verify it works

### **Step 3: Add GitHub Token**
In interactive mode, type:
```bash
/mcp add
```

1. Choose `github` when prompted
2. **Setup instructions** for GitHub personal access tokens
3. **Secure prompt** to enter your token
4. **Automatic testing** of the connection
5. **Auto-save** to configuration

## 📋 Complete Interactive Commands

### **Setup Commands (API Keys)**
```bash
/setup              # Show all setup options
/setup openai       # Add OpenAI API key
/setup claude       # Add Claude API key  
/setup azure        # Add Azure OpenAI
/setup all          # Setup all providers at once
```

### **MCP Commands (GitHub/GitLab)**
```bash
/mcp                # Show MCP status
/mcp add            # Add new service (GitHub/GitLab)
/mcp status         # Show connection status
/mcp test github    # Test GitHub connection
/mcp remove         # Remove service configuration
```

### **Status Commands**
```bash
/providers          # Show all AI provider status
/config             # Show current configuration
/help               # Show all commands
```

### **Chat Commands**
```bash
Hello, world!                           # Basic chat
Explain Python --provider claude        # Use specific provider
Write code --stream                     # Stream response
What is AI? --provider openai          # Direct provider specification
```

### **Exit Commands**
```bash
/exit               # Exit interactive mode
/quit               # Exit interactive mode
/q                  # Quick exit
```

## 🎯 Complete Workflow Example

### **1. Start Interactive Mode**
```bash
ai
```

### **2. Setup Your Keys**
```bash
AI CLI > /setup openai
```
- Follow the instructions to get your OpenAI key
- Paste your key (it will be hidden)
- Test automatically

```bash
AI CLI > /mcp add
```
- Choose `github`
- Follow instructions for GitHub token
- Paste your token
- Test automatically

### **3. Verify Everything Works**
```bash
AI CLI > /providers
```
Should show ✓ Connected for OpenAI

```bash
AI CLI > /mcp status
```
Should show ✓ Configured for GitHub

### **4. Start Chatting!**
```bash
AI CLI > Hello! How can you help me today?
```

```bash
AI CLI > Search GitHub for authentication code --provider openai
```

### **5. Use MCP Search (if working)**
```bash
AI CLI > /mcp test github
```

## 🔧 Your Current Setup Status

Based on our session, you currently have:
- ✅ **OpenAI API Key**: Already configured and working
- ✅ **GitHub Token**: Already configured
- ✅ **Interactive CLI**: Ready to use

## 🚀 Quick Test

Try this right now:

```bash
# Enter interactive mode
ai

# In interactive mode, check status:
/providers

# Test chat:
Hello! Please confirm you're working.

# Exit:
/exit
```

## 💡 Pro Tips

1. **Hidden Input**: API keys are hidden when you type them (secure)
2. **Auto-Testing**: Keys are tested before saving
3. **Auto-Save**: All configuration is saved automatically
4. **Tab Completion**: Use tab for command completion (if supported)
5. **Quick Exit**: Ctrl+C also exits gracefully

Your interactive AI CLI is ready to use! 🎉