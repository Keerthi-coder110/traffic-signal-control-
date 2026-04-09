#!/usr/bin/env python3
"""
Baseline inference script for traffic signal control environment.
Complies with Meta Hackathon OpenEnv RL Challenge requirements.
"""

import os
import sys
import json
from openai import OpenAI
from env import TrafficSignalEnv, DisruptionWrapper, Action, SignalPhase
from tasks import get_task, TASKS


# Read environment variables with defaults
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")

if HF_TOKEN is None:
    raise ValueError("HF_TOKEN environment variable is required")

# Initialize OpenAI client
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN
)


def get_llm_action(observation_dict: dict, task_name: str) -> Action:
    """
    Query LLM for action based on current observation.
    """
    prompt = f"""You are controlling traffic signals to minimize congestion and waiting time.

Task: {task_name}

Current State:
- Total vehicles waiting: {observation_dict['total_vehicles']}
- Total waiting time: {observation_dict['total_waiting_time']:.1f}
- Active disruptions: {observation_dict['disruptions_active']}
- Timestep: {observation_dict['timestep']}

Intersections:
"""
    
    for inter in observation_dict['intersections']:
        prompt += f"\nIntersection {inter['intersection_id']}:\n"
        prompt += f"  Current phase: {inter['current_phase']}\n"
        prompt += f"  Queue lengths: {inter['queue_lengths']}\n"
        prompt += f"  Waiting times: {inter['waiting_times']}\n"
        prompt += f"  Disruption: {inter['active_disruption']} (severity: {inter['disruption_severity']:.2f})\n"
    
    prompt += """
Choose an action to optimize traffic flow. Respond with JSON only:
{
  "intersection_id": <int>,
  "new_phase": "ns_green" or "ew_green" or "all_red",
  "duration": <int between 5 and 60>
}

Strategy tips:
- Switch phases when queues build up in the red direction
- Increase duration during disruptions
- Prioritize directions with longest waiting times
"""
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a traffic signal control expert. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        content = response.choices[0].message.content.strip()
        
        # Extract JSON from response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        action_dict = json.loads(content)
        
        # Validate and create action
        action = Action(
            intersection_id=action_dict.get("intersection_id", 0),
            new_phase=SignalPhase(action_dict.get("new_phase", "ns_green")),
            duration=max(5, min(60, action_dict.get("duration", 30)))
        )
        
        return action
        
    except Exception as e:
        # Fallback to simple heuristic
        print(f"LLM error: {e}, using fallback", file=sys.stderr)
        return Action(
            intersection_id=0,
            new_phase=SignalPhase.NORTH_SOUTH_GREEN,
            duration=30
        )


def run_episode(task_name: str, use_disruptions: bool = True) -> dict:
    """
    Run a single episode on the specified task.
    """
    # Get task configuration
    config, grader = get_task(task_name)
    
    # Create environment
    base_env = TrafficSignalEnv(
        num_intersections=config.num_intersections,
        max_steps=config.max_steps
    )
    
    if use_disruptions:
        env = DisruptionWrapper(
            base_env,
            disruption_probability=config.disruption_probability
        )
    else:
        env = base_env
    
    # Print start marker
    print(f"[START] task={task_name} env=traffic-signal-control model={MODEL_NAME}")
    
    # Reset environment
    obs = env.reset()
    done = False
    step_count = 0
    rewards = []
    last_error = None
    
    # Episode loop
    while not done:
        step_count += 1
        
        # Convert observation to dict
        obs_dict = obs.model_dump()
        
        # Get action from LLM
        try:
            action = get_llm_action(obs_dict, task_name)
            last_error = None
        except Exception as e:
            last_error = str(e)
            action = Action(intersection_id=0, new_phase=SignalPhase.NORTH_SOUTH_GREEN, duration=30)
        
        # Execute action
        obs, reward, done, info = env.step(action)
        rewards.append(reward)
        
        # Print step marker
        error_str = f"'{last_error}'" if last_error else "null"
        print(f"[STEP] step={step_count} action={action.model_dump_json()} reward={reward:.2f} done={str(done).lower()} error={error_str}")
        
        # Safety limit
        if step_count >= config.max_steps:
            done = True
    
    # Calculate final score using grader
    final_score = grader(base_env, info)
    
    # Print end marker
    rewards_str = ",".join([f"{r:.2f}" for r in rewards])
    success = final_score > 0.5
    print(f"[END] success={str(success).lower()} steps={step_count} rewards={rewards_str}")
    
    return {
        "task": task_name,
        "score": final_score,
        "steps": step_count,
        "total_reward": sum(rewards),
        "success": success
    }


def main():
    """Run inference on all tasks"""
    print("=" * 60)
    print("Traffic Signal Control - Baseline Inference")
    print(f"Model: {MODEL_NAME}")
    print("=" * 60)
    
    results = []
    
    for task_name in TASKS.keys():
        print(f"\n{'='*60}")
        print(f"Running task: {task_name}")
        print(f"{'='*60}\n")
        
        result = run_episode(task_name, use_disruptions=True)
        results.append(result)
        
        print(f"\nTask {task_name} completed:")
        print(f"  Score: {result['score']:.3f}")
        print(f"  Steps: {result['steps']}")
        print(f"  Total Reward: {result['total_reward']:.2f}")
        print(f"  Success: {result['success']}")
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    avg_score = sum(r['score'] for r in results) / len(results)
    print(f"Average Score: {avg_score:.3f}")
    print(f"Tasks Passed: {sum(r['success'] for r in results)}/{len(results)}")
    
    for result in results:
        print(f"  {result['task']}: {result['score']:.3f}")


if __name__ == "__main__":
    main()
