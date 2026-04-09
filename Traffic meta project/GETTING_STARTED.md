# Getting Started with Traffic Signal Control Environment

Welcome! This guide will help you get up and running with the traffic signal control environment in just a few minutes.

## 🎯 What You'll Learn

By the end of this guide, you'll be able to:
1. Install and validate the environment
2. Run your first traffic control episode
3. Understand the observation and action spaces
4. Test with different policies
5. Deploy to Hugging Face Spaces

## ⚡ Quick Start (5 minutes)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `openenv`: OpenEnv framework
- `pydantic`: Data validation
- `numpy`: Numerical operations
- `openai`: LLM client
- `gymnasium`: RL utilities

### Step 2: Validate Installation

```bash
python validate_env.py
```

You should see:
```
✓ PASS: OpenEnv Interface
✓ PASS: Pydantic Models
✓ PASS: DisruptionWrapper
✓ PASS: Tasks
🎉 All validation checks passed!
```

### Step 3: Run Your First Episode

```bash
python quick_test.py
```

This runs a simple heuristic policy on all three tasks. You'll see:
- Real-time progress updates
- Performance metrics
- Final scores

Expected output:
```
✓ easy_single_intersection: 1.000
✓ medium_multi_intersection: 0.995
✓ hard_network_resilience: 0.973
```

## 📖 Understanding the Basics

### What is Traffic Signal Control?

You control traffic lights at intersections to:
- **Minimize waiting time**: Keep vehicles moving
- **Maximize throughput**: Process as many vehicles as possible
- **Handle disruptions**: Adapt to lane closures, traffic spikes, sensor failures

### The Environment

```python
from env import TrafficSignalEnv

# Create environment with 1 intersection, 300 max steps
env = TrafficSignalEnv(num_intersections=1, max_steps=300)

# Reset to start
obs = env.reset()

# Take actions
action = Action(
    intersection_id=0,
    new_phase=SignalPhase.NORTH_SOUTH_GREEN,
    duration=30
)

obs, reward, done, info = env.step(action)
```

### Observations

Each observation tells you:
- **Queue lengths**: How many vehicles waiting in each direction
- **Waiting times**: How long vehicles have been waiting
- **Current phase**: Which lights are green
- **Disruptions**: Any active incidents

Example:
```python
obs.total_vehicles  # Total vehicles in system
obs.total_waiting_time  # Cumulative waiting time
obs.disruptions_active  # Number of active disruptions

# Per intersection
inter = obs.intersections[0]
inter.queue_lengths  # {"north": 5, "south": 3, "east": 7, "west": 2}
inter.current_phase  # "ns_green" or "ew_green"
inter.active_disruption  # "lane_closure", "demand_spike", etc.
```

### Actions

You control the traffic lights:
```python
action = Action(
    intersection_id=0,  # Which intersection (0 to N-1)
    new_phase=SignalPhase.NORTH_SOUTH_GREEN,  # Which lights to turn green
    duration=30  # How long (5-60 seconds)
)
```

Three phase options:
- `NORTH_SOUTH_GREEN`: North and south get green light
- `EAST_WEST_GREEN`: East and west get green light
- `ALL_RED`: All lights red (use sparingly!)

### Rewards

You get rewards based on:
- ✅ **Throughput**: +0.1 per vehicle processed
- ❌ **Waiting time**: -0.01 per second of waiting
- ❌ **Queue length**: -0.05 per vehicle waiting
- ❌ **Phase changes**: -2.0 for unnecessary switching
- ✅ **Disruption handling**: +5.0 bonus for good performance during incidents

## 🎮 Interactive Tutorial

### Tutorial 1: Basic Control

```python
from env import TrafficSignalEnv, Action, SignalPhase

# Create environment
env = TrafficSignalEnv(num_intersections=1, max_steps=100)
obs = env.reset()

print(f"Starting vehicles: {obs.total_vehicles}")

# Run for 10 steps
for i in range(10):
    # Simple alternating strategy
    phase = SignalPhase.NORTH_SOUTH_GREEN if i % 2 == 0 else SignalPhase.EAST_WEST_GREEN
    
    action = Action(
        intersection_id=0,
        new_phase=phase,
        duration=30
    )
    
    obs, reward, done, info = env.step(action)
    
    print(f"Step {i+1}: Reward={reward:.2f}, Vehicles={obs.total_vehicles}")
```

### Tutorial 2: Handling Disruptions

```python
from env import TrafficSignalEnv, DisruptionWrapper, Action, SignalPhase

# Create environment with automatic disruptions
base_env = TrafficSignalEnv(num_intersections=2, max_steps=100)
env = DisruptionWrapper(
    base_env,
    disruption_probability=0.2  # 20% chance per step
)

obs = env.reset()

for i in range(50):
    # Check for disruptions
    if obs.disruptions_active > 0:
        print(f"⚠️  Step {i}: {obs.disruptions_active} disruptions active!")
        # Use longer duration during disruptions
        duration = 40
    else:
        duration = 30
    
    action = Action(
        intersection_id=0,
        new_phase=SignalPhase.NORTH_SOUTH_GREEN,
        duration=duration
    )
    
    obs, reward, done, info = env.step(action)
```

### Tutorial 3: Smart Policy

```python
from env import TrafficSignalEnv, Action, SignalPhase

def smart_policy(obs):
    """Choose phase based on queue lengths"""
    inter = obs.intersections[0]
    
    # Calculate total queue in each direction
    ns_queue = inter.queue_lengths["north"] + inter.queue_lengths["south"]
    ew_queue = inter.queue_lengths["east"] + inter.queue_lengths["west"]
    
    # Switch to direction with more vehicles
    if ns_queue > ew_queue:
        phase = SignalPhase.NORTH_SOUTH_GREEN
    else:
        phase = SignalPhase.EAST_WEST_GREEN
    
    return Action(intersection_id=0, new_phase=phase, duration=30)

# Test the policy
env = TrafficSignalEnv(num_intersections=1, max_steps=100)
obs = env.reset()

total_reward = 0
for _ in range(100):
    action = smart_policy(obs)
    obs, reward, done, info = env.step(action)
    total_reward += reward
    if done:
        break

print(f"Total reward: {total_reward:.2f}")
```

## 🎯 Working with Tasks

### Load a Task

```python
from tasks import get_task

# Get task configuration and grader
config, grader = get_task("easy_single_intersection")

print(f"Task: {config.name}")
print(f"Difficulty: {config.difficulty}")
print(f"Intersections: {config.num_intersections}")
print(f"Max steps: {config.max_steps}")
```

### Run and Grade

```python
from env import TrafficSignalEnv, DisruptionWrapper
from tasks import get_task

# Load task
config, grader = get_task("easy_single_intersection")

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

while not done:
    # Your policy here
    action = your_policy(obs)
    obs, reward, done, info = env.step(action)

# Calculate score
score = grader(base_env, info)
print(f"Score: {score:.3f}")
print(f"Pass: {score > 0.5}")
```

## 🤖 Using LLMs

### Basic LLM Integration

```python
import os
from openai import OpenAI

# Set up client
client = OpenAI(
    base_url=os.getenv("API_BASE_URL", "https://api.openai.com/v1"),
    api_key=os.getenv("HF_TOKEN")
)

def llm_policy(obs):
    """Use LLM to decide action"""
    prompt = f"""
    Traffic state:
    - Total vehicles: {obs.total_vehicles}
    - Waiting time: {obs.total_waiting_time:.1f}
    
    Intersection 0:
    - Queues: {obs.intersections[0].queue_lengths}
    - Current phase: {obs.intersections[0].current_phase}
    
    Choose: "ns_green" or "ew_green"
    Respond with JSON: {{"new_phase": "...", "duration": 30}}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Parse response and create action
    # (see inference.py for full implementation)
    return action
```

### Run Full Inference

```bash
# Set your token
export HF_TOKEN=your_huggingface_token

# Run on all tasks
python inference.py
```

## 🐳 Docker Deployment

### Build Container

```bash
docker build -t traffic-signal-env .
```

### Run Container

```bash
docker run -e HF_TOKEN=your_token traffic-signal-env
```

### Test Locally

```bash
# Run with custom model
docker run \
  -e HF_TOKEN=your_token \
  -e MODEL_NAME=gpt-3.5-turbo \
  traffic-signal-env
```

## ☁️ Hugging Face Spaces

### Create Space

1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Name: `traffic-signal-control`
4. SDK: Docker
5. Visibility: Public

### Upload Files

```bash
# Clone your space
git clone https://huggingface.co/spaces/YOUR_USERNAME/traffic-signal-control
cd traffic-signal-control

# Copy all files
cp -r /path/to/traffic-signal-env/* .

# Push to space
git add .
git commit -m "Initial commit"
git push
```

### Configure Secrets

In Space settings, add:
- `HF_TOKEN`: Your Hugging Face token

### Verify Deployment

1. Wait for build to complete (5-10 minutes)
2. Check logs for successful execution
3. Verify output format is correct

## 🔧 Troubleshooting

### "Cannot import name 'SignalPhase'"

**Fix**: Update imports in your script:
```python
from env import TrafficSignalEnv, Action, SignalPhase, DisruptionType
```

### "HF_TOKEN environment variable is required"

**Fix**: Set the environment variable:
```bash
export HF_TOKEN=your_token
```

### Docker build fails

**Fix**: Clean up Docker:
```bash
docker system prune -a
docker build -t traffic-signal-env .
```

### Low scores

**Tips**:
- Switch phases based on queue lengths
- Use longer durations during disruptions
- Avoid frequent phase changes
- Monitor waiting times

## 📚 Next Steps

Now that you're set up:

1. **Experiment**: Try different policies in `quick_test.py`
2. **Customize**: Modify tasks in `tasks/task_configs.py`
3. **Visualize**: Add plotting to see traffic flow
4. **Optimize**: Improve prompting in `inference.py`
5. **Deploy**: Push to Hugging Face Spaces
6. **Share**: Submit to the hackathon!

## 🎓 Learning Resources

- **Example Usage**: Run `python example_usage.py` for 6 detailed examples
- **Validation**: Run `python validate_env.py` to check setup
- **Quick Test**: Run `python quick_test.py` for heuristic baseline
- **Full Inference**: Run `python inference.py` for LLM baseline

## 💡 Tips for Success

1. **Start Simple**: Test with heuristic policy first
2. **Understand Rewards**: Read the reward function carefully
3. **Handle Disruptions**: Adapt your strategy when disruptions occur
4. **Monitor Metrics**: Track throughput, waiting time, and queue length
5. **Iterate**: Test, measure, improve, repeat

## 🎉 You're Ready!

You now have everything you need to:
- ✅ Run the environment locally
- ✅ Understand observations and actions
- ✅ Implement custom policies
- ✅ Test with LLMs
- ✅ Deploy to Hugging Face Spaces

**Good luck with your traffic signal control system!** 🚦

---

**Questions?** Check the other documentation files:
- `README.md`: Full documentation
- `SETUP.md`: Detailed setup guide
- `SUBMISSION_CHECKLIST.md`: Pre-submission checklist
- `PROJECT_SUMMARY.md`: Project overview
