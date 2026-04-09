# Architecture Documentation

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Traffic Signal Control                    │
│              Incident-Resilient RL Environment               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │         OpenEnv Interface Layer          │
        │  reset() / step() / state()              │
        └─────────────────────────────────────────┘
                              │
        ┌─────────────────────┴─────────────────────┐
        │                                            │
        ▼                                            ▼
┌──────────────────┐                    ┌──────────────────────┐
│  TrafficSignalEnv│                    │  DisruptionWrapper   │
│  (Base Env)      │◄───────────────────│  (Robustness Layer)  │
└──────────────────┘                    └──────────────────────┘
        │                                            │
        │                                            │
        ▼                                            ▼
┌──────────────────┐                    ┌──────────────────────┐
│  Pydantic Models │                    │  Disruption Injection│
│  - Observation   │                    │  - Lane Closure      │
│  - Action        │                    │  - Demand Spike      │
│  - State         │                    │  - Sensor Failure    │
└──────────────────┘                    └──────────────────────┘
```

## Component Architecture

### 1. Core Environment (`env/traffic_env.py`)

```
TrafficSignalEnv
├── __init__(num_intersections, max_steps)
├── reset() → Observation
├── step(action) → (Observation, reward, done, info)
├── state() → TrafficState
├── _simulate_traffic_flow()
├── _calculate_reward()
├── inject_disruption()
└── clear_disruption()
```

**Responsibilities**:
- Traffic flow simulation
- Queue dynamics
- Reward calculation
- State management

### 2. Data Models (`env/models.py`)

```
Pydantic Models
├── SignalPhase (Enum)
│   ├── NORTH_SOUTH_GREEN
│   ├── EAST_WEST_GREEN
│   └── ALL_RED
│
├── DisruptionType (Enum)
│   ├── LANE_CLOSURE
│   ├── DEMAND_SPIKE
│   ├── SENSOR_FAILURE
│   └── NONE
│
├── IntersectionState
│   ├── intersection_id: int
│   ├── queue_lengths: Dict[str, int]
│   ├── waiting_times: Dict[str, float]
│   ├── current_phase: SignalPhase
│   ├── phase_duration: int
│   ├── active_disruption: DisruptionType
│   └── disruption_severity: float
│
├── Observation
│   ├── intersections: List[IntersectionState]
│   ├── total_vehicles: int
│   ├── total_waiting_time: float
│   ├── throughput: int
│   ├── timestep: int
│   └── disruptions_active: int
│
├── Action
│   ├── intersection_id: int
│   ├── new_phase: SignalPhase
│   └── duration: int (5-60)
│
└── TrafficState
    ├── observation: Observation
    ├── reward: float
    ├── done: bool
    └── info: Dict
```

### 3. Disruption Wrapper (`env/disruption_wrapper.py`)

```
DisruptionWrapper
├── __init__(env, disruption_probability, duration_range, severity_range)
├── reset() → Observation
├── step(action) → (Observation, reward, done, info)
├── state() → TrafficState
├── _inject_random_disruption()
└── _update_disruptions()
```

**Responsibilities**:
- Automatic disruption injection
- Disruption lifecycle management
- Timer tracking
- Info augmentation

### 4. Task System (`tasks/task_configs.py`)

```
Task System
├── TaskConfig (Pydantic Model)
│   ├── name: str
│   ├── difficulty: str
│   ├── description: str
│   ├── num_intersections: int
│   ├── max_steps: int
│   ├── disruption_probability: float
│   ├── target_throughput: int
│   └── max_avg_waiting_time: float
│
├── TASKS: Dict[str, TaskConfig]
│   ├── easy_single_intersection
│   ├── medium_multi_intersection
│   └── hard_network_resilience
│
├── GRADERS: Dict[str, Callable]
│   ├── grade_easy_task()
│   ├── grade_medium_task()
│   └── grade_hard_task()
│
└── get_task(task_name) → (config, grader)
```

## Data Flow

### Episode Execution Flow

```
1. Initialize
   ┌─────────────┐
   │ Create Env  │
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐
   │   reset()   │
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐
   │ Observation │
   └──────┬──────┘
          │
          ▼
2. Episode Loop ─────────────────────┐
   ┌─────────────┐                   │
   │ Agent/LLM   │                   │
   │ Decides     │                   │
   └──────┬──────┘                   │
          │                          │
          ▼                          │
   ┌─────────────┐                   │
   │   Action    │                   │
   └──────┬──────┘                   │
          │                          │
          ▼                          │
   ┌─────────────┐                   │
   │   step()    │                   │
   └──────┬──────┘                   │
          │                          │
          ├──► Simulate Traffic      │
          ├──► Update Queues         │
          ├──► Check Disruptions     │
          ├──► Calculate Reward      │
          │                          │
          ▼                          │
   ┌─────────────┐                   │
   │ Observation │                   │
   │   Reward    │                   │
   │    Done     │                   │
   │    Info     │                   │
   └──────┬──────┘                   │
          │                          │
          └──────────────────────────┘
          │ (if not done)
          │
          ▼ (if done)
3. Evaluation
   ┌─────────────┐
   │   Grader    │
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐
   │ Final Score │
   │  (0.0-1.0)  │
   └─────────────┘
```

### Disruption Injection Flow

```
DisruptionWrapper.step()
        │
        ▼
┌───────────────────┐
│ Random Check      │
│ (probability p)   │
└────────┬──────────┘
         │
    ┌────┴────┐
    │         │
   Yes       No
    │         │
    ▼         │
┌───────────┐ │
│ Inject    │ │
│ Disruption│ │
└─────┬─────┘ │
      │       │
      └───┬───┘
          │
          ▼
┌─────────────────┐
│ env.step()      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Update Timers   │
│ Clear Expired   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Return with     │
│ disruption info │
└─────────────────┘
```

## Reward Calculation

```
Reward Components
├── Waiting Time Penalty
│   └── -0.01 × total_waiting_time
│
├── Throughput Reward
│   └── +0.1 × vehicles_processed
│
├── Phase Change Penalty
│   └── -2.0 (if phase changed)
│
├── Queue Penalty
│   └── -0.05 × total_queue_length
│
└── Disruption Bonus
    └── +5.0 (if handling disruption well)
    
Total Reward = Sum of all components
```

## Grading System

### Easy Task Grader
```
Score = min(1.0, throughput_score + waiting_score)

where:
  throughput_score = min(0.6, (throughput / 150) × 0.6)
  waiting_score = max(0, 0.4 × (1 - avg_waiting / 50))
```

### Medium Task Grader
```
Score = min(1.0, throughput_score + waiting_score + disruption_score)

where:
  throughput_score = min(0.5, (throughput / 400) × 0.5)
  waiting_score = max(0, 0.3 × (1 - avg_waiting / 80))
  disruption_score = max(0, 0.2 × (1 - avg_queue / 30))
```

### Hard Task Grader
```
Score = min(1.0, throughput_score + waiting_score + resilience_score)

where:
  throughput_score = min(0.4, (throughput / 600) × 0.4)
  waiting_score = max(0, 0.3 × (1 - avg_waiting / 120))
  resilience_score = max(0, 0.3 × (1 - avg_queue / 40))
```

## Traffic Simulation Model

### Arrival Process
```
For each direction at each intersection:
  arrivals ~ Poisson(λ × disruption_factor)
  
where:
  λ = base_arrival_rate (0.3 vehicles/second)
  disruption_factor = 1.0 - (severity × 0.7)
  
Special case:
  If disruption_type == DEMAND_SPIKE:
    λ = λ × 2.0
```

### Service Process
```
For each direction at each intersection:
  if direction has green light:
    departures = min(queue_length, service_rate × phase_duration × disruption_factor)
    queue_length -= departures
    throughput += departures
    
where:
  service_rate = 0.5 vehicles/second
  disruption_factor = 1.0 - (severity × 0.7)
```

### Queue Dynamics
```
queue_length[t+1] = queue_length[t] + arrivals[t] - departures[t]

waiting_time[t+1] = {
  waiting_time[t] + 1.0,  if queue_length > 0
  max(0, waiting_time[t] - 0.5),  otherwise
}
```

## Deployment Architecture

### Local Development
```
Developer Machine
├── Python 3.10+
├── Virtual Environment
│   └── requirements.txt
├── Source Code
│   ├── env/
│   ├── tasks/
│   └── *.py
└── Validation Scripts
    ├── validate_env.py
    ├── quick_test.py
    └── example_usage.py
```

### Docker Container
```
Docker Image
├── Base: python:3.10-slim
├── System Dependencies
│   └── gcc
├── Python Dependencies
│   └── requirements.txt
├── Application Code
│   ├── env/
│   ├── tasks/
│   └── inference.py
└── Entry Point
    └── CMD ["python", "inference.py"]
```

### Hugging Face Space
```
HF Space
├── Repository
│   ├── Dockerfile
│   ├── app.py (entry point)
│   ├── All source files
│   └── .dockerignore
├── Secrets
│   ├── HF_TOKEN
│   ├── API_BASE_URL (optional)
│   └── MODEL_NAME (optional)
└── Runtime
    ├── 2 vCPU
    └── 8 GB RAM
```

## Integration Points

### LLM Integration
```
inference.py
├── OpenAI Client
│   ├── base_url: API_BASE_URL
│   └── api_key: HF_TOKEN
│
├── get_llm_action(observation)
│   ├── Format prompt
│   ├── Call LLM
│   ├── Parse response
│   └── Return Action
│
└── run_episode(task_name)
    ├── Create environment
    ├── Episode loop
    │   ├── Get LLM action
    │   ├── Execute step
    │   └── Log output
    └── Calculate score
```

### Output Format
```
[START] task=<name> env=<env> model=<model>
[STEP] step=<n> action=<json> reward=<r> done=<bool> error=<msg|null>
[STEP] step=<n> action=<json> reward=<r> done=<bool> error=<msg|null>
...
[END] success=<bool> steps=<n> rewards=<r1,r2,...,rn>
```

## Performance Characteristics

### Computational Complexity
- **reset()**: O(N) where N = num_intersections
- **step()**: O(N × D) where D = directions per intersection (4)
- **Memory**: O(N × D) for state storage

### Scalability
- Tested up to 5 intersections
- Linear scaling with number of intersections
- Suitable for 2 vCPU, 8 GB RAM constraint

### Typical Episode Duration
- Easy task: ~300 steps, ~5 seconds
- Medium task: ~500 steps, ~10 seconds
- Hard task: ~600 steps, ~15 seconds

## Extension Points

### Adding New Disruption Types
```python
# In env/models.py
class DisruptionType(str, Enum):
    LANE_CLOSURE = "lane_closure"
    DEMAND_SPIKE = "demand_spike"
    SENSOR_FAILURE = "sensor_failure"
    ACCIDENT = "accident"  # New!
    WEATHER = "weather"    # New!
```

### Adding New Tasks
```python
# In tasks/task_configs.py
TASKS["custom_task"] = TaskConfig(
    name="custom_task",
    difficulty="custom",
    description="Your description",
    num_intersections=4,
    max_steps=400,
    disruption_probability=0.2,
    target_throughput=500,
    max_avg_waiting_time=100.0
)

def grade_custom_task(env, info):
    # Your grading logic
    return score

GRADERS["custom_task"] = grade_custom_task
```

### Custom Policies
```python
class MyPolicy:
    def __init__(self):
        # Initialize policy
        pass
    
    def select_action(self, observation):
        # Your logic here
        return Action(...)
```

## Testing Strategy

### Unit Tests
- Pydantic model validation
- Environment state transitions
- Reward calculation
- Disruption injection

### Integration Tests
- Full episode execution
- Task grading
- LLM integration
- Docker build and run

### Validation Tests
- OpenEnv compliance
- Output format
- Hardware constraints
- Reproducibility

---

**This architecture supports**:
- ✅ Modularity and extensibility
- ✅ Type safety with Pydantic
- ✅ Clear separation of concerns
- ✅ Easy testing and validation
- ✅ Scalable deployment
