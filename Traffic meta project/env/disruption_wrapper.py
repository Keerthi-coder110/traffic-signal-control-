import numpy as np
from typing import Tuple, Dict, Any
from .traffic_env import TrafficSignalEnv
from .models import Observation, Action, DisruptionType


class DisruptionWrapper:
    """
    Wrapper that injects realistic disruptions into the traffic environment.
    This enables training robust agents that can handle unexpected events.
    """
    
    def __init__(
        self,
        env: TrafficSignalEnv,
        disruption_probability: float = 0.1,
        disruption_duration_range: Tuple[int, int] = (20, 100),
        severity_range: Tuple[float, float] = (0.3, 0.8)
    ):
        self.env = env
        self.disruption_probability = disruption_probability
        self.disruption_duration_range = disruption_duration_range
        self.severity_range = severity_range
        
        # Track active disruptions
        self.disruption_timers = {}
    
    def reset(self) -> Observation:
        """Reset environment and disruption tracking"""
        self.disruption_timers = {}
        return self.env.reset()
    
    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict[str, Any]]:
        """Step with potential disruption injection"""
        # Randomly inject new disruptions
        if np.random.random() < self.disruption_probability:
            self._inject_random_disruption()
        
        # Execute environment step
        obs, reward, done, info = self.env.step(action)
        
        # Update disruption timers
        self._update_disruptions()
        
        # Add disruption info
        info["disruptions"] = {
            k: {"type": v["type"], "remaining": v["remaining"]}
            for k, v in self.disruption_timers.items()
        }
        
        return obs, reward, done, info
    
    def state(self):
        """Return current state"""
        return self.env.state()
    
    def _inject_random_disruption(self):
        """Inject a random disruption at a random intersection"""
        # Choose random intersection
        intersection_id = np.random.randint(0, self.env.num_intersections)
        
        # Skip if already disrupted
        if intersection_id in self.disruption_timers:
            return
        
        # Choose disruption type
        disruption_types = [
            DisruptionType.LANE_CLOSURE,
            DisruptionType.DEMAND_SPIKE,
            DisruptionType.SENSOR_FAILURE
        ]
        disruption_type = np.random.choice(disruption_types)
        
        # Choose severity and duration
        severity = np.random.uniform(*self.severity_range)
        duration = np.random.randint(*self.disruption_duration_range)
        
        # Inject disruption
        self.env.inject_disruption(intersection_id, disruption_type, severity)
        
        # Track timer
        self.disruption_timers[intersection_id] = {
            "type": disruption_type,
            "remaining": duration,
            "severity": severity
        }
    
    def _update_disruptions(self):
        """Update and clear expired disruptions"""
        expired = []
        
        for intersection_id, timer in self.disruption_timers.items():
            timer["remaining"] -= 1
            
            if timer["remaining"] <= 0:
                self.env.clear_disruption(intersection_id)
                expired.append(intersection_id)
        
        # Remove expired timers
        for intersection_id in expired:
            del self.disruption_timers[intersection_id]
