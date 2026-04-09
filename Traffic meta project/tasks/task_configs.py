from typing import Dict, Callable
from pydantic import BaseModel
from env.traffic_env import TrafficSignalEnv
from env.disruption_wrapper import DisruptionWrapper


class TaskConfig(BaseModel):
    """Configuration for a task"""
    name: str
    difficulty: str
    description: str
    num_intersections: int
    max_steps: int
    disruption_probability: float
    target_throughput: int
    max_avg_waiting_time: float
    
    class Config:
        arbitrary_types_allowed = True


def grade_easy_task(env: TrafficSignalEnv, info: Dict) -> float:
    """
    Grader for easy task: single intersection with minimal disruptions.
    Score based on throughput and waiting time.
    """
    target_throughput = 150
    max_waiting_time = 50.0
    
    # Get metrics
    throughput = info.get("total_throughput", 0)
    obs = env._get_observation()
    avg_waiting = obs.total_waiting_time / max(1, len(obs.intersections))
    
    # Throughput score (0-0.6)
    throughput_score = min(0.6, (throughput / target_throughput) * 0.6)
    
    # Waiting time score (0-0.4)
    waiting_score = max(0, 0.4 * (1 - avg_waiting / max_waiting_time))
    
    total_score = throughput_score + waiting_score
    return min(1.0, max(0.0, total_score))


def grade_medium_task(env: TrafficSignalEnv, info: Dict) -> float:
    """
    Grader for medium task: multiple intersections with moderate disruptions.
    Score based on throughput, waiting time, and disruption handling.
    """
    target_throughput = 400
    max_waiting_time = 80.0
    
    throughput = info.get("total_throughput", 0)
    obs = env._get_observation()
    avg_waiting = obs.total_waiting_time / max(1, len(obs.intersections))
    
    # Throughput score (0-0.5)
    throughput_score = min(0.5, (throughput / target_throughput) * 0.5)
    
    # Waiting time score (0-0.3)
    waiting_score = max(0, 0.3 * (1 - avg_waiting / max_waiting_time))
    
    # Disruption handling score (0-0.2)
    # Reward if average queue length stayed reasonable
    avg_queue = obs.total_vehicles / max(1, len(obs.intersections))
    disruption_score = max(0, 0.2 * (1 - avg_queue / 30))
    
    total_score = throughput_score + waiting_score + disruption_score
    return min(1.0, max(0.0, total_score))


def grade_hard_task(env: TrafficSignalEnv, info: Dict) -> float:
    """
    Grader for hard task: network under severe disruptions.
    Score based on resilience, recovery time, and overall performance.
    """
    target_throughput = 600
    max_waiting_time = 120.0
    
    throughput = info.get("total_throughput", 0)
    obs = env._get_observation()
    avg_waiting = obs.total_waiting_time / max(1, len(obs.intersections))
    
    # Throughput score (0-0.4)
    throughput_score = min(0.4, (throughput / target_throughput) * 0.4)
    
    # Waiting time score (0-0.3)
    waiting_score = max(0, 0.3 * (1 - avg_waiting / max_waiting_time))
    
    # Resilience score (0-0.3)
    # Check if system maintained stability despite disruptions
    avg_queue = obs.total_vehicles / max(1, len(obs.intersections))
    max_acceptable_queue = 40
    resilience_score = max(0, 0.3 * (1 - avg_queue / max_acceptable_queue))
    
    total_score = throughput_score + waiting_score + resilience_score
    return min(1.0, max(0.0, total_score))


# Task definitions
TASKS: Dict[str, TaskConfig] = {
    "easy_single_intersection": TaskConfig(
        name="easy_single_intersection",
        difficulty="easy",
        description="Control a single intersection with minimal disruptions",
        num_intersections=1,
        max_steps=300,
        disruption_probability=0.05,
        target_throughput=150,
        max_avg_waiting_time=50.0
    ),
    "medium_multi_intersection": TaskConfig(
        name="medium_multi_intersection",
        difficulty="medium",
        description="Control multiple intersections with moderate disruptions",
        num_intersections=3,
        max_steps=500,
        disruption_probability=0.15,
        target_throughput=400,
        max_avg_waiting_time=80.0
    ),
    "hard_network_resilience": TaskConfig(
        name="hard_network_resilience",
        difficulty="hard",
        description="Manage a network under severe disruptions",
        num_intersections=5,
        max_steps=600,
        disruption_probability=0.25,
        target_throughput=600,
        max_avg_waiting_time=120.0
    )
}


GRADERS: Dict[str, Callable] = {
    "easy_single_intersection": grade_easy_task,
    "medium_multi_intersection": grade_medium_task,
    "hard_network_resilience": grade_hard_task
}


def get_task(task_name: str) -> tuple:
    """Get task configuration and grader"""
    if task_name not in TASKS:
        raise ValueError(f"Unknown task: {task_name}. Available: {list(TASKS.keys())}")
    
    config = TASKS[task_name]
    grader = GRADERS[task_name]
    
    return config, grader
