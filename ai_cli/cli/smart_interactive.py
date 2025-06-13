import asyncio
import json
from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table

from ..core.config import AICliConfig
from ..core.context import ConversationContext, ContextToolCall
from ..core.tools import ToolExecutor, get_tool_definitions_for_ai, should_use_auto_detected_context
from ..providers.factory import ProviderFactory
from ..providers.base import AIMessage

console = Console()


class SmartInteractiveCLI:
    """Intelligent interactive CLI that automatically uses tools based on user queries."""
    
    def __init__(self):
        self.config = AICliConfig()
        self.config.load_config_file()
        self.context = ConversationContext(self.config)
        self.tool_executor = ToolExecutor(self.config, self.context)
        self.running = True
        
        # Check if we have any providers configured
        self._check_initial_setup()
    
    def _should_use_advanced_reasoning(self, user_message: str) -> bool:
        """Determine if a user message requires advanced reasoning capabilities."""
        query_lower = user_message.lower()
        
        # Complex reasoning indicators
        complex_indicators = [
            "architecture", "design pattern", "best practice", "optimization",
            "security", "performance", "scalability", "integration",
            "troubleshoot", "debug", "analyze", "compare", "evaluate",
            "system design", "distributed", "microservice", "concurrency",
            "algorithm complexity", "memory optimization", "race condition",
            "thread safety", "security vulnerability", "performance bottleneck",
            "how should i", "what's the best way", "design a", "implement a",
            "explain why", "explain how", "walk me through", "step by step"
        ]
        
        # Length and complexity heuristics
        word_count = len(user_message.split())
        has_complex_indicator = any(indicator in query_lower for indicator in complex_indicators)
        has_multiple_questions = user_message.count('?') > 1
        is_long_query = word_count > 15
        
        return has_complex_indicator or has_multiple_questions or is_long_query

    def _add_standard_tool_context(self, filtered_messages: List[AIMessage], tool_calls: List) -> None:
        """Add standard tool context for non-reasoning tools."""
        tool_context = "\n\nCode Context from your repositories:\n"
        for tool_call_record in tool_calls:
            if tool_call_record.result and not tool_call_record.result.get("error"):
                tool_context += f"\n--- {tool_call_record.name} results ---\n"
                tool_context += str(tool_call_record.result.get("message", ""))
                if tool_call_record.result.get("results"):
                    tool_context += f"\nFound {len(tool_call_record.result['results'])} examples in your repositories"
        
        # Update the last user message with context
        if filtered_messages and filtered_messages[-1].role == "user":
            filtered_messages[-1].content += tool_context

    def _check_initial_setup(self) -> bool:
        """Check if basic setup is complete."""
        has_ai_provider = False
        has_mcp_service = False
        
        # Check AI providers
        for provider_name in ["openai", "claude", "azure_openai"]:
            try:
                provider_config = self.config.get_provider_config(provider_name).model_dump()
                if provider_config.get("api_key"):
                    has_ai_provider = True
                    break
            except:
                continue
        
        # Check MCP services
        mcp_config = self.config.get_mcp_config()
        if mcp_config.github.auth_token or mcp_config.gitlab.auth_token:
            has_mcp_service = True
        
        if not has_ai_provider or not has_mcp_service:
            console.print(Panel(
                "[yellow]⚠️  Initial setup incomplete[/yellow]\n\n"
                f"AI Provider: {'✓' if has_ai_provider else '✗'} Configured\n"
                f"Code Access: {'✓' if has_mcp_service else '✗'} Configured\n\n"
                "Use --help to see setup commands for developers.",
                title="Setup Status"
            ))
        
        return has_ai_provider and has_mcp_service
    
    def show_welcome(self):
        """Show simplified welcome message."""
        git_info = ""
        if self.context.git_context:
            git_info = f"\n📁 Detected: {self.context.git_context['owner']}/{self.context.git_context['repo']} ({self.context.git_context['service']})"
        
        welcome_text = f"""
# 🤖 Cody - AI Code Assistant with Advanced Reasoning

I can help you understand, search, and analyze code from GitHub and GitLab repositories using advanced AI reasoning.
{git_info}

**🧠 Advanced AI Capabilities:**
- **NLP Search**: "websocket" finds socket.io, ws, realtime code automatically
- **Advanced Reasoning**: Complex questions get sophisticated analysis (o3, o1 models)
- **Multi-Modal Thinking**: Step-by-step, chain-of-thought, tree-of-thought reasoning
- **RAG for Your Code**: Prioritizes YOUR repositories as knowledge base

**🎯 Reasoning Modes (Automatic):**
- **Simple queries**: Step-by-step analysis
- **Complex problems**: Chain-of-thought reasoning  
- **Architecture questions**: Tree-of-thought exploration
- **Debugging**: Metacognitive analysis

**Just chat with me naturally:**
- "How should I design a scalable websocket architecture?" (→ Tree-of-thought)
- "Show me authentication patterns in my code" (→ NLP + your repos)
- "Debug this performance issue" (→ Metacognitive reasoning)
- "Compare these API design approaches" (→ Analytical reasoning)

**Special commands:**
- `/clear` - Clear conversation history
- `/context` - Show current context and cache
- `/help` - Show detailed help for developers
- `/exit` - Exit the application

**Examples with AI reasoning:**
- Complex: "scalable websocket architecture design" → o3 reasoning
- Simple: "websocket examples" → NLP search + analysis
- Debug: "performance bottleneck analysis" → metacognitive approach
        """
        console.print(Panel(Markdown(welcome_text), title="Welcome to Cody", border_style="blue"))
    
    def show_developer_help(self):
        """Show detailed help for developers (hidden from main interface)."""
        help_text = """
# 🛠️ Developer Commands & Setup

**Initial Setup:**
- `/setup openai` - Configure OpenAI API key
- `/setup claude` - Configure Claude API key
- `/setup azure` - Configure Azure OpenAI
- `/mcp add` - Add GitHub/GitLab access tokens

**Advanced Commands:**
- `/search <service> <query>` - Direct code search
- `/view <service> <owner/repo> <path>` - View specific file
- `/analyze <service> <question> --query <search>` - Analyze with AI
- `/providers` - Check AI provider status
- `/config` - Show configuration details

**Testing & Debugging:**
- `/mcp status` - Check MCP service connections
- `/mcp test <service>` - Test GitHub/GitLab connections

**Configuration:**
- Config file: `~/.ai-cli/config.yaml`
- Logs: `~/.ai-cli/logs/`
- Cache: Memory-based conversation context

**Tool Calling:**
The AI automatically uses these tools:
- `search_code` - Find relevant code examples
- `view_file` - Read complete file contents
- `analyze_code_context` - Provide detailed analysis

**Git Integration:**
- Auto-detects current repository context
- Prioritizes searches within detected repo
- Falls back to global search when needed
        """
        console.print(Panel(Markdown(help_text), title="Developer Reference", border_style="cyan"))
    
    def show_context(self):
        """Show current conversation context."""
        summary = self.context.get_context_summary()
        console.print(Panel(summary, title="Current Context", border_style="green"))
    
    async def process_user_message(self, user_message: str) -> None:
        """Process user message with AI and automatic tool calling."""
        
        # Add user message to context
        self.context.add_message(AIMessage(role="user", content=user_message))
        
        try:
            # Get AI provider
            provider_name = self.config.default_provider
            provider_config = self.config.get_provider_config(provider_name).model_dump()
            ai_provider = ProviderFactory.create_provider(provider_name, provider_config)
            
            async with ai_provider:
                # Prepare messages with context
                messages = self.context.get_recent_context()
                messages.append(AIMessage(role="user", content=user_message))
                
                # Check if current model supports tool calling
                current_model = provider_config.get("model", "gpt-4")
                
                # Get tool definitions
                tools = get_tool_definitions_for_ai()
                
                if current_model.startswith(("o3", "o1")):
                    console.print(f"[dim]🤔 Using GPT-4o for tools + {current_model} for reasoning...[/dim]")
                else:
                    console.print(f"[dim]🤔 Thinking with {provider_name}...[/dim]")
                
                # o3 and o1 models don't support function calling yet
                if current_model.startswith(("o3", "o1")):
                    # Use gpt-4o for tool calling, then o3 for final reasoning
                    tool_provider_config = provider_config.copy()
                    tool_provider_config["model"] = "gpt-4o"
                    tool_provider_config["max_tokens"] = 4000  # Use max_tokens for gpt-4o
                    if "max_completion_tokens" in tool_provider_config:
                        del tool_provider_config["max_completion_tokens"]  # Remove o3-specific param
                    tool_ai_provider = ProviderFactory.create_provider(provider_name, tool_provider_config)
                    
                    # Enhance the message to FORCE advanced reasoning for complex queries
                    enhanced_messages = messages.copy()
                    if self._should_use_advanced_reasoning(user_message):
                        reasoning_hint = f"\n\nIMPORTANT: This is a complex technical question that REQUIRES advanced reasoning. You MUST call the 'advanced_reasoning' tool with the following parameters:\n- query: \"{user_message}\"\n- domain: \"architecture\" (or appropriate technical domain)\n\nDo NOT just search for code - you MUST also use advanced_reasoning to provide sophisticated analysis with proper reasoning modes (step-by-step, chain-of-thought, tree-of-thought, etc.)."
                        if enhanced_messages and enhanced_messages[-1].role == "user":
                            enhanced_messages[-1] = AIMessage(
                                role="user", 
                                content=enhanced_messages[-1].content + reasoning_hint
                            )
                    
                    async with tool_ai_provider:
                        response = await tool_ai_provider.chat_completion(
                            enhanced_messages, 
                            tools=tools,
                            tool_choice="auto"
                        )
                else:
                    # Model supports tool calling directly
                    response = await ai_provider.chat_completion(
                        messages, 
                        tools=tools,
                        tool_choice="auto"
                    )
                
                tool_calls = []
                
                # Execute any tool calls
                if hasattr(response, 'tool_calls') and response.tool_calls:
                    console.print(f"[dim]🔧 Using {len(response.tool_calls)} tools...[/dim]")
                    
                    for tool_call in response.tool_calls:
                        console.print(f"[dim]  → {tool_call.function['name']}[/dim]")
                        
                        # Parse arguments
                        try:
                            arguments = json.loads(tool_call.function['arguments'])
                        except json.JSONDecodeError:
                            arguments = {}
                        
                        # Show NLP optimization details for search_code
                        if tool_call.function['name'] == 'search_code':
                            console.print(f"[dim]    🔍 Searching: {arguments.get('query', 'N/A')}[/dim]")
                            if arguments.get('owner'):
                                console.print(f"[dim]    👤 Owner: {arguments.get('owner')}[/dim]")
                        
                        # Execute tool
                        # If this is advanced_reasoning, pass code context from previous tools
                        if tool_call.function['name'] == 'advanced_reasoning':
                            # Collect code context from previously executed tools in this turn
                            code_context = []
                            for prev_tool in tool_calls:
                                if prev_tool.result and prev_tool.result.get("results"):
                                    for result_item in prev_tool.result.get("results", []):
                                        if result_item.get("content"):
                                            code_context.append({
                                                "repository": result_item.get("repository", "Unknown"),
                                                "path": result_item.get("path", "Unknown"),
                                                "content": result_item.get("content", "")[:2000],  # Limit content size
                                                "url": result_item.get("url", ""),
                                                "file": result_item.get("file", "")
                                            })
                            
                            # Add code_context to arguments if not already provided
                            if code_context and "code_context" not in arguments:
                                arguments["code_context"] = code_context
                        
                        result = await self.tool_executor.execute_tool(
                            tool_call.function['name'], 
                            arguments
                        )
                        
                        # Show enhanced search results info
                        if tool_call.function['name'] == 'search_code' and result.get('optimized_queries'):
                            console.print(f"[dim]    🧠 NLP expanded to: {len(result.get('optimized_queries', []))} queries[/dim]")
                            if result.get('intent', {}).get('primary_concept'):
                                console.print(f"[dim]    💡 Detected concept: {result['intent']['primary_concept']}[/dim]")
                        
                        # Show advanced reasoning info
                        if tool_call.function['name'] == 'advanced_reasoning':
                            console.print(f"[dim]    🧠 Reasoning mode: {result.get('reasoning_mode', 'N/A')}[/dim]")
                            console.print(f"[dim]    📊 Complexity: {result.get('complexity_level', 'N/A')}[/dim]")
                            console.print(f"[dim]    🎯 Domain: {result.get('domain', 'N/A')}[/dim]")
                            if result.get('model_optimized'):
                                console.print(f"[dim]    🤖 Optimized for: {result.get('model_optimized')}[/dim]")
                            if result.get('estimated_tokens'):
                                console.print(f"[dim]    📈 Estimated tokens: {result.get('estimated_tokens')}[/dim]")
                        
                        # Create tool call record
                        tool_call_record = ContextToolCall(
                            id=tool_call.id,
                            name=tool_call.function['name'],
                            arguments=arguments,
                            result=result
                        )
                        tool_calls.append(tool_call_record)
                    
                    # Build context for final response
                    final_messages = self.context.get_recent_context()
                    final_messages.append(AIMessage(role="user", content=user_message))
                    
                    # Add assistant message with tool calls (if any content)
                    if response.content:
                        final_messages.append(AIMessage(role="assistant", content=response.content))
                    
                    # Add tool results
                    for tool_call_record in tool_calls:
                        final_messages.append(AIMessage(
                            role="function",
                            content=json.dumps(tool_call_record.result),
                            name=tool_call_record.name
                        ))
                    
                    # Use o3-mini for final reasoning if available
                    if current_model.startswith(("o3", "o1")):
                        # Filter out function messages for o3 models
                        filtered_messages = [msg for msg in final_messages if msg.role != "function"]
                        
                        # Check if advanced_reasoning tool was called
                        advanced_reasoning_result = None
                        for tool_call_record in tool_calls:
                            if tool_call_record.name == "advanced_reasoning":
                                advanced_reasoning_result = tool_call_record.result
                                break
                        
                        if advanced_reasoning_result and not advanced_reasoning_result.get("error"):
                            # Use the enhanced reasoning prompt from advanced_reasoning tool
                            enhanced_prompt = advanced_reasoning_result.get("enhanced_prompt", "")
                            if enhanced_prompt:
                                console.print(f"[dim]🧠 Applying {advanced_reasoning_result.get('reasoning_mode', 'advanced')} reasoning mode...[/dim]")
                                
                                # Replace the user message with the enhanced reasoning prompt
                                if filtered_messages and filtered_messages[-1].role == "user":
                                    # Add code context from other tools to the enhanced prompt
                                    code_context = ""
                                    for tool_call_record in tool_calls:
                                        if tool_call_record.name != "advanced_reasoning" and tool_call_record.result and not tool_call_record.result.get("error"):
                                            if tool_call_record.result.get("results"):
                                                code_context += f"\nCode Examples from {tool_call_record.name}:\n"
                                                for i, result in enumerate(tool_call_record.result.get("results", [])[:3]):
                                                    code_context += f"Example {i+1}: {result.get('repository', 'Unknown')}/{result.get('path', 'Unknown')}\n"
                                                    if result.get('content'):
                                                        code_context += f"```\n{result.get('content', '')[:1000]}...\n```\n\n"
                                    
                                    # Combine enhanced prompt with code context
                                    full_reasoning_prompt = enhanced_prompt
                                    if code_context:
                                        full_reasoning_prompt += f"\n\nAdditional Code Context:\n{code_context}"
                                    
                                    filtered_messages[-1].content = full_reasoning_prompt
                            else:
                                # Fallback to original logic if no enhanced prompt
                                self._add_standard_tool_context(filtered_messages, tool_calls)
                        else:
                            # No advanced reasoning tool was called, but this is an o3 model
                            # Let's apply reasoning directly for complex queries
                            if self._should_use_advanced_reasoning(user_message):
                                console.print(f"[dim]🧠 Applying direct reasoning (advanced_reasoning tool not called)...[/dim]")
                                
                                # Generate reasoning prompt directly
                                try:
                                    # Collect any code context from search tools
                                    search_code_context = []
                                    for tool_call_record in tool_calls:
                                        if tool_call_record.name == "search_code" and tool_call_record.result.get("results"):
                                            for result in tool_call_record.result.get("results", [])[:3]:
                                                if result.get("content"):
                                                    search_code_context.append({
                                                        "repository": result.get("repository", "Unknown"),
                                                        "path": result.get("path", "Unknown"),
                                                        "content": result.get("content", "")[:2000],
                                                        "file": result.get("file", "Unknown")
                                                    })
                                    
                                    # Generate enhanced reasoning prompt
                                    from ..core.reasoning import AdvancedReasoningEngine
                                    reasoning_engine = AdvancedReasoningEngine()
                                    enhancement = reasoning_engine.enhance_query_for_reasoning(
                                        original_query=user_message,
                                        code_context=search_code_context,
                                        domain="architecture",
                                        model=current_model
                                    )
                                    
                                    reasoning_context = enhancement["reasoning_context"]
                                    enhanced_prompt = enhancement["enhanced_prompt"]["prompt"]
                                    
                                    console.print(f"[dim]📊 Direct reasoning mode: {reasoning_context.reasoning_mode.value}[/dim]")
                                    console.print(f"[dim]📈 Complexity: {reasoning_context.complexity.value}[/dim]")
                                    
                                    # Add any additional code context
                                    if search_code_context:
                                        code_context = "\n\nAdditional Code Context:\n"
                                        for i, result in enumerate(search_code_context):
                                            code_context += f"Example {i+1}: {result['repository']}/{result['path']}\n"
                                            code_context += f"```\n{result['content'][:1000]}...\n```\n\n"
                                        enhanced_prompt += code_context
                                    
                                    # Replace user message with enhanced prompt
                                    if filtered_messages and filtered_messages[-1].role == "user":
                                        filtered_messages[-1].content = enhanced_prompt
                                except Exception as e:
                                    console.print(f"[dim]⚠️ Direct reasoning failed: {e}, using standard context[/dim]")
                                    self._add_standard_tool_context(filtered_messages, tool_calls)
                            else:
                                # Simple query, use standard tool context
                                self._add_standard_tool_context(filtered_messages, tool_calls)
                        
                        final_response = await ai_provider.chat_completion(filtered_messages)
                    else:
                        final_response = await ai_provider.chat_completion(final_messages)
                    
                    ai_response_content = final_response.content or "I've gathered the information but couldn't generate a response."
                    tokens_used = getattr(final_response, 'usage', None)
                else:
                    # No tools needed, use direct response
                    ai_response_content = response.content or "I couldn't generate a response."
                    tokens_used = getattr(response, 'usage', None)
                
                # Display AI response
                console.print(f"\n[bold blue]Cody[/bold blue]:")
                console.print(Markdown(ai_response_content))
                
                if tokens_used:
                    console.print(f"\n[dim]Tokens: {tokens_used}[/dim]")
                
                # Add to conversation context
                self.context.add_conversation_turn(
                    user_message=user_message,
                    ai_response=ai_response_content,
                    tool_calls=tool_calls,
                    provider=provider_name,
                    tokens_used=tokens_used if hasattr(tokens_used, '__dict__') else None
                )
                
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            console.print("[dim]Try rephrasing your question or check your configuration.[/dim]")
    
    async def handle_setup_command(self, args: list):
        """Handle setup commands (imported from original implementation)."""
        # Import the original setup methods
        from .interactive import InteractiveCLI
        original_cli = InteractiveCLI()
        await original_cli.handle_setup_command(args)
        
        # Reload config after setup
        self.config.load_config_file()
    
    async def handle_mcp_command(self, args: list):
        """Handle MCP commands (imported from original implementation)."""
        from .interactive import InteractiveCLI
        original_cli = InteractiveCLI()
        await original_cli.handle_mcp_command(args)
        
        # Reload config after MCP changes
        self.config.load_config_file()
    
    async def handle_legacy_commands(self, command: str, args: list):
        """Handle legacy commands for developer access."""
        from .interactive import InteractiveCLI
        original_cli = InteractiveCLI()
        
        if command == "search":
            await original_cli.handle_search_command(args)
        elif command == "view":
            await original_cli.handle_view_command(args)
        elif command == "analyze":
            await original_cli.handle_analyze_command(args)
        elif command == "providers":
            await original_cli.handle_providers_command()
        elif command == "config":
            original_cli.handle_config_command()
    
    async def run(self):
        """Main interactive loop with simplified interface."""
        self.show_welcome()
        
        while self.running:
            try:
                user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]", default="").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.startswith("/"):
                    command_parts = user_input[1:].split()
                    command = command_parts[0].lower()
                    args = command_parts[1:] if len(command_parts) > 1 else []
                    
                    if command in ["exit", "quit", "q"]:
                        console.print("[green]Goodbye! 👋[/green]")
                        self.running = False
                        
                    elif command == "clear":
                        self.context.clear_context()
                        console.print("[green]✓ Conversation context cleared[/green]")
                        
                    elif command == "context":
                        self.show_context()
                        
                    elif command == "help":
                        self.show_developer_help()
                        
                    elif command == "setup":
                        await self.handle_setup_command(args)
                        
                    elif command == "mcp":
                        await self.handle_mcp_command(args)
                        
                    # Legacy developer commands
                    elif command in ["search", "view", "analyze", "providers", "config"]:
                        await self.handle_legacy_commands(command, args)
                        
                    else:
                        console.print(f"[red]Unknown command: /{command}[/red]")
                        console.print("[dim]Use /help for available commands[/dim]")
                else:
                    # Process as natural language with AI
                    await self.process_user_message(user_input)
                    
            except KeyboardInterrupt:
                console.print("\n[green]Goodbye! 👋[/green]")
                self.running = False
            except Exception as e:
                console.print(f"[red]Unexpected error: {e}[/red]")


async def main():
    """Main entry point for smart interactive mode."""
    cli = SmartInteractiveCLI()
    await cli.run()


if __name__ == "__main__":
    asyncio.run(main())