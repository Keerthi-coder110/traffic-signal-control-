#!/usr/bin/env python3
"""
Quick test script to verify environment works without LLM calls.
Useful for rapid iteration and debugging.
"""

from env import TrafficSignalEnv, DisruptionWrapper, Action, SignalPhase, DisruptionType
from tasks import get_task
import random


def simple_heuristic_policy(obs):
    """
    Simple rule-based policy for testing.
    Switches to the direction with the longest queue.
    """
    # Find intersection with longest total queue
    max_queue = 0
    target_intersection = 0
    
    for inter in obs.intersections:
        total_queue = sum(inter.queue_lengths.values())
        if total_queue > max_queue:
            max_queue = total_queue
            target_intersection = inter.intersection_id
    
    # Get the intersection
    inter = obs.intersections[target_intersection]
    
    # Determine which direction has more vehicles
    ns_queue = inter.queue_lengths["north"] + inter.queue_lengths["south"]
    ew_queue = inter.queue_lengths["east"] + inter.queue_lengths["west"]
    
    # Choose phase based on queue lengths
    if ns_queue > ew_queue:
        new_phase = SignalPhase.NORTH_SOUTH_GREEN
    else:
        new_phase = SignalPhase.EAST_WEST_GREEN
    
    # Longer duration during disruptions
    duration = 40 if inter.active_disruption != DisruptionType.NONE else 30
    
    return Action(
        intersection_id=target_intersection,
        new_phase=new_phase,
        duration=duration
    )


def test_task(task_name: str):
    """Test a single task with heuristic policy"""
    print(f"\n{'='*60}")
    print(f"Testing: {task_name}")
    print(f"{'='*60}")
    
    # Get task configuration
    config, grader = get_task(task_name)
    
    # Create environment
    base_env = TrafficSignalEnv(
        num_intersections=config.num_intersections,
        max_steps=config.max_steps
    )
    
    env = DisruptionWrapper(
        base_env,
        disruption_probability=config.disruption_probability
    )
    
    # Run episode
    obs = env.reset()
    done = False
    step_count = 0
    total_reward = 0.0
    disruptions_seen = 0
    
    print(f"Starting episode with {config.num_intersections} intersections...")
    
    while not done:
        step_count += 1
        
        # Get action from heuristic
        action = simple_heuristic_policy(obs)
        
        # Execute step
        obs, reward, done, info = env.step(action)
        total_reward += reward
        
        # Track disruptions
        if 'disruptions' in info and len(info['disruptions']) > 0:
            disruptions_seen = max(disruptions_seen, len(info['disruptions']))
        
        # Print progress every 50 steps
        if step_count % 50 == 0:
            print(f"  Step {step_count}: "
                  f"Vehicles={obs.total_vehicles}, "
                  f"Waiting={obs.total_waiting_time:.1f}, "
                  f"Throughput={obs.throughput}, "
                  f"Disruptions={obs.disruptions_active}")
    
    # Calculate final score
    score = grader(base_env, info)
    
    # Print results
    print(f"\nResults:")
    print(f"  Steps: {step_count}")
    print(f"  Total Reward: {total_reward:.2f}")
    print(f"  Final Score: {score:.3f}")
    print(f"  Max Disruptions: {disruptions_seen}")
    print(f"  Success: {'✓' if score > 0.5 else '✗'}")
    
    return score


def main():
    """Test all tasks"""
    print("="*60)
    print("Quick Test - Heuristic Policy")
    print("="*60)
    
    from tasks import TASKS
    
    scores = []
    for task_name in TASKS.keys():
        score = test_task(task_name)
        scores.append((task_name, score))
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    for task_name, score in scores:
        status = "✓" if score > 0.5 else "✗"
        print(f"{status} {task_name}: {score:.3f}")
    
    avg_score = sum(s for _, s in scores) / len(scores)
    print(f"\nAverage Score: {avg_score:.3f}")
    print(f"Tasks Passed: {sum(1 for _, s in scores if s > 0.5)}/{len(scores)}")


if __name__ == "__main__":
    main()
