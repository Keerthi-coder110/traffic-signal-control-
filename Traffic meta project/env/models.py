from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum


class SignalPhase(str, Enum):
    """Traffic signal phases"""
    NORTH_SOUTH_GREEN = "ns_green"
    EAST_WEST_GREEN = "ew_green"
    ALL_RED = "all_red"


class DisruptionType(str, Enum):
    """Types of traffic disruptions"""
    LANE_CLOSURE = "lane_closure"
    DEMAND_SPIKE = "demand_spike"
    SENSOR_FAILURE = "sensor_failure"
    NONE = "none"


class IntersectionState(BaseModel):
    """State of a single intersection"""
    intersection_id: int
    queue_lengths: Dict[str, int] = Field(
        description="Queue length for each direction (north, south, east, west)"
    )
    waiting_times: Dict[str, float] = Field(
        description="Average waiting time for each direction"
    )
    current_phase: SignalPhase
    phase_duration: int = Field(description="Time remaining in current phase")
    active_disruption: DisruptionType = DisruptionType.NONE
    disruption_severity: float = Field(default=0.0, ge=0.0, le=1.0)


class Observation(BaseModel):
    """Environment observation"""
    intersections: List[IntersectionState]
    total_vehicles: int
    total_waiting_time: float
    throughput: int = Field(description="Vehicles that passed through in last step")
    timestep: int
    disruptions_active: int = Field(description="Number of active disruptions")


class Action(BaseModel):
    """Agent action"""
    intersection_id: int = Field(description="Which intersection to control")
    new_phase: SignalPhase = Field(description="New signal phase to set")
    duration: int = Field(default=10, ge=5, le=60, description="Duration in seconds")


class TrafficState(BaseModel):
    """Complete environment state"""
    observation: Observation
    reward: float
    done: bool
    info: Dict = Field(default_factory=dict)
