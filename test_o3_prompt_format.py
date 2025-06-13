#!/usr/bin/env python3

"""Test to show the exact prompt format that o3 models will receive."""

import asyncio
import sys
import os

# Add the current directory to path so we can import our modules
sys.path.insert(0, '/Users/Ghost/Desktop/dev/cody')

from ai_cli.core.reasoning import AdvancedReasoningEngine
from ai_cli.core.tools import ToolExecutor
from ai_cli.core.config import AICliConfig
from ai_cli.core.context import ConversationContext

async def test_o3_prompt_format():
    """Show exactly what prompt o3 models will receive."""
    
    print("=== O3 Model Prompt Format Test ===\n")
    
    # Set up the reasoning engine
    reasoning_engine = AdvancedReasoningEngine()
    
    # Test with a complex query that should trigger advanced reasoning
    complex_query = "Design a scalable websocket architecture for real-time collaboration with authentication and message persistence"
    
    # Mock some code context
    mock_code_context = [
        {
            "repository": "myproject/backend", 
            "path": "src/websocket/server.js",
            "content": "const WebSocket = require('ws');\nconst jwt = require('jsonwebtoken');\n\nclass WebSocketServer {\n  constructor(port) {\n    this.wss = new WebSocket.Server({ port });\n    this.clients = new Map();\n  }\n\n  authenticate(token) {\n    try {\n      return jwt.verify(token, process.env.JWT_SECRET);\n    } catch (err) {\n      return null;\n    }\n  }\n}",
            "url": "https://github.com/user/myproject/blob/main/src/websocket/server.js",
            "file": "server.js"
        }
    ]
    
    # Generate enhanced reasoning prompt
    enhancement = reasoning_engine.enhance_query_for_reasoning(
        original_query=complex_query,
        code_context=mock_code_context,
        domain="websocket",
        model="o3"
    )
    
    enhanced_prompt = enhancement['enhanced_prompt']['prompt']
    
    print("📋 Full Enhanced Prompt for O3 Model:")
    print("=" * 80)
    print(enhanced_prompt)
    print("=" * 80)
    
    print(f"\n📊 Prompt Analysis:")
    print(f"- Length: {len(enhanced_prompt)} characters")
    print(f"- Reasoning Mode: {enhancement['reasoning_context'].reasoning_mode.value}")
    print(f"- Complexity: {enhancement['reasoning_context'].complexity.value}")
    print(f"- Has <reasoning> tags: {'<reasoning>' in enhanced_prompt}")
    print(f"- Has code context: {len(mock_code_context)} examples")
    print(f"- Recommended model: {enhancement['recommendations']['best_model']}")
    
    print(f"\n🔍 Key Components Found:")
    components = [
        ("Reasoning template", "<reasoning>" in enhanced_prompt),
        ("Code examples", "Example 1:" in enhanced_prompt),
        ("Instructions", "Instructions for reasoning:" in enhanced_prompt),
        ("Reasoning mode", f"Reasoning mode: {enhancement['reasoning_context'].reasoning_mode.value}" in enhanced_prompt),
        ("Analysis framework", any(word in enhanced_prompt for word in ["Step", "Branch", "Meta-Question"]))
    ]
    
    for component, found in components:
        status = "✅" if found else "❌"
        print(f"  {status} {component}")
    
    return enhanced_prompt

if __name__ == "__main__":
    prompt = asyncio.run(test_o3_prompt_format())
    
    print("\n🎯 Summary:")
    print("This is the exact enhanced prompt that o3 models will receive when")
    print("the advanced_reasoning tool is called. It includes:")
    print("1. Detailed reasoning instructions in <reasoning> tags")
    print("2. Code context from the user's repositories") 
    print("3. Model-specific optimizations for o3")
    print("4. Step-by-step analysis framework")
    print("\nThe fix ensures o3 models get these enhanced prompts instead of")
    print("simple tool context summaries, enabling proper reasoning responses.")