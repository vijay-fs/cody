#!/usr/bin/env python3

"""Test script to verify local search functionality works."""

import asyncio
import sys
import os

# Add the current directory to path so we can import our modules
sys.path.insert(0, '/Users/Ghost/Desktop/dev/cody')

from ai_cli.cli.interactive import InteractiveCLI

async def test_local_search():
    """Test the local search functionality."""
    cli = InteractiveCLI()
    
    print("Testing local search for 'websocket'...")
    
    # Test the search functionality directly
    matches = cli.search_files_with_ripgrep("websocket", ".", None)
    
    if matches:
        print(f"Found {len(matches)} matches:")
        for match in matches[:5]:
            print(f"  - {match['file']}:{match['line_number']} - {match['line_content'][:100]}")
    else:
        print("No matches found for 'websocket'")
    
    print("\nTesting local search for 'python'...")
    matches = cli.search_files_with_ripgrep("python", ".", ["py"])
    
    if matches:
        print(f"Found {len(matches)} matches in Python files:")
        for match in matches[:5]:
            print(f"  - {match['file']}:{match['line_number']} - {match['line_content'][:100]}")
    else:
        print("No matches found for 'python' in .py files")

if __name__ == "__main__":
    asyncio.run(test_local_search())