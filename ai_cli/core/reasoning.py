from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json


class ReasoningMode(Enum):
    """Different reasoning modes for different types of queries."""
    STEP_BY_STEP = "step_by_step"
    CHAIN_OF_THOUGHT = "chain_of_thought"
    TREE_OF_THOUGHT = "tree_of_thought"
    METACOGNITIVE = "metacognitive"
    SOCRATIC = "socratic"
    ANALYTICAL = "analytical"


class ComplexityLevel(Enum):
    """Complexity levels for reasoning tasks."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    EXPERT = "expert"


@dataclass
class ReasoningContext:
    """Context for reasoning about code queries."""
    query: str
    complexity: ComplexityLevel
    reasoning_mode: ReasoningMode
    domain: str  # e.g., "authentication", "websocket", "database"
    code_context: List[Dict[str, Any]]
    user_intent: str
    constraints: List[str]


class AdvancedReasoningEngine:
    """Advanced reasoning engine for complex code analysis and problem solving."""
    
    def __init__(self):
        self.reasoning_templates = {
            ReasoningMode.STEP_BY_STEP: self._step_by_step_template,
            ReasoningMode.CHAIN_OF_THOUGHT: self._chain_of_thought_template,
            ReasoningMode.TREE_OF_THOUGHT: self._tree_of_thought_template,
            ReasoningMode.METACOGNITIVE: self._metacognitive_template,
            ReasoningMode.SOCRATIC: self._socratic_template,
            ReasoningMode.ANALYTICAL: self._analytical_template,
        }
        
        # Model capabilities mapping
        self.reasoning_models = {
            "o1-mini": {
                "supports_reasoning": True,
                "reasoning_token_limit": 65536,
                "best_modes": [ReasoningMode.CHAIN_OF_THOUGHT, ReasoningMode.STEP_BY_STEP],
                "complexity_limit": ComplexityLevel.EXPERT
            },
            "o1": {
                "supports_reasoning": True,
                "reasoning_token_limit": 200000,
                "best_modes": [ReasoningMode.TREE_OF_THOUGHT, ReasoningMode.METACOGNITIVE],
                "complexity_limit": ComplexityLevel.EXPERT
            },
            "o3-mini": {
                "supports_reasoning": True,
                "reasoning_token_limit": 100000,
                "best_modes": [ReasoningMode.CHAIN_OF_THOUGHT, ReasoningMode.ANALYTICAL],
                "complexity_limit": ComplexityLevel.EXPERT
            },
            "o3": {
                "supports_reasoning": True,
                "reasoning_token_limit": 300000,
                "best_modes": [ReasoningMode.TREE_OF_THOUGHT, ReasoningMode.METACOGNITIVE, ReasoningMode.SOCRATIC],
                "complexity_limit": ComplexityLevel.EXPERT
            },
            "claude-3-5-sonnet": {
                "supports_reasoning": True,
                "reasoning_token_limit": 200000,
                "best_modes": [ReasoningMode.ANALYTICAL, ReasoningMode.SOCRATIC],
                "complexity_limit": ComplexityLevel.EXPERT
            }
        }
    
    def analyze_query_complexity(self, query: str, code_context: List[Dict] = None) -> Tuple[ComplexityLevel, str]:
        """Analyze the complexity of a user query and determine reasoning requirements."""
        query_lower = query.lower()
        
        # Simple indicators
        simple_indicators = [
            "what is", "how to", "show me", "find", "example of",
            "basic", "simple", "quick"
        ]
        
        # Complex indicators
        complex_indicators = [
            "architecture", "design pattern", "best practice", "optimization",
            "security", "performance", "scalability", "integration",
            "troubleshoot", "debug", "analyze", "compare", "evaluate"
        ]
        
        # Expert indicators
        expert_indicators = [
            "system design", "distributed", "microservice", "concurrency",
            "algorithm complexity", "memory optimization", "race condition",
            "thread safety", "security vulnerability", "performance bottleneck"
        ]
        
        # Multiple code files or repositories
        code_complexity = 0
        if code_context:
            code_complexity = len(code_context)
            if code_complexity > 10:
                return ComplexityLevel.EXPERT, "Multiple complex codebases"
            elif code_complexity > 5:
                return ComplexityLevel.COMPLEX, "Multiple code files"
        
        # Check indicators
        if any(indicator in query_lower for indicator in expert_indicators):
            return ComplexityLevel.EXPERT, "Expert-level concepts detected"
        elif any(indicator in query_lower for indicator in complex_indicators):
            return ComplexityLevel.COMPLEX, "Complex technical concepts"
        elif any(indicator in query_lower for indicator in simple_indicators):
            return ComplexityLevel.SIMPLE, "Basic query pattern"
        else:
            return ComplexityLevel.MODERATE, "Moderate complexity"
    
    def select_reasoning_mode(self, query: str, complexity: ComplexityLevel, domain: str) -> ReasoningMode:
        """Select the best reasoning mode for the given query and complexity."""
        query_lower = query.lower()
        
        # Intent-based mode selection
        if any(word in query_lower for word in ["how", "implement", "create", "build"]):
            if complexity in [ComplexityLevel.COMPLEX, ComplexityLevel.EXPERT]:
                return ReasoningMode.TREE_OF_THOUGHT
            else:
                return ReasoningMode.STEP_BY_STEP
        
        elif any(word in query_lower for word in ["why", "explain", "understand"]):
            return ReasoningMode.SOCRATIC
        
        elif any(word in query_lower for word in ["compare", "analyze", "evaluate"]):
            return ReasoningMode.ANALYTICAL
        
        elif any(word in query_lower for word in ["debug", "fix", "error", "issue"]):
            return ReasoningMode.METACOGNITIVE
        
        elif any(word in query_lower for word in ["architecture", "design", "pattern"]):
            return ReasoningMode.TREE_OF_THOUGHT
        
        else:
            # Default based on complexity
            if complexity == ComplexityLevel.EXPERT:
                return ReasoningMode.TREE_OF_THOUGHT
            elif complexity == ComplexityLevel.COMPLEX:
                return ReasoningMode.CHAIN_OF_THOUGHT
            else:
                return ReasoningMode.STEP_BY_STEP
    
    def create_reasoning_context(
        self,
        query: str,
        code_context: List[Dict[str, Any]] = None,
        user_intent: str = None,
        domain: str = None
    ) -> ReasoningContext:
        """Create a comprehensive reasoning context for the query."""
        complexity, complexity_reason = self.analyze_query_complexity(query, code_context)
        reasoning_mode = self.select_reasoning_mode(query, complexity, domain or "general")
        
        # Extract constraints from query
        constraints = []
        if "without" in query.lower():
            constraints.append("Avoid mentioned technologies")
        if "security" in query.lower():
            constraints.append("Security-first approach")
        if "performance" in query.lower():
            constraints.append("Performance optimization")
        if "simple" in query.lower():
            constraints.append("Keep it simple")
        
        return ReasoningContext(
            query=query,
            complexity=complexity,
            reasoning_mode=reasoning_mode,
            domain=domain or "general",
            code_context=code_context or [],
            user_intent=user_intent or "understand",
            constraints=constraints
        )
    
    def _step_by_step_template(self, context: ReasoningContext) -> str:
        """Template for step-by-step reasoning."""
        return f"""
<reasoning>
I need to analyze this query step by step:

Query: "{context.query}"
Domain: {context.domain}
Complexity: {context.complexity.value}
Code Context: {len(context.code_context)} files/examples

Step 1: Understanding the Question
- What exactly is the user asking?
- What is the core problem or need?
- What level of detail is expected?

Step 2: Analyzing Available Code Context
- What relevant code examples do I have?
- How do these examples relate to the query?
- What patterns or approaches are evident?

Step 3: Identifying Key Concepts
- What are the main technical concepts involved?
- What are the dependencies and relationships?
- What are potential challenges or considerations?

Step 4: Structuring the Response
- How can I best explain this to the user?
- What order should I present the information?
- What examples or code snippets would be most helpful?

Step 5: Validation and Completeness
- Does my response fully address the query?
- Are there any gaps or missing information?
- Should I suggest follow-up questions or next steps?
</reasoning>

Based on my step-by-step analysis of your query about {context.domain}, here's my comprehensive response:
"""
    
    def _chain_of_thought_template(self, context: ReasoningContext) -> str:
        """Template for chain of thought reasoning."""
        return f"""
<reasoning>
Let me think through this systematically:

First, I'm analyzing the query "{context.query}" in the context of {context.domain}. 

The user seems to be looking for {context.user_intent}, and given the {context.complexity.value} complexity level, I need to consider multiple aspects:

1. Technical Implementation: How would this actually work in practice?
2. Code Architecture: What patterns and structures are involved?
3. Best Practices: What are the recommended approaches?
4. Potential Issues: What could go wrong and how to avoid it?

Looking at the available code context ({len(context.code_context)} examples), I can see patterns that relate to:
- Implementation approaches
- Common pitfalls and solutions
- Real-world usage examples

The key insight here is that this isn't just about showing code, but about understanding the underlying principles and how they apply to the user's specific situation.

Given the constraints: {', '.join(context.constraints) if context.constraints else 'None specified'}, I need to tailor my response accordingly.

This leads me to conclude that the best approach is to...
</reasoning>

After thinking through your question about {context.domain}, here's my analysis:
"""
    
    def _tree_of_thought_template(self, context: ReasoningContext) -> str:
        """Template for tree of thought reasoning (exploring multiple paths)."""
        return f"""
<reasoning>
I'll explore multiple approaches to answer this query about {context.domain}:

Branch A: Direct Implementation Approach
- Pros: Straightforward, easy to understand
- Cons: May not cover edge cases
- Best for: Immediate solutions

Branch B: Architectural Design Approach  
- Pros: Scalable, maintainable, robust
- Cons: More complex upfront
- Best for: Long-term systems

Branch C: Best Practices Approach
- Pros: Industry-standard, well-tested
- Cons: May be overkill for simple cases
- Best for: Production systems

Branch D: Learning-Oriented Approach
- Pros: Educational, builds understanding
- Cons: Takes more time
- Best for: Skill development

Evaluating the paths:
Given the complexity level ({context.complexity.value}) and user intent ({context.user_intent}), I should combine elements from multiple branches.

The optimal path appears to be: Start with Branch A for immediate understanding, then incorporate elements from Branch B for proper architecture, and reference Branch C for validation.

This hybrid approach will provide both immediate value and long-term guidance.
</reasoning>

I've explored several approaches to your {context.domain} question. Here's my comprehensive analysis combining the best elements:
"""
    
    def _metacognitive_template(self, context: ReasoningContext) -> str:
        """Template for metacognitive reasoning (thinking about thinking)."""
        return f"""
<reasoning>
I need to think about how I'm thinking about this problem:

Meta-Question: What type of reasoning is most appropriate here?
- The query is about {context.domain}
- The complexity is {context.complexity.value}
- The user wants to {context.user_intent}

What do I know?
- I have {len(context.code_context)} code examples
- I understand the technical domain
- I can see patterns and relationships

What don't I know?
- The user's specific context and constraints
- Their level of expertise
- Their ultimate goals beyond this query

How should I approach this?
- I should start with what's most directly relevant
- I should provide multiple levels of detail
- I should acknowledge uncertainties and assumptions

What biases might I have?
- Tendency to over-engineer solutions
- Assumption about user's technical level
- Preference for certain technologies or approaches

How can I validate my reasoning?
- Check against the actual code examples
- Consider alternative perspectives
- Think about potential counterarguments

Am I answering the right question?
- Re-reading the query: "{context.query}"
- The core need seems to be...
- I should focus on...
</reasoning>

Let me think carefully about your question regarding {context.domain}. Here's my thoughtful analysis:
"""
    
    def _socratic_template(self, context: ReasoningContext) -> str:
        """Template for Socratic reasoning (questioning approach)."""
        return f"""
<reasoning>
Let me explore this through a series of guiding questions:

What is the user really asking?
- Surface question: "{context.query}"
- Deeper question: What problem are they trying to solve?
- Meta question: What do they need to learn or understand?

What assumptions am I making?
- About their technical level?
- About their use case?
- About their constraints?

What questions should the user be asking themselves?
- Is this the right approach for their situation?
- What are the trade-offs they should consider?
- What don't they know that they should know?

What would a Socratic dialogue look like?
- "Why do you need this particular solution?"
- "What have you tried before?"
- "What constraints are you working within?"
- "How will you know if this solution is successful?"

How can I guide discovery rather than just provide answers?
- Show the thinking process
- Highlight decision points
- Explain the reasoning behind choices
- Encourage critical thinking
</reasoning>

Great question about {context.domain}! Rather than just giving you an answer, let me guide you through the thinking process:
"""
    
    def _analytical_template(self, context: ReasoningContext) -> str:
        """Template for analytical reasoning (systematic analysis)."""
        return f"""
<reasoning>
Systematic Analysis Framework:

1. Problem Decomposition:
   - Primary components of "{context.query}"
   - Sub-problems and dependencies
   - Critical vs. non-critical elements

2. Context Analysis:
   - Domain: {context.domain}
   - Complexity: {context.complexity.value}
   - Available examples: {len(context.code_context)}
   - Constraints: {context.constraints}

3. Solution Space Mapping:
   - Possible approaches (enumerate all)
   - Feasibility assessment
   - Resource requirements
   - Risk factors

4. Comparative Analysis:
   - Pros/cons of each approach
   - Performance implications
   - Maintainability factors
   - Security considerations

5. Decision Matrix:
   - Weighted criteria based on context
   - Scoring of alternatives
   - Sensitivity analysis

6. Implementation Strategy:
   - Phased approach
   - Validation checkpoints
   - Rollback strategies
   - Success metrics

7. Future Considerations:
   - Scalability implications
   - Evolution paths
   - Technical debt assessment
</reasoning>

Here's my systematic analysis of your {context.domain} question:
"""
    
    def generate_reasoning_prompt(
        self,
        context: ReasoningContext,
        model: str = "o3-mini"
    ) -> Dict[str, Any]:
        """Generate a reasoning-optimized prompt for the given context and model."""
        
        # Get model capabilities
        model_caps = self.reasoning_models.get(model, {
            "supports_reasoning": False,
            "best_modes": [ReasoningMode.STEP_BY_STEP],
            "complexity_limit": ComplexityLevel.MODERATE
        })
        
        # Adjust reasoning mode if model doesn't support it well
        if context.reasoning_mode not in model_caps.get("best_modes", []):
            context.reasoning_mode = model_caps["best_modes"][0]
        
        # Get the appropriate template
        template_func = self.reasoning_templates[context.reasoning_mode]
        reasoning_template = template_func(context)
        
        # Build the complete prompt
        prompt_parts = [
            "You are an expert code assistant with advanced reasoning capabilities.",
            f"You're analyzing a {context.complexity.value} complexity query about {context.domain}.",
            "",
            reasoning_template,
            "",
            "Code Context:",
        ]
        
        # Add code context
        for i, code in enumerate(context.code_context[:5]):  # Limit to 5 examples
            prompt_parts.append(f"Example {i+1}: {code.get('repository', 'Unknown')}/{code.get('path', 'Unknown')}")
            if code.get('content'):
                prompt_parts.append(f"```\n{code['content'][:1000]}...\n```")
            prompt_parts.append("")
        
        # Add specific instructions for reasoning models
        if model_caps["supports_reasoning"]:
            prompt_parts.extend([
                "Instructions for reasoning:",
                "1. Show your complete reasoning process in <reasoning> tags",
                "2. Break down complex problems systematically",
                "3. Consider multiple perspectives and approaches",
                "4. Validate your reasoning against the provided code examples",
                "5. Explain trade-offs and decision factors",
                "6. Provide actionable insights and next steps",
                "",
                f"Reasoning mode: {context.reasoning_mode.value}",
                f"Constraints: {', '.join(context.constraints) if context.constraints else 'None'}",
                ""
            ])
        
        return {
            "prompt": "\n".join(prompt_parts),
            "reasoning_mode": context.reasoning_mode.value,
            "complexity": context.complexity.value,
            "model_optimized": model,
            "supports_reasoning": model_caps["supports_reasoning"]
        }
    
    def enhance_query_for_reasoning(
        self,
        original_query: str,
        code_context: List[Dict] = None,
        domain: str = None,
        model: str = "o3-mini"
    ) -> Dict[str, Any]:
        """Main entry point to enhance a query with advanced reasoning."""
        
        # Create reasoning context
        context = self.create_reasoning_context(
            query=original_query,
            code_context=code_context,
            domain=domain
        )
        
        # Generate reasoning-optimized prompt
        reasoning_prompt = self.generate_reasoning_prompt(context, model)
        
        return {
            "original_query": original_query,
            "reasoning_context": context,
            "enhanced_prompt": reasoning_prompt,
            "recommendations": {
                "best_model": self._recommend_model(context),
                "reasoning_mode": context.reasoning_mode.value,
                "complexity_level": context.complexity.value,
                "estimated_tokens": self._estimate_tokens(context)
            }
        }
    
    def _recommend_model(self, context: ReasoningContext) -> str:
        """Recommend the best model for the given reasoning context."""
        if context.complexity == ComplexityLevel.EXPERT:
            return "o3"  # Most capable reasoning model
        elif context.complexity == ComplexityLevel.COMPLEX:
            return "o3-mini"  # Good balance of capability and speed
        elif context.reasoning_mode in [ReasoningMode.SOCRATIC, ReasoningMode.ANALYTICAL]:
            return "claude-3-5-sonnet"  # Excellent at detailed analysis
        else:
            return "o1-mini"  # Fast reasoning for simpler tasks
    
    def _estimate_tokens(self, context: ReasoningContext) -> int:
        """Estimate token usage for the reasoning task."""
        base_tokens = len(context.query.split()) * 1.3  # Rough token estimation
        
        # Add context tokens
        context_tokens = sum(len(str(code).split()) for code in context.code_context) * 1.3
        
        # Add reasoning overhead based on mode
        reasoning_overhead = {
            ReasoningMode.STEP_BY_STEP: 500,
            ReasoningMode.CHAIN_OF_THOUGHT: 800,
            ReasoningMode.TREE_OF_THOUGHT: 1500,
            ReasoningMode.METACOGNITIVE: 1200,
            ReasoningMode.SOCRATIC: 1000,
            ReasoningMode.ANALYTICAL: 2000
        }
        
        total = base_tokens + context_tokens + reasoning_overhead.get(context.reasoning_mode, 500)
        return int(total)