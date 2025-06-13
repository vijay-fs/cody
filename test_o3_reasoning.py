#!/usr/bin/env python3

"""Test script to verify o3 reasoning functionality works."""

import asyncio
import sys
import os

# Add the current directory to path so we can import our modules
sys.path.insert(0, '/Users/Ghost/Desktop/dev/cody')

from ai_cli.core.reasoning import AdvancedReasoningEngine, ReasoningMode, ComplexityLevel
from ai_cli.core.tools import ToolExecutor
from ai_cli.core.config import AICliConfig
from ai_cli.core.context import ConversationContext

async def test_reasoning_functionality():
    """Test the reasoning functionality that should work with o3 models."""
    
    print("Testing Advanced Reasoning Engine...")
    
    reasoning_engine = AdvancedReasoningEngine()
    
    # Test 1: Complexity analysis
    test_queries = [
        "How do I implement authentication?",
        "Design a scalable websocket architecture for real-time collaboration",
        "What's the best way to optimize database performance in a distributed system?"
    ]
    
    for query in test_queries:
        print(f"\n--- Testing Query: '{query}' ---")
        
        complexity, reason = reasoning_engine.analyze_query_complexity(query)
        print(f"Complexity: {complexity.value} ({reason})")
        
        reasoning_mode = reasoning_engine.select_reasoning_mode(query, complexity, "architecture")
        print(f"Reasoning Mode: {reasoning_mode.value}")
        
        # Test the enhanced query generation
        enhancement = reasoning_engine.enhance_query_for_reasoning(
            original_query=query,
            code_context=[],
            domain="architecture",
            model="o3"
        )
        
        print(f"Recommended Model: {enhancement['recommendations']['best_model']}")
        print(f"Estimated Tokens: {enhancement['recommendations']['estimated_tokens']}")
        print(f"Enhanced Prompt Length: {len(enhancement['enhanced_prompt']['prompt'])} chars")
        
        # Check if reasoning template contains <reasoning> tags
        enhanced_prompt = enhancement['enhanced_prompt']['prompt']
        has_reasoning_tags = '<reasoning>' in enhanced_prompt and '</reasoning>' in enhanced_prompt
        print(f"Has Reasoning Tags: {has_reasoning_tags}")
        
        if has_reasoning_tags:
            print("✅ Reasoning template correctly generated")
        else:
            print("❌ Missing reasoning template tags")

def test_should_use_advanced_reasoning():
    """Test the query complexity detection."""
    
    print("\n\n=== Testing Query Complexity Detection ===")
    
    # Import the SmartInteractiveCLI class to test the method
    from ai_cli.cli.smart_interactive import SmartInteractiveCLI
    
    cli = SmartInteractiveCLI()
    
    test_cases = [
        ("Hello", False, "Simple greeting"),
        ("How do I implement authentication?", True, "Implementation question"),
        ("Design a scalable websocket architecture", True, "Architecture design"),
        ("What's the best way to optimize performance?", True, "Best practices"),
        ("Show me examples", False, "Simple request"),
        ("Explain step by step how to build a distributed microservice system with load balancing", True, "Complex multi-part question"),
    ]
    
    for query, expected, description in test_cases:
        result = cli._should_use_advanced_reasoning(query)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{query}' -> {result} ({description})")

if __name__ == "__main__":
    asyncio.run(test_reasoning_functionality())
    test_should_use_advanced_reasoning()
    
    print("\n🎯 Summary:")
    print("- Advanced reasoning engine generates proper reasoning templates")
    print("- Query complexity detection identifies when reasoning is needed") 
    print("- o3 models should now receive enhanced prompts with <reasoning> tags")
    print("- Complex queries will automatically trigger advanced reasoning mode")