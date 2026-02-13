#!/usr/bin/env python3
"""
Dual-Domain Memory System
Personal and Work contexts with automatic memory consolidation
"""

import os
import json
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
MEMORY_DIR = BASE_DIR / "memory"

@dataclass
class MemoryEntry:
    id: str
    timestamp: str
    category: str  # project, decision, lesson, fact, preference
    domain: str  # personal or work
    content: str
    importance: int  # 1-5
    tags: List[str] = field(default_factory=list)
    source: Optional[str] = None
    
    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "category": self.category,
            "domain": self.domain,
            "content": self.content,
            "importance": self.importance,
            "tags": self.tags,
            "source": self.source
        }

class MemoryStore:
    def __init__(self, domain: str):
        self.domain = domain
        self.memory_dir = MEMORY_DIR / domain
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.learnings_file = self.memory_dir / "LEARNINGS.md"
        self.memory_file = self.memory_dir / "MEMORY.md"
        self.daily_dir = self.memory_dir / "daily"
        self.daily_dir.mkdir(exist_ok=True)
        self._entries: Dict[str, MemoryEntry] = {}
        self._load_existing()
        
    def _load_existing(self):
        """Load existing memory entries"""
        if self.learnings_file.exists():
            # Parse learnings markdown
            pass  # Would parse existing file
        
    def add(self, category: str, content: str, importance: int = 3, 
            tags: List[str] = None, source: str = None) -> MemoryEntry:
        """Add a new memory entry"""
        entry = MemoryEntry(
            id=f"mem_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            timestamp=datetime.now().isoformat(),
            category=category,
            domain=self.domain,
            content=content,
            importance=importance,
            tags=tags or [],
            source=source
        )
        self._entries[entry.id] = entry
        self._save_entry(entry)
        return entry
    
    def _save_entry(self, entry: MemoryEntry):
        """Save entry to daily log"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        daily_file = self.daily_dir / f"{date_str}.md"
        
        with open(daily_file, 'a') as f:
            f.write(f"\n## {entry.timestamp} - {entry.category}\n")
            f.write(f"**Importance:** {'⭐' * entry.importance}\n")
            f.write(f"**Tags:** {', '.join(entry.tags)}\n\n")
            f.write(f"{entry.content}\n")
    
    def query(self, query: str, category: str = None, 
              min_importance: int = 3, limit: int = 10) -> List[MemoryEntry]:
        """Query memories by content or category"""
        results = []
        for entry in self._entries.values():
            if entry.importance < min_importance:
                continue
            if category and entry.category != category:
                continue
            if query.lower() in entry.content.lower():
                results.append(entry)
        return results[:limit]
    
    def get_recent(self, days: int = 7) -> List[MemoryEntry]:
        """Get recent memories"""
        cutoff = datetime.now() - timedelta(days=days)
        return [e for e in self._entries.values() 
                if datetime.fromisoformat(e.timestamp) > cutoff]
    
    def export_context(self, for_model: str = None) -> str:
        """Export memory as context string for LLM"""
        context_parts = []
        context_parts.append(f"# {self.domain.upper()} MEMORY CONTEXT")
        context_parts.append(f"Generated: {datetime.now().isoformat()}")
        
        # Recent learnings
        recent = self.get_recent(30)
        if recent:
            context_parts.append("\n## Recent Learnings")
            for entry in recent[-20:]:
                context_parts.append(f"- [{entry.category}] {entry.content[:200]}")
        
        # Important facts
        important = [e for e in self._entries.values() if e.importance >= 4]
        if important:
            context_parts.append("\n## Important Facts")
            for entry in important[:10]:
                context_parts.append(f"- {entry.content}")
        
        return "\n".join(context_parts)

class DualDomainMemory:
    """Wrapper for both personal and work memory"""
    def __init__(self):
        self.personal = MemoryStore("personal")
        self.work = MemoryStore("work")
        
    def add_personal(self, category: str, content: str, importance: int = 3,
                     tags: List[str] = None, source: str = None):
        return self.personal.add(category, content, importance, tags, source)
    
    def add_work(self, category: str, content: str, importance: int = 3,
                 tags: List[str] = None, source: str = None):
        return self.work.add(category, content, importance, tags, source)
    
    def query_all(self, query: str, domain: str = None) -> Dict:
        """Query across domains"""
        results = {}
        if domain in [None, "personal"]:
            results["personal"] = self.personal.query(query)
        if domain in [None, "work"]:
            results["work"] = self.work.query(query)
        return results
    
    def get_context(self, domain: str = "personal") -> str:
        """Get memory context for a domain"""
        if domain == "personal":
            return self.personal.export_context()
        elif domain == "work":
            return self.work.export_context()
        else:
            # Combined context
            return self.personal.export_context() + "\n\n" + self.work.export_context()

if __name__ == "__main__":
    # Test
    memory = DualDomainMemory()
    
    # Add some memories
    memory.add_personal(
        category="preference",
        content="Prefers concise responses over verbose explanations",
        importance=4,
        tags=["communication", "preference"]
    )
    
    memory.add_work(
        category="project",
        content="Building Personal AI Architect with dual-domain architecture",
        importance=5,
        tags=["project", "architecture", "openclaw"]
    )
    
    # Query
    results = memory.query_all("architecture")
    print("Query Results:", json.dumps(results, default=lambda x: x.to_dict() if hasattr(x, 'to_dict') else str(x), indent=2))
