# Quick Reference Card

## 🚀 Essential Commands

```bash
# Setup
pip install -r requirements.txt

# Validate
python validate_env.py

# Test (no LLM)
python quick_test.py

# Run inference
export HF_TOKEN=your_token
python inference.py

# Docker
docker build -t traffic-signal-env .
docker run -e HF_TOKEN=token traffic-signal-env
```

## 📦 Core Imports

```python
from env import (
    TrafficSignalEnv,
    DisruptionWrapper,
    Action,
    SignalPhase,
    DisruptionType
)
from tasks import get_task, TASKS
```

## 🎮 Basic Usage

```python
# Create environment
env = TrafficSignalEnv(num_intersections=1, max_steps=300)

# Reset
obs = env.reset()

# Take action
action = Action(
    intersection_id=0,
    new_phase=SignalPhase.NORTH_SOUTH_GREEN,
    duration=30
)

# Step
obs, reward, done, info = env.step(action)
```

## 📊 Observation Structure

```python
obs.total_vehicles          # Total vehicles in system
obs.total_waiting_time      # Cumulative waiting time
obs.throughput              # Vehicles processed
obs.timestep                # Current step
obs.disruptions_active      # Number of disruptions

# Per intersection
inter = obs.intersections[0]
inter.queue_lengths         # {"north": 5, "south": 3, ...}
inter.waiting_times         # {"north": 10.0, "south": 8.0, ...}
inter.current_phase         # SignalPhase enum
inter.active_disruption     # DisruptionType enum
inter.disruption_severity   # 0.0 to 1.0
```

## 🎯 Action Structure

```python
Action(
    intersection_id=0,      # 0 to N-1
    new_phase=SignalPhase.NORTH_SOUTH_GREEN,  # or EAST_WEST_GREEN or ALL_RED
    duration=30             # 5 to 60 seconds
)
```

## 🏆 Tasks

| Task | Intersections | Steps | Disruption % | Target Throughput |
|------|---------------|-------|--------------|-------------------|
| easy_single_intersection | 1 | 300 | 5% | 150 |
| medium_multi_intersection | 3 | 500 | 15% | 400 |
| hard_network_resilience | 5 | 600 | 25% | 600 |

## 💰 Reward Components

```python
reward = (
    -0.01 * total_waiting_time    # Minimize waiting
    + 0.1 * throughput            # Maximize flow
    - 2.0 * phase_changes         # Reduce switching
    - 0.05 * total_queue_length   # Prevent congestion
    + 5.0 * disruption_bonus      # Reward resilience
)
```

## 🎲 Disruption Types

- `LANE_CLOSURE`: Reduced capacity
- `DEMAND_SPIKE`: 2x arrival rate
- `SENSOR_FAILURE`: Degraded observations
- `NONE`: No disruption

## 📈 Grading

```python
config, grader = get_task("easy_single_intersection")
score = grader(env, info)  # Returns 0.0 to 1.0
pass_threshold = 0.5
```

## 🔧 Environment Variables

```bash
HF_TOKEN=your_token              # Required
API_BASE_URL=https://...         # Optional (default: OpenAI)
MODEL_NAME=gpt-4o-mini           # Optional (default: gpt-4o-mini)
```

## 📝 Output Format

```
[START] task=<name> env=<env> model=<model>
[STEP] step=<n> action=<json> reward=<r> done=<bool> error=<msg|null>
[END] success=<bool> steps=<n> rewards=<r1,r2,...>
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Import error | `pip install -r requirements.txt` |
| HF_TOKEN error | `export HF_TOKEN=your_token` |
| Validation fails | Check Python version (3.10+) |
| Docker fails | `docker system prune -a` |
| Low scores | Improve policy/prompting |

## 📚 Documentation

- **Getting Started**: GETTING_STARTED.md
- **Full Docs**: README.md
- **Setup Guide**: SETUP.md
- **Architecture**: ARCHITECTURE.md
- **Submission**: SUBMISSION_CHECKLIST.md
- **Index**: INDEX.md

## 🎯 Simple Policy Example

```python
def simple_policy(obs):
    inter = obs.intersections[0]
    
    # Calculate queue totals
    ns = inter.queue_lengths["north"] + inter.queue_lengths["south"]
    ew = inter.queue_lengths["east"] + inter.queue_lengths["west"]
    
    # Choose phase with longer queue
    phase = SignalPhase.NORTH_SOUTH_GREEN if ns > ew else SignalPhase.EAST_WEST_GREEN
    
    # Longer duration during disruptions
    duration = 40 if inter.active_disruption != DisruptionType.NONE else 30
    
    return Action(intersection_id=0, new_phase=phase, duration=duration)
```

## 🔗 Key Files

| File | Purpose |
|------|---------|
| `inference.py` | Main submission script |
| `validate_env.py` | Validation script |
| `quick_test.py` | Heuristic testing |
| `example_usage.py` | Code examples |
| `env/traffic_env.py` | Core environment |
| `tasks/task_configs.py` | Task definitions |

## ✅ Pre-Submission Checklist

- [ ] `python validate_env.py` passes
- [ ] `python quick_test.py` runs
- [ ] Docker builds successfully
- [ ] HF Space is running
- [ ] Output format is correct
- [ ] All docs are complete

## 🎓 Learning Resources

1. Start: GETTING_STARTED.md
2. Examples: `python example_usage.py`
3. Test: `python quick_test.py`
4. Deploy: SETUP.md
5. Submit: SUBMISSION_CHECKLIST.md

## 💡 Tips

- Start with heuristic policy
- Test without LLM first
- Monitor queue lengths
- Adapt to disruptions
- Avoid frequent phase changes
- Use longer durations during disruptions

## 🏅 Baseline Scores

| Policy | Easy | Medium | Hard | Average |
|--------|------|--------|------|---------|
| Heuristic | 1.000 | 0.995 | 0.973 | 0.989 |
| LLM (GPT-4o-mini) | ~0.45 | ~0.38 | ~0.32 | ~0.38 |

## 🚀 Deployment

### Local
```bash
python inference.py
```

### Docker
```bash
docker build -t traffic-signal-env .
docker run -e HF_TOKEN=token traffic-signal-env
```

### HF Spaces
1. Create Space (Docker SDK)
2. Upload files
3. Set HF_TOKEN secret
4. Wait for build

---

**Keep this card handy for quick reference!** 📌
