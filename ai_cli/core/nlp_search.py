from typing import List, Dict, Set, Tuple
import re


class SemanticSearchOptimizer:
    """Optimizes search queries using NLP techniques for better code discovery."""
    
    def __init__(self):
        # Semantic mapping of concepts to actual code terms
        self.concept_mappings = {
            # WebSocket related terms
            "websocket": [
                "websocket", "ws", "socket.io", "socketio", "realtime", "real-time",
                "live", "push", "streaming", "connection", "emit", "on(", "broadcast",
                "room", "namespace", "io.on", "socket.on", "WebSocket", "eventEmitter"
            ],
            
            # Authentication related terms
            "authentication": [
                "auth", "login", "signin", "signup", "register", "jwt", "token",
                "session", "passport", "oauth", "firebase", "supabase", "nextauth",
                "middleware", "protect", "guard", "authorize", "credential"
            ],
            
            # Database related terms
            "database": [
                "db", "database", "sql", "nosql", "mongo", "postgres", "mysql",
                "prisma", "mongoose", "sequelize", "typeorm", "knex", "query",
                "collection", "table", "model", "schema"
            ],
            
            # API related terms
            "api": [
                "api", "endpoint", "route", "handler", "controller", "service",
                "rest", "graphql", "fetch", "axios", "request", "response",
                "post", "get", "put", "delete", "patch"
            ],
            
            # Frontend framework terms
            "react": [
                "react", "jsx", "tsx", "component", "hook", "useState", "useEffect",
                "context", "provider", "reducer", "props", "state"
            ],
            
            # Next.js specific terms
            "nextjs": [
                "next", "nextjs", "app", "pages", "router", "routing", "getServerSideProps",
                "getStaticProps", "dynamic", "middleware", "api/", "_app", "_document"
            ],
            
            # S3 and cloud storage
            "s3": [
                "s3", "aws", "bucket", "upload", "download", "presigned", "cloudfront",
                "storage", "file", "blob", "multipart", "putObject", "getObject"
            ],
            
            # Error handling
            "error": [
                "error", "exception", "try", "catch", "throw", "ErrorBoundary",
                "handle", "validation", "fail", "reject", "status"
            ]
        }
        
        # File extension context for better targeting
        self.extension_contexts = {
            "frontend": [".tsx", ".jsx", ".ts", ".js", ".vue", ".svelte"],
            "backend": [".py", ".go", ".rs", ".java", ".php", ".rb"],
            "config": [".json", ".yaml", ".yml", ".toml", ".env"],
            "database": [".sql", ".prisma", ".schema"],
            "api": ["/api/", "/routes/", "/controllers/", "/handlers/"]
        }
        
        # Common code patterns that indicate functionality
        self.functionality_patterns = {
            "websocket": [
                "socket\\.io", "ws://", "wss://", "WebSocket", "io\\.", "socket\\.",
                "emit\\(", "on\\(.*message", "broadcast", "room", "namespace"
            ],
            "authentication": [
                "jwt\\.sign", "passport", "bcrypt", "hash", "verify", "login",
                "authenticate", "authorize", "session", "cookie"
            ],
            "database": [
                "findMany", "findFirst", "create", "update", "delete", "where",
                "include", "select", "connect", "collection\\."
            ],
            "file_upload": [
                "multer", "formData", "FileReader", "blob", "upload", "multipart"
            ]
        }
    
    def expand_query(self, query: str) -> List[str]:
        """Expand a natural language query into multiple search terms."""
        expanded_queries = []
        query_lower = query.lower()
        
        # Add original query
        expanded_queries.append(query)
        
        # Find matching concepts and expand
        for concept, related_terms in self.concept_mappings.items():
            if concept in query_lower:
                # Add related terms as separate queries
                for term in related_terms[:5]:  # Limit to top 5 related terms
                    expanded_queries.append(f"{term}")
                    
                # Create combined queries
                if len(related_terms) > 0:
                    expanded_queries.append(f"{related_terms[0]} {related_terms[1] if len(related_terms) > 1 else ''}")
        
        # Extract and expand individual words
        words = re.findall(r'\b\w+\b', query_lower)
        for word in words:
            if len(word) > 3:  # Skip short words
                for concept, related_terms in self.concept_mappings.items():
                    if word in concept or any(word in term for term in related_terms):
                        expanded_queries.extend(related_terms[:3])
                        break
        
        # Remove duplicates while preserving order
        seen = set()
        unique_queries = []
        for q in expanded_queries:
            if q.lower() not in seen:
                seen.add(q.lower())
                unique_queries.append(q)
        
        return unique_queries[:8]  # Limit to 8 queries to avoid API rate limits
    
    def get_contextual_searches(self, query: str, detected_languages: List[str] = None) -> List[Dict[str, str]]:
        """Generate contextual search queries based on detected patterns."""
        searches = []
        query_lower = query.lower()
        
        # Basic expanded search
        expanded = self.expand_query(query)
        for term in expanded:
            searches.append({
                "query": term,
                "context": "expanded",
                "priority": 1 if term == query else 2
            })
        
        # Add file extension specific searches
        if "frontend" in query_lower or "react" in query_lower or "component" in query_lower:
            for term in expanded[:3]:
                searches.append({
                    "query": f"{term} extension:tsx",
                    "context": "frontend",
                    "priority": 1
                })
                searches.append({
                    "query": f"{term} extension:jsx",
                    "context": "frontend", 
                    "priority": 2
                })
        
        if "backend" in query_lower or "api" in query_lower or "server" in query_lower:
            for term in expanded[:3]:
                searches.append({
                    "query": f"{term} extension:ts",
                    "context": "backend",
                    "priority": 1
                })
                searches.append({
                    "query": f"{term} extension:js",
                    "context": "backend",
                    "priority": 2
                })
        
        # Add pattern-based searches
        for concept, patterns in self.functionality_patterns.items():
            if concept in query_lower:
                for pattern in patterns[:2]:  # Top 2 patterns
                    searches.append({
                        "query": pattern,
                        "context": f"pattern_{concept}",
                        "priority": 1
                    })
        
        # Sort by priority and remove duplicates
        unique_searches = {}
        for search in searches:
            key = search["query"].lower()
            if key not in unique_searches or unique_searches[key]["priority"] > search["priority"]:
                unique_searches[key] = search
        
        return sorted(unique_searches.values(), key=lambda x: x["priority"])[:6]
    
    def extract_intent(self, query: str) -> Dict[str, any]:
        """Extract user intent and suggest search strategy."""
        query_lower = query.lower()
        
        intent = {
            "primary_concept": None,
            "search_type": "general",
            "suggested_extensions": [],
            "search_strategy": "broad"
        }
        
        # Identify primary concept
        for concept in self.concept_mappings.keys():
            if concept in query_lower:
                intent["primary_concept"] = concept
                break
        
        # Determine search type
        if any(word in query_lower for word in ["how", "implement", "create", "build"]):
            intent["search_type"] = "implementation"
            intent["search_strategy"] = "pattern_focused"
        elif any(word in query_lower for word in ["example", "show", "find"]):
            intent["search_type"] = "examples"
            intent["search_strategy"] = "broad"
        elif any(word in query_lower for word in ["error", "debug", "fix", "issue"]):
            intent["search_type"] = "troubleshooting"
            intent["search_strategy"] = "error_focused"
        
        # Suggest file extensions based on context
        if intent["primary_concept"] in ["react", "nextjs"]:
            intent["suggested_extensions"] = [".tsx", ".jsx", ".ts"]
        elif intent["primary_concept"] in ["websocket", "api"]:
            intent["suggested_extensions"] = [".ts", ".js", ".py"]
        elif intent["primary_concept"] == "database":
            intent["suggested_extensions"] = [".prisma", ".sql", ".ts", ".js"]
        
        return intent
    
    def optimize_for_codebase(self, query: str, language_context: str = None) -> List[str]:
        """Optimize search queries specifically for code discovery."""
        optimized_queries = []
        
        # Get intent and expand query
        intent = self.extract_intent(query)
        expanded = self.expand_query(query)
        
        # Strategy 1: Direct term search
        optimized_queries.extend(expanded[:3])
        
        # Strategy 2: Function/method pattern search
        if intent["search_type"] == "implementation":
            concept = intent["primary_concept"]
            if concept and concept in self.functionality_patterns:
                patterns = self.functionality_patterns[concept]
                optimized_queries.extend(patterns[:2])
        
        # Strategy 3: File path based search
        if intent["suggested_extensions"]:
            for ext in intent["suggested_extensions"][:2]:
                optimized_queries.append(f"{expanded[0]} extension:{ext[1:]}")
        
        # Strategy 4: Import/dependency search
        if intent["primary_concept"]:
            concept = intent["primary_concept"]
            if concept == "websocket":
                optimized_queries.extend(["import.*socket", "require.*socket"])
            elif concept == "authentication":
                optimized_queries.extend(["import.*auth", "require.*passport"])
            elif concept == "s3":
                optimized_queries.extend(["import.*aws", "require.*aws"])
        
        return optimized_queries[:8]


def enhance_search_with_nlp(query: str, optimizer: SemanticSearchOptimizer = None) -> Dict[str, any]:
    """Main function to enhance a search query with NLP optimizations."""
    if not optimizer:
        optimizer = SemanticSearchOptimizer()
    
    return {
        "original_query": query,
        "expanded_queries": optimizer.expand_query(query),
        "contextual_searches": optimizer.get_contextual_searches(query),
        "intent": optimizer.extract_intent(query),
        "optimized_queries": optimizer.optimize_for_codebase(query)
    }