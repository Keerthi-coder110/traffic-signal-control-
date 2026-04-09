#!/usr/bin/env python3
"""
Validation script to ensure OpenEnv compliance.
Run this before submission to catch issues early.
"""

import sys
from env import TrafficSignalEnv, DisruptionWrapper, Action, SignalPhase
from tasks import get_task, TASKS


def validate_openenv_interface():
    """Validate that environment implements OpenEnv interface correctly"""
    print("Validating OpenEnv interface...")
    
    env = TrafficSignalEnv(num_intersections=1, max_steps=100)
    
    # Check reset() returns Observation
    try:
        obs = env.reset()
        assert hasattr(obs, 'model_dump'), "Observation must be Pydantic model"
        print("✓ reset() returns valid Observation")
    except Exception as e:
        print(f"✗ reset() failed: {e}")
        return False
    
    # Check step() returns correct tuple
    try:
        action = Action(
            intersection_id=0,
            new_phase=SignalPhase.NORTH_SOUTH_GREEN,
            duration=30
        )
        obs, reward, done, info = env.step(action)
        
        assert hasattr(obs, 'model_dump'), "Observation must be Pydantic model"
        assert isinstance(reward, (int, float)), "Reward must be numeric"
        assert isinstance(done, bool), "Done must be boolean"
        assert isinstance(info, dict), "Info must be dict"
        
        print("✓ step() returns (observation, reward, done, info)")
    except Exception as e:
        print(f"✗ step() failed: {e}")
        return False
    
    # Check state() returns TrafficState
    try:
        state = env.state()
        assert hasattr(state, 'observation'), "State must have observation"
        assert hasattr(state, 'reward'), "State must have reward"
        assert hasattr(state, 'done'), "State must have done"
        print("✓ state() returns valid TrafficState")
    except Exception as e:
        print(f"✗ state() failed: {e}")
        return False
    
    return True


def validate_disruption_wrapper():
    """Validate DisruptionWrapper functionality"""
    print("\nValidating DisruptionWrapper...")
    
    try:
        base_env = TrafficSignalEnv(num_intersections=2, max_steps=100)
        env = DisruptionWrapper(base_env, disruption_probability=0.5)
        
        obs = env.reset()
        print("✓ DisruptionWrapper reset() works")
        
        action = Action(
            intersection_id=0,
            new_phase=SignalPhase.EAST_WEST_GREEN,
            duration=20
        )
        
        disruption_found = False
        for _ in range(50):
            obs, reward, done, info = env.step(action)
            if 'disruptions' in info and len(info['disruptions']) > 0:
                disruption_found = True
                break
        
        if disruption_found:
            print("✓ DisruptionWrapper injects disruptions")
        else:
            print("⚠ No disruptions found in 50 steps (may be random)")
        
        return True
    except Exception as e:
        print(f"✗ DisruptionWrapper failed: {e}")
        return False


def validate_tasks():
    """Validate all task configurations"""
    print("\nValidating tasks...")
    
    for task_name in TASKS.keys():
        try:
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
            
            # Run short episode
            obs = env.reset()
            for _ in range(10):
                action = Action(
                    intersection_id=0,
                    new_phase=SignalPhase.NORTH_SOUTH_GREEN,
                    duration=30
                )
                obs, reward, done, info = env.step(action)
                if done:
                    break
            
            # Test grader
            score = grader(base_env, info)
            assert 0.0 <= score <= 1.0, f"Score {score} out of range [0, 1]"
            
            print(f"✓ Task '{task_name}' validated (score: {score:.3f})")
            
        except Exception as e:
            print(f"✗ Task '{task_name}' failed: {e}")
            return False
    
    return True


def validate_pydantic_models():
    """Validate Pydantic model serialization"""
    print("\nValidating Pydantic models...")
    
    try:
        from env.models import Observation, Action, TrafficState, IntersectionState, SignalPhase
        
        # Test Action
        action = Action(
            intersection_id=0,
            new_phase=SignalPhase.NORTH_SOUTH_GREEN,
            duration=30
        )
        action_dict = action.model_dump()
        action_json = action.model_dump_json()
        print("✓ Action model serializes correctly")
        
        # Test IntersectionState
        inter = IntersectionState(
            intersection_id=0,
            queue_lengths={"north": 5, "south": 5, "east": 5, "west": 5},
            waiting_times={"north": 10.0, "south": 10.0, "east": 10.0, "west": 10.0},
            current_phase=SignalPhase.NORTH_SOUTH_GREEN,
            phase_duration=30
        )
        inter_dict = inter.model_dump()
        print("✓ IntersectionState model serializes correctly")
        
        # Test Observation
        obs = Observation(
            intersections=[inter],
            total_vehicles=20,
            total_waiting_time=40.0,
            throughput=0,
            timestep=0,
            disruptions_active=0
        )
        obs_dict = obs.model_dump()
        print("✓ Observation model serializes correctly")
        
        return True
    except Exception as e:
        print(f"✗ Pydantic model validation failed: {e}")
        return False


def main():
    """Run all validation checks"""
    print("="*60)
    print("OpenEnv Environment Validation")
    print("="*60)
    
    checks = [
        ("OpenEnv Interface", validate_openenv_interface),
        ("Pydantic Models", validate_pydantic_models),
        ("DisruptionWrapper", validate_disruption_wrapper),
        ("Tasks", validate_tasks),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} validation crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 All validation checks passed!")
        print("Environment is ready for submission.")
        return 0
    else:
        print("\n❌ Some validation checks failed.")
        print("Please fix the issues before submission.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
