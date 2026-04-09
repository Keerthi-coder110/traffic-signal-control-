#!/usr/bin/env python3
"""
Example usage of the Traffic Signal Control environment.
This script demonstrates various features and use cases.
"""

from env import TrafficSignalEnv, DisruptionWrapper, Action, SignalPhase
from env.models import DisruptionType
from tasks import get_task, TASKS


def example_1_basic_usage():
    """Example 1: Basic environment usage"""
    print("\n" + "="*60)
    print("Example 1: Basic Environment Usage")
    print("="*60)
    
    # Create environment
    env = TrafficSignalEnv(num_intersections=1, max_steps=50)
    
    # Reset to get initial observation
    obs = env.reset()
    print(f"\nInitial state:")
    print(f"  Total vehicles: {obs.total_vehicles}")
    print(f"  Timestep: {obs.timestep}")
    
    # Take a few actions
    for i in range(5):
        action = Action(
            intersection_id=0,
            new_phase=SignalPhase.NORTH_SOUTH_GREEN if i % 2 == 0 else SignalPhase.EAST_WEST_GREEN,
            duration=30
        )
        
        obs, reward, done, info = env.step(action)
        
        print(f"\nStep {i+1}:")
        print(f"  Action: {action.new_phase.value}")
        print(f"  Reward: {reward:.2f}")
        print(f"  Total vehicles: {obs.total_vehicles}")
        print(f"  Throughput: {obs.throughput}")


def example_2_disruption_handling():
    """Example 2: Handling disruptions"""
    print("\n" + "="*60)
    print("Example 2: Disruption Handling")
    print("="*60)
    
    # Create environment
    env = TrafficSignalEnv(num_intersections=2, max_steps=100)
    obs = env.reset()
    
    print("\nRunning without disruptions for 10 steps...")
    for i in range(10):
        action = Action(
            intersection_id=0,
            new_phase=SignalPhase.NORTH_SOUTH_GREEN,
            duration=30
        )
        obs, reward, done, info = env.step(action)
    
    print(f"Vehicles before disruption: {obs.total_vehicles}")
    
    # Inject a disruption
    print("\n⚠️  Injecting LANE_CLOSURE disruption at intersection 0...")
    env.inject_disruption(0, DisruptionType.LANE_CLOSURE, severity=0.7)
    
    # Continue for 10 more steps
    print("Running with disruption for 10 steps...")
    for i in range(10):
        action = Action(
            intersection_id=0,
            new_phase=SignalPhase.NORTH_SOUTH_GREEN,
            duration=40  # Longer duration to compensate
        )
        obs, reward, done, info = env.step(action)
    
    print(f"Vehicles after disruption: {obs.total_vehicles}")
    print(f"Active disruption: {obs.intersections[0].active_disruption.value}")
    print(f"Disruption severity: {obs.intersections[0].disruption_severity:.2f}")
    
    # Clear disruption
    print("\n✓ Clearing disruption...")
    env.clear_disruption(0)
    obs = env._get_observation()
    print(f"Active disruption: {obs.intersections[0].active_disruption.value}")


def example_3_disruption_wrapper():
    """Example 3: Using DisruptionWrapper for automatic disruptions"""
    print("\n" + "="*60)
    print("Example 3: DisruptionWrapper (Automatic Disruptions)")
    print("="*60)
    
    # Create base environment
    base_env = TrafficSignalEnv(num_intersections=3, max_steps=100)
    
    # Wrap with disruption injection
    env = DisruptionWrapper(
        base_env,
        disruption_probability=0.3,  # 30% chance per step
        disruption_duration_range=(10, 30),
        severity_range=(0.4, 0.8)
    )
    
    obs = env.reset()
    
    print("\nRunning episode with automatic disruption injection...")
    disruption_events = []
    
    for i in range(50):
        action = Action(
            intersection_id=i % 3,  # Rotate between intersections
            new_phase=SignalPhase.NORTH_SOUTH_GREEN,
            duration=30
        )
        
        obs, reward, done, info = env.step(action)
        
        # Track disruptions
        if 'disruptions' in info and len(info['disruptions']) > 0:
            disruption_events.append((i, info['disruptions']))
            print(f"\nStep {i}: Disruption detected!")
            for inter_id, disruption in info['disruptions'].items():
                print(f"  Intersection {inter_id}: {disruption['type'].value} "
                      f"(remaining: {disruption['remaining']} steps)")
    
    print(f"\nTotal disruption events: {len(disruption_events)}")
    print(f"Final throughput: {obs.throughput}")


def example_4_task_evaluation():
    """Example 4: Running and evaluating a task"""
    print("\n" + "="*60)
    print("Example 4: Task Evaluation")
    print("="*60)
    
    # Load easy task
    task_name = "easy_single_intersection"
    config, grader = get_task(task_name)
    
    print(f"\nTask: {config.name}")
    print(f"Difficulty: {config.difficulty}")
    print(f"Description: {config.description}")
    print(f"Intersections: {config.num_intersections}")
    print(f"Max steps: {config.max_steps}")
    
    # Create environment
    base_env = TrafficSignalEnv(
        num_intersections=config.num_intersections,
        max_steps=config.max_steps
    )
    
    env = DisruptionWrapper(
        base_env,
        disruption_probability=config.disruption_probability
    )
    
    # Run episode with simple policy
    obs = env.reset()
    done = False
    step_count = 0
    
    print("\nRunning episode...")
    while not done and step_count < 50:  # Limit for demo
        step_count += 1
        
        # Simple alternating policy
        action = Action(
            intersection_id=0,
            new_phase=SignalPhase.NORTH_SOUTH_GREEN if step_count % 2 == 0 else SignalPhase.EAST_WEST_GREEN,
            duration=30
        )
        
        obs, reward, done, info = env.step(action)
        
        if step_count % 10 == 0:
            print(f"  Step {step_count}: Vehicles={obs.total_vehicles}, "
                  f"Waiting={obs.total_waiting_time:.1f}, Reward={reward:.2f}")
    
    # Evaluate performance
    score = grader(base_env, info)
    
    print(f"\nFinal Evaluation:")
    print(f"  Steps completed: {step_count}")
    print(f"  Total throughput: {info['total_throughput']}")
    print(f"  Final score: {score:.3f}")
    print(f"  Pass threshold: 0.5")
    print(f"  Result: {'✓ PASS' if score > 0.5 else '✗ FAIL'}")


def example_5_state_inspection():
    """Example 5: Inspecting detailed state"""
    print("\n" + "="*60)
    print("Example 5: State Inspection")
    print("="*60)
    
    env = TrafficSignalEnv(num_intersections=2, max_steps=100)
    obs = env.reset()
    
    # Take a few steps
    for _ in range(5):
        action = Action(
            intersection_id=0,
            new_phase=SignalPhase.NORTH_SOUTH_GREEN,
            duration=30
        )
        obs, reward, done, info = env.step(action)
    
    # Get full state
    state = env.state()
    
    print("\nFull Environment State:")
    print(f"  Current timestep: {state.observation.timestep}")
    print(f"  Episode reward: {state.reward:.2f}")
    print(f"  Done: {state.done}")
    
    print("\nIntersection Details:")
    for inter in state.observation.intersections:
        print(f"\n  Intersection {inter.intersection_id}:")
        print(f"    Current phase: {inter.current_phase.value}")
        print(f"    Phase duration: {inter.phase_duration}")
        print(f"    Queue lengths:")
        for direction, length in inter.queue_lengths.items():
            print(f"      {direction}: {length} vehicles")
        print(f"    Waiting times:")
        for direction, time in inter.waiting_times.items():
            print(f"      {direction}: {time:.1f} seconds")


def example_6_all_tasks_overview():
    """Example 6: Overview of all tasks"""
    print("\n" + "="*60)
    print("Example 6: All Tasks Overview")
    print("="*60)
    
    for task_name, config in TASKS.items():
        print(f"\n{config.name}:")
        print(f"  Difficulty: {config.difficulty}")
        print(f"  Intersections: {config.num_intersections}")
        print(f"  Max steps: {config.max_steps}")
        print(f"  Disruption probability: {config.disruption_probability*100:.0f}%")
        print(f"  Target throughput: {config.target_throughput}")
        print(f"  Max avg waiting time: {config.max_avg_waiting_time}")
        print(f"  Description: {config.description}")


def main():
    """Run all examples"""
    print("="*60)
    print("Traffic Signal Control - Example Usage")
    print("="*60)
    
    examples = [
        example_1_basic_usage,
        example_2_disruption_handling,
        example_3_disruption_wrapper,
        example_4_task_evaluation,
        example_5_state_inspection,
        example_6_all_tasks_overview,
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\n❌ Example failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60)


if __name__ == "__main__":
    main()
