#!/usr/bin/env python3
"""
Trinity Council - Multi-Agent Decision System
Strategist: Plans and proposes
Skeptic: Challenges and finds flaws  
Guardian: Evaluates risk and cost
Moderator: Reconciles and decides
"""

from dataclasses import dataclass
from typing import List, Optional, Dict
from enum import Enum
from datetime import datetime
import json

class AgentRole(Enum):
    STRATEGIST = "strategist"
    SKEPTIC = "skeptic"
    GUARDIAN = "guardian"
    MODERATOR = "moderator"

@dataclass
class Proposal:
    id: str
    title: str
    description: str
    proposed_by: AgentRole
    timestamp: datetime
    domain: str  # personal or work
    priority: int  # 1-5
    external_action: bool = False
    estimated_cost: float = 0.0
    risk_level: str = "low"
    votes: Dict[AgentRole, str] = None  # approve, reject, abstain

    def __post_init__(self):
        if self.votes is None:
            self.votes = {}

class CouncilMember:
    def __init__(self, role: AgentRole, system_prompt: str):
        self.role = role
        self.system_prompt = system_prompt
        self.position = ""
        self.concerns = []
        self.vote = None
        
    def evaluate(self, proposal: Proposal) -> Dict:
        """Each member evaluates the proposal based on their role"""
        if self.role == AgentRole.STRATEGIST:
            return self._evaluate_strategist(proposal)
        elif self.role == AgentRole.SKEPTIC:
            return self._evaluate_skeptic(proposal)
        elif self.role == AgentRole.GUARDIAN:
            return self._evaluate_guardian(proposal)
        elif self.role == AgentRole.MODERATOR:
            return self._evaluate_moderator(proposal)
            
    def _evaluate_strategist(self, proposal: Proposal) -> Dict:
        return {
            "role": self.role.value,
            "position": "This proposal aligns with long-term goals",
            "rating": "support",
            "reasoning": f"Strategic fit for {proposal.domain} domain"
        }
    
    def _evaluate_skeptic(self, proposal: Proposal) -> Dict:
        concerns = []
        if proposal.external_action:
            concerns.append("External action requires explicit approval")
        if proposal.risk_level == "high":
            concerns.append("Risk level is high - needs mitigation")
        if not proposal.votes:
            concerns.append("No consensus yet")
            
        return {
            "role": self.role.value,
            "position": "Questions and concerns raised",
            "rating": "conditional" if concerns else "support",
            "reasoning": f"Found {len(concerns)} concern(s)" if concerns else "No major issues",
            "concerns": concerns
        }
    
    def _evaluate_guardian(self, proposal: Proposal) -> Dict:
        return {
            "role": self.role.value,
            "position": "Safety and cost assessment",
            "rating": "approved" if proposal.risk_level != "critical" else "reject",
            "reasoning": f"Risk: {proposal.risk_level}, Cost: ${proposal.estimated_cost}",
            "requires_approval": proposal.external_action
        }
    
    def _evaluate_moderator(self, proposal: Proposal) -> Dict:
        approvals = sum(1 for v in proposal.votes.values() if v == "approve")
        rejections = sum(1 for v in proposal.votes.values() if v == "reject")
        
        return {
            "role": self.role.value,
            "position": "Final decision",
            "rating": "approved" if approvals > rejections else "rejected",
            "reasoning": f"{approvals} approvals, {rejections} rejections",
            "consensus_reached": approvals >= 2
        }

class TrinityCouncil:
    def __init__(self):
        self.members = {
            AgentRole.STRATEGIST: CouncilMember(
                AgentRole.STRATEGIST,
                "You focus on long-term alignment and strategic value."
            ),
            AgentRole.SKEPTIC: CouncilMember(
                AgentRole.SKEPTIC,
                "You challenge assumptions and find weaknesses."
            ),
            AgentRole.GUARDIAN: CouncilMember(
                AgentRole.GUARDIAN,
                "You assess risk, cost, and safety implications."
            ),
            AgentRole.MODERATOR: CouncilMember(
                AgentRole.MODERATOR,
                "You facilitate discussion and make final decisions."
            )
        }
        self.proposals: List[Proposal] = []
        self.decisions: List[Dict] = []
        
    def submit_proposal(self, title: str, description: str, domain: str, 
                       priority: int = 3, external_action: bool = False,
                       estimated_cost: float = 0.0, risk_level: str = "low") -> Proposal:
        """Submit a new proposal to the council"""
        proposal = Proposal(
            id=f"prop_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            title=title,
            description=description,
            proposed_by=AgentRole.STRATEGIST,
            timestamp=datetime.now(),
            domain=domain,
            priority=priority,
            external_action=external_action,
            estimated_cost=estimated_cost,
            risk_level=risk_level
        )
        self.proposals.append(proposal)
        return proposal
    
    def deliberated(self, proposal: Proposal) -> Dict:
        """Run full council deliberation on a proposal"""
        results = {}
        
        # Each member evaluates
        for role, member in self.members.items():
            results[role.value] = member.evaluate(proposal)
            
        # Count votes
        votes = {role.value: results[role.value]["rating"] for role in self.members}
        
        # Moderator makes final call
        moderator_result = results[AgentRole.MODERATOR.value]
        
        decision = {
            "proposal_id": proposal.id,
            "title": proposal.title,
            "domain": proposal.domain,
            "timestamp": datetime.now().isoformat(),
            "council_votes": votes,
            "decision": moderator_result["rating"],
            "reasoning": moderator_result["reasoning"],
            "consensus": moderator_result["consensus_reached"],
            "requires_human_approval": proposal.external_action and moderator_result["rating"] != "approved"
        }
        
        self.decisions.append(decision)
        
        return decision
    
    def get_pending_proposals(self) -> List[Dict]:
        """Get proposals awaiting decision"""
        decided_ids = {d["proposal_id"] for d in self.decisions}
        return [
            {
                "id": p.id,
                "title": p.title,
                "domain": p.domain,
                "priority": p.priority,
                "external_action": p.external_action
            }
            for p in self.proposals if p.id not in decided_ids
        ]
    
    def export_decisions(self, filepath: str = "council_decisions.json"):
        """Export all decisions to JSON"""
        with open(filepath, 'w') as f:
            json.dump(self.decisions, f, indent=2, default=str)
        return filepath

if __name__ == "__main__":
    # Quick test
    council = TrinityCouncil()
    
    # Submit a proposal
    proposal = council.submit_proposal(
        title="Deploy new automation script",
        description="Create automated backup system for personal files",
        domain="personal",
        priority=4,
        external_action=True,
        estimated_cost=0.50,
        risk_level="low"
    )
    
    # Run deliberation
    decision = council.deliberated(proposal)
    
    print("=" * 60)
    print("COUNCIL DECISION")
    print("=" * 60)
    print(f"Proposal: {decision['title']}")
    print(f"Domain: {decision['domain']}")
    print(f"Decision: {decision['decision'].upper()}")
    print(f"Consensus: {decision['consensus']}")
    print(f"Human Approval Required: {decision['requires_human_approval']}")
    print("=" * 60)
