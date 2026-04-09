import numpy as np
from typing import Tuple, Dict, Any
from .models import (
    Observation, Action, TrafficState, IntersectionState,
    SignalPhase, DisruptionType
)


class TrafficSignalEnv:
    """
    OpenEnv-compliant traffic signal control environment.
    Simulates realistic traffic flow with support for disruptions.
    """
    
    def __init__(self, num_intersections: int = 1, max_steps: int = 500):
        self.num_intersections = num_intersections
        self.max_steps = max_steps
        self.current_step = 0
        
        # Traffic parameters
        self.arrival_rate = 0.3  # Vehicles per second per lane
        self.service_rate = 0.5  # Vehicles per second when green
        
        # State tracking
        self.intersections_state = []
        self.total_throughput = 0
        self.episode_reward = 0.0
        
        # Disruption tracking
        self.active_disruptions = {}
        
    def reset(self) -> Observation:
        """Reset environment to initial state"""
        self.current_step = 0
        self.total_throughput = 0
        self.episode_reward = 0.0
        self.active_disruptions = {}
        
        # Initialize intersections
        self.intersections_state = []
        for i in range(self.num_intersections):
            intersection = IntersectionState(
                intersection_id=i,
                queue_lengths={"north": 5, "south": 5, "east": 5, "west": 5},
                waiting_times={"north": 10.0, "south": 10.0, "east": 10.0, "west": 10.0},
                current_phase=SignalPhase.NORTH_SOUTH_GREEN,
                phase_duration=30,
                active_disruption=DisruptionType.NONE,
                disruption_severity=0.0
            )
            self.intersections_state.append(intersection)
        
        return self._get_observation()
    
    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict[str, Any]]:
        """Execute one environment step"""
        self.current_step += 1
        
        # Validate action
        if action.intersection_id >= self.num_intersections:
            return self._get_observation(), -10.0, False, {"error": "Invalid intersection ID"}
        
        # Apply action
        intersection = self.intersections_state[action.intersection_id]
        old_phase = intersection.current_phase
        intersection.current_phase = action.new_phase
        intersection.phase_duration = action.duration
        
        # Simulate traffic flow
        self._simulate_traffic_flow()
        
        # Calculate reward
        reward = self._calculate_reward(old_phase, action.new_phase)
        self.episode_reward += reward
        
        # Check termination
        done = self.current_step >= self.max_steps
        
        # Gather info
        info = {
            "total_throughput": self.total_throughput,
            "episode_reward": self.episode_reward,
            "active_disruptions": len(self.active_disruptions)
        }
        
        observation = self._get_observation()
        return observation, reward, done, info

    def state(self) -> TrafficState:
        """Return current state"""
        obs = self._get_observation()
        return TrafficState(
            observation=obs,
            reward=self.episode_reward,
            done=self.current_step >= self.max_steps,
            info={"step": self.current_step}
        )
    
    def _get_observation(self) -> Observation:
        """Construct observation from current state"""
        total_vehicles = sum(
            sum(inter.queue_lengths.values())
            for inter in self.intersections_state
        )
        
        total_waiting = sum(
            sum(inter.waiting_times.values())
            for inter in self.intersections_state
        )
        
        disruptions_count = sum(
            1 for inter in self.intersections_state
            if inter.active_disruption != DisruptionType.NONE
        )
        
        return Observation(
            intersections=self.intersections_state,
            total_vehicles=total_vehicles,
            total_waiting_time=total_waiting,
            throughput=self.total_throughput,
            timestep=self.current_step,
            disruptions_active=disruptions_count
        )
    
    def _simulate_traffic_flow(self):
        """Simulate one step of traffic dynamics"""
        step_throughput = 0
        
        for intersection in self.intersections_state:
            # Get disruption multiplier
            disruption_factor = 1.0 - (intersection.disruption_severity * 0.7)
            
            # Process each direction
            for direction in ["north", "south", "east", "west"]:
                # Add arriving vehicles
                arrival_rate = self.arrival_rate * disruption_factor
                if intersection.active_disruption == DisruptionType.DEMAND_SPIKE:
                    arrival_rate *= 2.0
                
                arrivals = np.random.poisson(arrival_rate)
                intersection.queue_lengths[direction] += arrivals
                
                # Process departures (if green light)
                can_depart = False
                if intersection.current_phase == SignalPhase.NORTH_SOUTH_GREEN:
                    can_depart = direction in ["north", "south"]
                elif intersection.current_phase == SignalPhase.EAST_WEST_GREEN:
                    can_depart = direction in ["east", "west"]
                
                if can_depart and intersection.queue_lengths[direction] > 0:
                    service_rate = self.service_rate * disruption_factor
                    departures = min(
                        intersection.queue_lengths[direction],
                        int(service_rate * intersection.phase_duration)
                    )
                    intersection.queue_lengths[direction] -= departures
                    step_throughput += departures
                
                # Update waiting times
                if intersection.queue_lengths[direction] > 0:
                    intersection.waiting_times[direction] += 1.0
                else:
                    intersection.waiting_times[direction] = max(0, intersection.waiting_times[direction] - 0.5)
            
            # Decay phase duration
            intersection.phase_duration = max(0, intersection.phase_duration - 1)
        
        self.total_throughput += step_throughput
    
    def _calculate_reward(self, old_phase: SignalPhase, new_phase: SignalPhase) -> float:
        """Calculate reward based on traffic metrics"""
        # Penalize total waiting time
        total_waiting = sum(
            sum(inter.waiting_times.values())
            for inter in self.intersections_state
        )
        waiting_penalty = -0.01 * total_waiting
        
        # Reward throughput
        throughput_reward = 0.1 * self.total_throughput
        
        # Penalize unnecessary phase changes
        phase_change_penalty = -2.0 if old_phase != new_phase else 0.0
        
        # Penalize long queues
        total_queue = sum(
            sum(inter.queue_lengths.values())
            for inter in self.intersections_state
        )
        queue_penalty = -0.05 * total_queue
        
        # Bonus for handling disruptions well
        disruption_bonus = 0.0
        for inter in self.intersections_state:
            if inter.active_disruption != DisruptionType.NONE:
                # Reward if queues are kept under control during disruption
                avg_queue = sum(inter.queue_lengths.values()) / 4
                if avg_queue < 15:
                    disruption_bonus += 5.0
        
        total_reward = (
            waiting_penalty +
            throughput_reward +
            phase_change_penalty +
            queue_penalty +
            disruption_bonus
        )
        
        return total_reward
    
    def inject_disruption(self, intersection_id: int, disruption_type: DisruptionType, severity: float = 0.5):
        """Inject a disruption into the environment"""
        if intersection_id < self.num_intersections:
            self.intersections_state[intersection_id].active_disruption = disruption_type
            self.intersections_state[intersection_id].disruption_severity = severity
            self.active_disruptions[intersection_id] = {
                "type": disruption_type,
                "severity": severity,
                "start_step": self.current_step
            }
    
    def clear_disruption(self, intersection_id: int):
        """Clear disruption from an intersection"""
        if intersection_id < self.num_intersections:
            self.intersections_state[intersection_id].active_disruption = DisruptionType.NONE
            self.intersections_state[intersection_id].disruption_severity = 0.0
            if intersection_id in self.active_disruptions:
                del self.active_disruptions[intersection_id]
