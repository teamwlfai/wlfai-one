"""
AI Agent management and interaction models
"""

from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Text,
    Integer,
    Numeric,
    ForeignKey,
    Enum,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import BaseModel
from .enums import AgentType, AgentStatus, InteractionStatus


class Agent(BaseModel):
    """AI agents for healthcare automation"""

    __tablename__ = "agents"

    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    type = Column(Enum(AgentType), nullable=False)
    status = Column(Enum(AgentStatus), default=AgentStatus.INACTIVE, nullable=False)
    config = Column(JSONB, default=dict)
    api_keys = Column(JSONB, default=dict)  # Encrypted API keys for external services
    version = Column(String(50), default="1.0.0")
    metrics = Column(JSONB, default=dict)
    is_public = Column(Boolean, default=False)

    __table_args__ = (
        Index("idx_agent_org", "org_id"),
        Index("idx_agent_type", "type"),
        Index("idx_agent_status", "status"),
        Index("idx_agent_org_type", "org_id", "type"),
        Index("idx_agent_public", "is_public"),
    )

    # Relationships
    organization = relationship("Organization", back_populates="agents")
    interactions = relationship(
        "AgentInteraction", back_populates="agent", cascade="all, delete-orphan"
    )
    workflows = relationship("Workflow", back_populates="agent")

    @property
    def is_active(self):
        """Check if agent is active"""
        return self.status == AgentStatus.ACTIVE

    @property
    def is_training(self):
        """Check if agent is in training mode"""
        return self.status == AgentStatus.TRAINING

    @property
    def total_interactions(self):
        """Get total interaction count from metrics"""
        return self.metrics.get("total_interactions", 0)

    @property
    def success_rate(self):
        """Get success rate from metrics"""
        return self.metrics.get("success_rate", 0.0)

    @property
    def average_response_time(self):
        """Get average response time from metrics"""
        return self.metrics.get("avg_response_time_ms", 0)

    @property
    def total_cost(self):
        """Get total cost from metrics"""
        return self.metrics.get("total_cost_usd", 0.0)

    def update_metrics(self, interaction_data):
        """Update agent metrics with new interaction data"""
        current_metrics = self.metrics or {}

        # Update counters
        current_metrics["total_interactions"] = (
            current_metrics.get("total_interactions", 0) + 1
        )
        current_metrics["total_cost_usd"] = current_metrics.get(
            "total_cost_usd", 0.0
        ) + interaction_data.get("cost", 0.0)

        # Update averages
        total_interactions = current_metrics["total_interactions"]
        current_avg_time = current_metrics.get("avg_response_time_ms", 0)
        new_response_time = interaction_data.get("response_time_ms", 0)

        current_metrics["avg_response_time_ms"] = (
            current_avg_time * (total_interactions - 1) + new_response_time
        ) / total_interactions

        # Update success rate
        if interaction_data.get("status") == InteractionStatus.COMPLETED:
            successful = current_metrics.get("successful_interactions", 0) + 1
            current_metrics["successful_interactions"] = successful
            current_metrics["success_rate"] = (successful / total_interactions) * 100

        self.metrics = current_metrics
        return current_metrics


class AgentInteraction(BaseModel):
    """Individual agent interactions with patients/users"""

    __tablename__ = "agent_interactions"

    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"))
    type = Column(
        String(100), nullable=False
    )  # appointment_booking, reminder, triage, etc.
    status = Column(
        Enum(InteractionStatus), default=InteractionStatus.STARTED, nullable=False
    )
    input_data = Column(JSONB, default=dict)
    output_data = Column(JSONB, default=dict)
    metadata = Column(JSONB, default=dict)
    response_time_ms = Column(Integer, default=0)
    total_cost_usd = Column(Numeric(10, 4), default=0)
    total_credits_consumed = Column(Integer, default=0)
    service_breakdown = Column(JSONB, default=dict)  # Cost breakdown by service
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

    __table_args__ = (
        Index("idx_interaction_agent", "agent_id"),
        Index("idx_interaction_org", "org_id"),
        Index("idx_interaction_patient", "patient_id"),
        Index("idx_interaction_type", "type"),
        Index("idx_interaction_status", "status"),
        Index("idx_interaction_started", "started_at"),
        Index("idx_interaction_completed", "completed_at"),
        Index("idx_interaction_org_type", "org_id", "type"),
    )

    # Relationships
    agent = relationship("Agent", back_populates="interactions")
    organization = relationship("Organization")
    patient = relationship("Patient", back_populates="agent_interactions")
    service_consumptions = relationship(
        "ServiceConsumption", back_populates="interaction"
    )

    @property
    def is_completed(self):
        """Check if interaction is completed"""
        return self.status == InteractionStatus.COMPLETED

    @property
    def is_failed(self):
        """Check if interaction failed"""
        return self.status == InteractionStatus.FAILED

    @property
    def is_in_progress(self):
        """Check if interaction is in progress"""
        return self.status == InteractionStatus.IN_PROGRESS

    @property
    def duration_seconds(self):
        """Calculate interaction duration in seconds"""
        if self.completed_at and self.started_at:
            delta = self.completed_at - self.started_at
            return delta.total_seconds()
        return 0

    @property
    def cost_per_second(self):
        """Calculate cost per second of interaction"""
        duration = self.duration_seconds
        if duration > 0 and self.total_cost_usd:
            return float(self.total_cost_usd) / duration
        return 0

    @property
    def success_indicator(self):
        """Get success indicator from output data"""
        return self.output_data.get("success", False)

    def mark_completed(
        self, output_data=None, cost_usd=0, credits_consumed=0, service_breakdown=None
    ):
        """Mark interaction as completed with results"""
        self.status = InteractionStatus.COMPLETED
        self.completed_at = func.now()

        if output_data:
            self.output_data = output_data

        self.total_cost_usd = cost_usd
        self.total_credits_consumed = credits_consumed

        if service_breakdown:
            self.service_breakdown = service_breakdown

        # Calculate response time if not set
        if self.response_time_ms == 0 and self.duration_seconds > 0:
            self.response_time_ms = int(self.duration_seconds * 1000)

    def mark_failed(self, error_message=None):
        """Mark interaction as failed with optional error message"""
        self.status = InteractionStatus.FAILED
        self.completed_at = func.now()

        if error_message:
            error_data = self.output_data or {}
            error_data["error"] = error_message
            self.output_data = error_data

    def add_service_consumption(
        self,
        service_type,
        provider,
        model,
        input_units=0,
        output_units=0,
        cost_usd=0,
        credits=0,
    ):
        """Add service consumption data to the interaction"""
        breakdown = self.service_breakdown or {}

        service_key = f"{service_type}_{provider}_{model}"
        breakdown[service_key] = {
            "service_type": service_type,
            "provider": provider,
            "model": model,
            "input_units": input_units,
            "output_units": output_units,
            "cost_usd": float(cost_usd),
            "credits": credits,
        }

        self.service_breakdown = breakdown

        # Update totals
        self.total_cost_usd = sum(s.get("cost_usd", 0) for s in breakdown.values())
        self.total_credits_consumed = sum(
            s.get("credits", 0) for s in breakdown.values()
        )

    def get_conversation_history(self):
        """Extract conversation history from input/output data"""
        history = []

        # Add input messages
        if self.input_data.get("messages"):
            history.extend(self.input_data["messages"])

        # Add output messages
        if self.output_data.get("messages"):
            history.extend(self.output_data["messages"])

        # Sort by timestamp if available
        try:
            history.sort(key=lambda x: x.get("timestamp", ""))
        except:
            pass

        return history

    def get_performance_metrics(self):
        """Get performance metrics for this interaction"""
        return {
            "duration_seconds": self.duration_seconds,
            "response_time_ms": self.response_time_ms,
            "total_cost_usd": float(self.total_cost_usd or 0),
            "credits_consumed": self.total_credits_consumed,
            "cost_per_second": self.cost_per_second,
            "success": self.success_indicator,
            "status": self.status.value,
            "service_count": len(self.service_breakdown or {}),
        }
