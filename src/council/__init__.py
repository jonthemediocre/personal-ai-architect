#!/usr/bin/env python3
"""
Trinity Council - Multi-Agent Decision System
Strategist: Plans and proposes
Skeptic: Challenges and finds flaws  
Guardian: Evaluates risk and cost
Moderator: Reconciles and decides
"""

from dataclasses import dataclass, field
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
    proposed_by: str  # domain
    timestamp: datetime
    domain: str  # personal or work
    priority: int  # 1-5
    external_action: bool = False
    estimated_cost: float = 0.0
    risk_level: str = "low"
    votes: Dict[str, str] = field(default_factory=dict)  # role: vote

class CouncilMember:
    def __init__(self, role: AgentRole):
        self.role = role
        self.system_prompt = ""
        
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
        if proposal.risk_level in ["high", "critical"]:
            concerns.append(f"Risk level is {proposal.risk_level}")
        if proposal.priority > 4:
            concerns.append("Very high priority needs justification")
            
        return {
            "role": self.role.value,
            "position": "Questions and concerns raised",
            "rating": "reject" if proposal.risk_level == "critical" else ("conditional" if concerns else "support"),
            "reasoning": f"Found {len(concerns)} concern(s)" if concerns else "No major issues",
            "concerns": concerns
        }
    
    def _evaluate_guardian(self, proposal: Proposal) -> Dict:
        if proposal.risk_level == "critical":
            return {
                "role": self.role.value,
                "position": "Safety and cost assessment",
                "rating": "reject",
                "reasoning": f"Risk: CRITICAL - cannot approve"
            }
        elif proposal.risk_level == "high" and proposal.estimated_cost > 100:
            return {
                "role": self.role.value,
                "position": "Safety and cost assessment",
                "rating": "conditional",
                "reasoning": f"High risk (${proposal.estimated_cost}) needs approval"
            }
        else:
            return {
                "role": self.role.value,
                "position": "Safety and cost assessment",
                "rating": "approved",
                "reasoning": f"Risk: {proposal.risk_level}, Cost: ${proposal.estimated_cost}"
            }
    
    def _evaluate_moderator(self, proposal: Proposal) -> Dict:
        # Count votes from evaluations
        ratings = {
            AgentRole.STRATEGIST: "support",
            AgentRole.SKEPTIC: "conditional",
            AgentRole.GUARDIAN: "approved",
        }
        
        # Get actual ratings from evaluations (would come from LLM in real system)
        approvals = 0
        rejections = 0
        
        for role, rating in ratings.items():
            if rating in ["support", "approved"]:
                approvals += 1
            elif rating == "reject":
                rejections += 1
            elif rating == "conditional":
                # Conditional counts as half approval
                approvals += 0.5
        
        decision = "approved" if approvals > rejections else "rejected"
        
        return {
            "role": self.role.value,
            "position": "Final decision",
            "rating": decision,
            "reasoning": f"{approvals:.1f} approvals vs {rejections:.1f} rejections",
            "consensus_reached": approvals >= 2
        }

class TrinityCouncil:
    def __init__(self):
        self.members = {
            AgentRole.STRATEGIST: CouncilMember(AgentRole.STRATEGIST),
            AgentRole.SKEPTIC: CouncilMember(AgentRole.SKEPTIC),
            AgentRole.GUARDIAN: CouncilMember(AgentRole.GUARDIAN),
            AgentRole.MODERATOR: CouncilMember(AgentRole.MODERATOR)
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
            proposed_by=domain,
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
        votes = {}
        
        # Each member evaluates
        for role, member in self.members.items():
            result = member.evaluate(proposal)
            results[role] = result
            votes[role.value] = result["rating"]
        
        # Moderator makes final call
        moderator_result = results[AgentRole.MODERATOR]
        
        decision = {
            "proposal_id": proposal.id,
            "title": proposal.title,
            "domain": proposal.domain,
            "timestamp": datetime.now().isoformat(),
            "council_votes": votes,
            "council_analysis": {
                role.value: {
                    "rating": r["rating"],
                    "reasoning": r["reasoning"]
                }
                for role, r in results.items()
            },
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
