#!/usr/bin/env python3
"""
Natural Language Command Parser for Personal AI Architect
Parses freeform text into actionable commands
"""

import re
from typing import Tuple, Optional, Dict, List
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class Intent(Enum):
    STATUS = "status"
    SWITCH_DOMAIN = "switch_domain"
    REMEMBER = "remember"
    QUERY_MEMORY = "query_memory"
    SUBMIT_PROPOSAL = "submit_proposal"
    RUN_CRONS = "run_crons"
    HELP = "help"
    UNKNOWN = "unknown"

@dataclass
class ParsedCommand:
    intent: Intent
    entities: Dict = None
    raw: str = ""
    
    def __post_init__(self):
        if self.entities is None:
            self.entities = {}

class NLParser:
    """Natural language parser for Personal AI Architect"""
    
    def __init__(self):
        self.intent_patterns = {
            Intent.STATUS: [
                r"^(status|how are you|system status|what's happening|what is happening)",
                r"show me.*status",
            ],
            Intent.SWITCH_DOMAIN: [
                r"switch to (personal|work)",
                r"use (personal|work) domain",
                r"change to (personal|work)",
                r"i want to (work|use personal)",
                r"(personal|work) mode",
            ],
            Intent.REMEMBER: [
                r"remember (.*)",
                r"note that (.*)",
                r"remind me that (.*)",
                r"i (hate|like|love|prefer|need|want) (.*)",
                r"save (.*) to memory",
                r"store (.*)",
            ],
            Intent.QUERY_MEMORY: [
                r"what do i remember about (.*)",
                r"do i remember (.*)",
                r"search memory for (.*)",
                r"query memory (.*)",
                r"what.*memory",
                r"recall (.*)",
                r"find.*(in|about) memory",
            ],
            Intent.SUBMIT_PROPOSAL: [
                r"propose (.*)",
                r"submit proposal (.*)",
                r"i think we should (.*)",
                r"we should (.*)",
                r"let's (.*)",
                r"could we (.*)",
                r"(?:make|create) a proposal (?:to |about |that )?(.*)",
            ],
            Intent.RUN_CRONS: [
                r"run (cron|backup|heartbeat|check)",
                r"execute (cron|scheduled) jobs",
                r"run all crons",
                r"check system health",
            ],
            Intent.HELP: [
                r"help",
                r"what can you do",
                r"commands",
                r"how do i use you",
            ],
        }
        
        self.entity_extractors = {
            "domain": [
                (r"(personal|work)", 1),
            ],
            "importance": [
                (r"important|critical|urgent", 4),
                (r"very.*important", 4),
                (r"somewhat.*important", 3),
                (r"not.*important", 1),
                (r"default", 3),
            ],
            "priority": [
                (r"high.*priority|urgent|critical", 5),
                (r"medium.*priority", 3),
                (r"low.*priority", 1),
            ],
        }
    
    def parse(self, text: str) -> ParsedCommand:
        """Parse natural language into command"""
        text = text.lower().strip()
        raw = text
        
        # Check each intent
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    entities = self._extract_entities(text, intent)
                    return ParsedCommand(
                        intent=intent,
                        entities=entities,
                        raw=raw
                    )
        
        return ParsedCommand(intent=Intent.UNKNOWN, raw=raw)
    
    def _extract_entities(self, text: str, intent: Intent) -> Dict:
        """Extract named entities from text"""
        entities = {}
        
        # Domain extraction
        if intent == Intent.SWITCH_DOMAIN:
            match = re.search(r"(personal|work)", text)
            if match:
                entities["domain"] = match.group(1)
        
        # Priority/importance extraction
        if intent in [Intent.REMEMBER, Intent.SUBMIT_PROPOSAL]:
            for level, (pattern, value) in enumerate([
                (r"(very |super |extremely )?important", 4),
                (r"critical|urgent|asap", 5),
                (r"not.*important|minor|small", 2),
            ]):
                if re.search(pattern, text):
                    entities["importance"] = value
                    break
        
        # Content extraction (everything after trigger words)
        if intent == Intent.REMEMBER:
            triggers = ["remember ", "note that ", "remind me that ", 
                       "i hate ", "i like ", "i love ", "i prefer ",
                       "i need ", "i want ", "save ", "store "]
            for trigger in triggers:
                if trigger in text:
                    content = text.split(trigger, 1)[-1].strip()
                    if content:
                        entities["content"] = content
                    break
        
        elif intent == Intent.QUERY_MEMORY:
            triggers = ["what do i remember about ", "do i remember ",
                       "search memory for ", "query memory ", "recall ",
                       "find in memory ", "find about memory "]
            for trigger in triggers:
                if trigger in text:
                    query = text.split(trigger, 1)[-1].strip().rstrip("?")
                    if query:
                        entities["query"] = query
                    break
        
        elif intent == Intent.SUBMIT_PROPOSAL:
            triggers = ["propose ", "submit proposal ", "i think we should ",
                       "we should ", "let's ", "could we ",
                       "make a proposal ", "create a proposal "]
            for trigger in triggers:
                if trigger in text:
                    proposal = text.split(trigger, 1)[-1].strip()
                    # Try to split title and description
                    if " because " in proposal:
                        parts = proposal.split(" because ", 1)
                        entities["title"] = parts[0].strip()
                        entities["description"] = parts[1].strip()
                    elif " for " in proposal:
                        parts = proposal.split(" for ", 1)
                        entities["title"] = parts[0].strip()
                        entities["description"] = parts[1].strip()
                    else:
                        entities["title"] = proposal
                        entities["description"] = proposal
                    break
        
        # Default importance
        if "importance" not in entities and intent == Intent.REMEMBER:
            entities["importance"] = 3
        if "priority" not in entities and intent == Intent.SUBMIT_PROPOSAL:
            entities["priority"] = 3
            
        return entities

class ConversationManager:
    """Conversational interface for Personal AI Architect"""
    
    def __init__(self, architect):
        self.architect = architect
        self.parser = NLParser()
        self.conversation_history: List[Dict] = []
        
    def process(self, message: str) -> str:
        """Process a natural language message"""
        # Parse intent
        parsed = self.parser.parse(message)
        
        # Log conversation
        self.conversation_history.append({
            "input": message,
            "intent": parsed.intent.value,
            "entities": parsed.entities,
            "timestamp": str(datetime.now())
        })
        
        # Execute command
        response = self._execute(parsed)
        
        # Log response
        self.conversation_history[-1]["response"] = response
        
        return response
    
    def _execute(self, parsed: ParsedCommand) -> str:
        """Execute parsed command"""
        e = parsed.entities
        
        if parsed.intent == Intent.STATUS:
            return self.architect.get_status()
        
        elif parsed.intent == Intent.SWITCH_DOMAIN:
            domain = e.get("domain", "personal")
            return self.architect.switch_domain(domain)
        
        elif parsed.intent == Intent.REMEMBER:
            content = e.get("content", parsed.raw.replace("remember", "").strip())
            importance = e.get("importance", 3)
            return self.architect.add_memory(
                category="note",
                content=content,
                importance=importance
            )
        
        elif parsed.intent == Intent.QUERY_MEMORY:
            query = e.get("query", parsed.raw.replace("remember", "").replace("about", "").strip())
            return self.architect.query_memory(query)
        
        elif parsed.intent == Intent.SUBMIT_PROPOSAL:
            title = e.get("title", "Untitled Proposal")
            description = e.get("description", title)
            priority = e.get("priority", 3)
            return self.architect.submit_proposal(
                title=title,
                description=description,
                priority=priority
            )
        
        elif parsed.intent == Intent.RUN_CRONS:
            return self.architect.run_crons()
        
        elif parsed.intent == Intent.HELP:
            return self._get_help()
        
        else:
            return self._get_help()
    
    def _get_help(self) -> str:
        """Show help"""
        return """# Personal AI Architect - Natural Language Commands

Talk to me naturally! Examples:

**Status & System**
- "How are you?"
- "Show me system status"
- "What's happening?"

**Domain Switching**
- "Switch to work"
- "Use personal domain"
- "I want to work"

**Memory**
- "Remember that I hate meetings"
- "Note that I prefer email over Slack"
- "What do I remember about projects?"
- "Search memory for deadlines"
- "Do I remember anything about budget?"

**Proposals**
- "Propose we should have daily standups"
- "Let's automate the backup process"
- "We should review the weekly goals"
- "Create a proposal to reduce meeting time"

**System**
- "Run heartbeat check"
- "Check system health"
- "Run all crons"

**Other**
- "Help"
- "What can you do?"

Just talk naturally - I'll understand!"""

if __name__ == "__main__":
    # Quick test
    parser = NLParser()
    
    test_inputs = [
        "switch to work",
        "remember that I hate meetings",
        "what do i remember about projects",
        "propose we should have daily standups",
        "status",
        "let's automate backups",
    ]
    
    print("NL Parser Test")
    print("=" * 60)
    
    for text in test_inputs:
        result = parser.parse(text)
        print(f"\nInput: '{text}'")
        print(f"Intent: {result.intent.value}")
        print(f"Entities: {result.entities}")
