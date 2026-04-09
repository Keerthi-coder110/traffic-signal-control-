# Incident-Resilient Traffic Signal Control using Reinforcement Learning

[![OpenEnv](https://img.shields.io/badge/OpenEnv-Compatible-blue)](https://github.com/meta-pytorch/OpenEnv)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Overview

Traditional reinforcement learning approaches for traffic signal control optimize for normal conditions but fail when faced with real-world disruptions like lane closures, traffic surges, or sensor failures. This project introduces an **incident-resilient traffic signal control system** that trains agents to maintain performance under adverse conditions.

### Key Innovation: DisruptionWrapper

Our core contribution is the `DisruptionWrapper`, a custom module that injects realistic disruptions during training:

- **Lane Closures**: Reduced capacity on specific lanes
- **Demand Spikes**: Sudden increases in vehicle arrival rates  
- **Sensor Failures**: Degraded observation quality

By training in this dynamic environment, agents learn adaptive strategies that enable quick recovery from unexpected events.

## Motivation

Current traffic control systems are optimized for ideal conditions. When disruptions occur:
- Standard RL agents experience severe performance degradation
- Traffic congestion increases dramatically
- Recovery time is slow or non-existent

Our robust training approach addresses this critical gap, making the system suitable for real-world deployment in smart cities.

## Environment Specification

### Action Space

```python
class Action(BaseModel):
    intersection_id: int          # Which intersection to control
    new_phase: SignalPhase        # "ns_green", "ew_green", or "all_red"
    duration: int                 # Signal duration (5-60 seconds)
```

### Observation Space

```python
class Observation(BaseModel):
    intersections: List[IntersectionState]  # State of each intersection
    total_vehicles: int                     # Total vehicles in system
    total_waiting_time: float               # Cumulative waiting time
    throughput: int                         # Vehicles processed
    timestep: int                           # Current timestep
    disruptions_active: int                 # Number of active disruptions
```

Each `IntersectionState` includes:
- Queue lengths per direction (north, south, east, west)
- Average waiting times per direction
- Current signal phase and duration
- Active disruption type and severity

### Reward Function

The reward function balances multiple objectives:

```python
reward = (
    -0.01 * total_waiting_time      # Minimize waiting
    + 0.1 * throughput              # Maximize flow
    - 2.0 * phase_changes           # Discourage frequent switching
    - 0.05 * total_queue_length     # Penalize congestion
    + 5.0 * disruption_bonus        # Reward resilience
)
```

The reward provides continuous feedback throughout the episode, enabling the agent to learn incremental progress.

## Tasks

### 1. Easy: Single Intersection (easy_single_intersection)

**Difficulty**: Easy  
**Description**: Control one intersection with minimal disruptions (5% probability)

**Objectives**:
- Target throughput: 150 vehicles
- Max average waiting time: 50 seconds
- Handle occasional lane closures

**Grading**: 60% throughput + 40% waiting time

### 2. Medium: Multi-Intersection Network (medium_multi_intersection)

**Difficulty**: Medium  
**Description**: Control 3 intersections with moderate disruptions (15% probability)

**Objectives**:
- Target throughput: 400 vehicles
- Max average waiting time: 80 seconds
- Coordinate signals across intersections
- Handle demand spikes and sensor failures

**Grading**: 50% throughput + 30% waiting time + 20% disruption handling

### 3. Hard: Network Resilience (hard_network_resilience)

**Difficulty**: Hard  
**Description**: Manage 5 intersections under severe disruptions (25% probability)

**Objectives**:
- Target throughput: 600 vehicles
- Max average waiting time: 120 seconds
- Maintain stability during multiple simultaneous disruptions
- Demonstrate quick recovery

**Grading**: 40% throughput + 30% waiting time + 30% resilience

## Installation

### Local Setup

```bash
# Clone repository
git clone <repository-url>
cd traffic-signal-env

# Install dependencies
pip install -r requirements.txt

# Validate OpenEnv compliance
openenv validate
```

### Docker Setup

```bash
# Build container
docker build -t traffic-signal-env .

# Run inference
docker run -e HF_TOKEN=<your-token> traffic-signal-env
```

## Usage

### Running Baseline Inference

```bash
# Set required environment variables
export HF_TOKEN=<your-huggingface-token>
export API_BASE_URL=https://api.openai.com/v1  # Optional
export MODEL_NAME=gpt-4o-mini                   # Optional

# Run inference script
python inference.py
```

### Using the Environment

```python
from env import TrafficSignalEnv, DisruptionWrapper, Action, SignalPhase
from tasks import get_task

# Load task configuration
config, grader = get_task("easy_single_intersection")

# Create environment
base_env = TrafficSignalEnv(
    num_intersections=config.num_intersections,
    max_steps=config.max_steps
)

# Wrap with disruptions for robust training
env = DisruptionWrapper(
    base_env,
    disruption_probability=config.disruption_probability
)

# Reset and run episode
obs = env.reset()
done = False

while not done:
    # Your agent logic here
    action = Action(
        intersection_id=0,
        new_phase=SignalPhase.NORTH_SOUTH_GREEN,
        duration=30
    )
    
    obs, reward, done, info = env.step(action)
    print(f"Reward: {reward:.2f}, Disruptions: {info.get('disruptions', {})}")

# Calculate final score
score = grader(base_env, info)
print(f"Final Score: {score:.3f}")
```

## Baseline Performance

Performance of GPT-4o-mini with simple prompting strategy:

| Task | Score | Success | Notes |
|------|-------|---------|-------|
| Easy Single Intersection | 0.45 | ❌ | Struggles with timing optimization |
| Medium Multi-Intersection | 0.38 | ❌ | Poor coordination between signals |
| Hard Network Resilience | 0.32 | ❌ | Cannot adapt to severe disruptions |

**Average Score**: 0.38 / 1.00

These baseline results demonstrate significant room for improvement through:
- Better prompting strategies
- Fine-tuned models
- Hybrid RL + LLM approaches
- Multi-agent coordination

## Evaluation Metrics

Each task is graded on a 0.0 to 1.0 scale based on:

1. **Throughput**: Number of vehicles successfully processed
2. **Waiting Time**: Average time vehicles spend waiting
3. **Queue Management**: Ability to prevent excessive congestion
4. **Disruption Resilience**: Performance maintenance during incidents
5. **Recovery Speed**: Time to restore normal operation after disruptions

A score above 0.5 is considered passing.

## Architecture

```
traffic-signal-env/
├── env/
│   ├── traffic_env.py         # Core OpenEnv implementation
│   ├── models.py               # Pydantic data models
│   └── disruption_wrapper.py  # Disruption injection logic
├── tasks/
│   └── task_configs.py         # Task definitions and graders
├── inference.py                # Baseline LLM inference
├── Dockerfile                  # Container configuration
├── requirements.txt            # Python dependencies
├── openenv.yaml                # OpenEnv metadata
└── README.md                   # This file
```

## Key Features

✅ **OpenEnv Compliant**: Fully implements the OpenEnv interface  
✅ **Real-World Relevance**: Models actual traffic control challenges  
✅ **Disruption Injection**: Trains for robustness, not just optimization  
✅ **Progressive Difficulty**: Three tasks from easy to hard  
✅ **Programmatic Grading**: Deterministic, reproducible scoring  
✅ **Continuous Rewards**: Feedback throughout episode trajectory  
✅ **Docker Ready**: Containerized for easy deployment  
✅ **HF Spaces Compatible**: Ready for Hugging Face deployment

## Deployment on Hugging Face Spaces

1. Create a new Space on Hugging Face
2. Select "Docker" as the SDK
3. Upload all project files
4. Set environment variables in Space settings:
   - `HF_TOKEN` (required)
   - `API_BASE_URL` (optional)
   - `MODEL_NAME` (optional)
5. Space will automatically build and run

## Future Enhancements

- Multi-agent coordination strategies
- Real traffic data integration
- Visualization dashboard
- Additional disruption types (accidents, weather, events)
- Transfer learning across different city layouts
- Integration with real traffic management systems

## Citation

If you use this environment in your research, please cite:

```bibtex
@software{traffic_signal_resilient_2026,
  title={Incident-Resilient Traffic Signal Control using Reinforcement Learning},
  author={Meta Hackathon Team},
  year={2026},
  url={https://github.com/yourusername/traffic-signal-env}
}
```

## License

MIT License - see LICENSE file for details

## Acknowledgments

Built for the Meta Hackathon OpenEnv RL Challenge. Inspired by real-world traffic management challenges and the need for robust AI systems in critical infrastructure.

---

**Contact**: For questions or collaboration opportunities, please open an issue on GitHub.
