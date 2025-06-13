#!/usr/bin/env python3

"""Simulate the user's exact query to see what should happen."""

import asyncio
import sys
import os

# Add the current directory to path so we can import our modules
sys.path.insert(0, '/Users/Ghost/Desktop/dev/cody')

from ai_cli.cli.smart_interactive import SmartInteractiveCLI

async def test_user_query():
    """Test the exact user query that was having issues."""
    
    print("=== Simulating User Query ===")
    
    user_query = "scalable websocket architecture design in Next.js , Provide a complete integration to do it with fileupload with all progress updates."
    
    cli = SmartInteractiveCLI()
    
    # Test 1: Check if this query triggers advanced reasoning
    should_use_reasoning = cli._should_use_advanced_reasoning(user_query)
    print(f"Query should trigger reasoning: {should_use_reasoning}")
    
    # Test 2: Show what the enhanced message would look like
    if should_use_reasoning:
        reasoning_hint = f"\n\nIMPORTANT: This is a complex technical question that REQUIRES advanced reasoning. You MUST call the 'advanced_reasoning' tool with the following parameters:\n- query: \"{user_query}\"\n- domain: \"architecture\" (or appropriate technical domain)\n\nDo NOT just search for code - you MUST also use advanced_reasoning to provide sophisticated analysis with proper reasoning modes (step-by-step, chain-of-thought, tree-of-thought, etc.)."
        
        full_message = user_query + reasoning_hint
        print(f"\nEnhanced message length: {len(full_message)} chars")
        print(f"Enhanced message preview: {full_message[:200]}...")
    
    # Test 3: Check what happens with direct reasoning (fallback)
    print(f"\n=== Testing Direct Reasoning Fallback ===")
    
    try:
        from ai_cli.core.reasoning import AdvancedReasoningEngine
        reasoning_engine = AdvancedReasoningEngine()
        
        # Simulate what happens when advanced_reasoning tool isn't called
        enhancement = reasoning_engine.enhance_query_for_reasoning(
            original_query=user_query,
            code_context=[],  # Simulate no code found
            domain="architecture",
            model="o3-mini"
        )
        
        reasoning_context = enhancement["reasoning_context"]
        enhanced_prompt = enhancement["enhanced_prompt"]["prompt"]
        
        print(f"✅ Direct reasoning mode: {reasoning_context.reasoning_mode.value}")
        print(f"✅ Complexity: {reasoning_context.complexity.value}")
        print(f"✅ Enhanced prompt length: {len(enhanced_prompt)} chars")
        print(f"✅ Has <reasoning> tags: {'<reasoning>' in enhanced_prompt}")
        
        # Show a snippet of what O3 would receive
        print(f"\n--- O3 Model Would Receive (first 500 chars) ---")
        print(enhanced_prompt[:500] + "...")
        print("--- End Preview ---")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in direct reasoning: {e}")
        return False

def analyze_user_output():
    """Analyze what went wrong with the user's actual output."""
    print(f"\n=== Analysis of User's CLI Output ===")
    
    observed_issues = [
        "Response is very short and incomplete",
        "Shows 'Just a moment...' but doesn't continue", 
        "Only search_code tool was called, not advanced_reasoning",
        "Response has reasoning_tokens but content seems cut off",
        "No enhanced reasoning mode indicators visible"
    ]
    
    print("Issues observed:")
    for issue in observed_issues:
        print(f"  ❌ {issue}")
    
    expected_behavior = [
        "GPT-4o should call both search_code AND advanced_reasoning tools",
        "O3-mini should receive enhanced prompt with <reasoning> tags",
        "Response should be comprehensive architecture guide",
        "Should show reasoning mode and complexity indicators",
        "Response should be complete, not truncated"
    ]
    
    print(f"\nExpected behavior:")
    for behavior in expected_behavior:
        print(f"  ✅ {behavior}")
    
    fixes_applied = [
        "Made advanced_reasoning tool call MANDATORY for complex queries",
        "Added direct reasoning fallback when tool isn't called",
        "Enhanced search to fetch actual file content",
        "Improved reasoning prompt integration for O3 models"
    ]
    
    print(f"\nFixes applied:")
    for fix in fixes_applied:
        print(f"  🔧 {fix}")

if __name__ == "__main__":
    success = asyncio.run(test_user_query())
    analyze_user_output()
    
    print(f"\n🎯 Summary:")
    print(f"The user's query should now:")
    print(f"1. Trigger mandatory advanced_reasoning tool call")
    print(f"2. Get direct reasoning fallback if tool isn't called") 
    print(f"3. Receive comprehensive O3-optimized reasoning prompts")
    print(f"4. Generate complete architecture responses with <reasoning> tags")
    
    if success:
        print(f"\n✅ Fixes should resolve the incomplete response issue!")
    else:
        print(f"\n❌ There may still be configuration issues to resolve.")