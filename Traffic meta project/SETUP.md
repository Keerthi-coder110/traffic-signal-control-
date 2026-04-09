# Setup Guide

This guide will help you set up and run the Traffic Signal Control environment locally and deploy it to Hugging Face Spaces.

## Prerequisites

- Python 3.10 or higher
- Docker (for containerized deployment)
- Hugging Face account (for Spaces deployment)
- OpenAI API key or compatible LLM API

## Local Development Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd traffic-signal-env
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Validate Environment

Run the validation script to ensure everything is set up correctly:

```bash
python validate_env.py
```

You should see all checks pass:
```
✓ PASS: OpenEnv Interface
✓ PASS: Pydantic Models
✓ PASS: DisruptionWrapper
✓ PASS: Tasks
```

### 5. Quick Test (No LLM Required)

Test the environment with a simple heuristic policy:

```bash
python quick_test.py
```

This will run all three tasks and show baseline performance without requiring API calls.

### 6. Run Full Inference

Set up your environment variables:

```bash
# Required
export HF_TOKEN=your_huggingface_token

# Optional (with defaults)
export API_BASE_URL=https://api.openai.com/v1
export MODEL_NAME=gpt-4o-mini
```

Run the inference script:

```bash
python inference.py
```

## Docker Setup

### Build the Container

```bash
docker build -t traffic-signal-env .
```

### Run the Container

```bash
docker run -e HF_TOKEN=your_token traffic-signal-env
```

### Test with Custom Model

```bash
docker run \
  -e HF_TOKEN=your_token \
  -e API_BASE_URL=https://api.together.xyz/v1 \
  -e MODEL_NAME=meta-llama/Llama-3-70b-chat-hf \
  traffic-signal-env
```

## Hugging Face Spaces Deployment

### 1. Create a New Space

1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Choose a name (e.g., `traffic-signal-control`)
4. Select "Docker" as the SDK
5. Choose "Public" or "Private"

### 2. Configure Space Settings

In your Space settings, add these secrets:

- `HF_TOKEN`: Your Hugging Face API token (required)
- `API_BASE_URL`: Your LLM API endpoint (optional)
- `MODEL_NAME`: Your model identifier (optional)

### 3. Upload Files

You can either:

**Option A: Git Push**
```bash
git remote add space https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
git push space main
```

**Option B: Web Upload**
Upload all files through the Hugging Face web interface.

### 4. Wait for Build

The Space will automatically build using the Dockerfile. This may take 5-10 minutes.

### 5. Verify Deployment

Once the Space shows "Running", check the logs to see the inference results.

## Troubleshooting

### Issue: "HF_TOKEN environment variable is required"

**Solution**: Make sure you've set the HF_TOKEN environment variable:
```bash
export HF_TOKEN=your_token
```

### Issue: Docker build fails

**Solution**: Ensure you have enough disk space and Docker is running:
```bash
docker system prune  # Clean up old images
docker info          # Check Docker status
```

### Issue: OpenEnv validation fails

**Solution**: Make sure all dependencies are installed:
```bash
pip install -r requirements.txt --upgrade
```

### Issue: LLM API errors

**Solution**: Check your API credentials and endpoint:
```bash
# Test API connection
curl -H "Authorization: Bearer $HF_TOKEN" $API_BASE_URL/models
```

### Issue: Space stuck in "Building" state

**Solution**: 
1. Check if you have other Spaces running (turn them off)
2. Verify Dockerfile syntax
3. Check Space logs for error messages

## Performance Optimization

### Reduce API Calls

Modify `inference.py` to cache LLM responses or use a local model:

```python
# Use a smaller, faster model
MODEL_NAME = "gpt-3.5-turbo"

# Or use a local model with Ollama
API_BASE_URL = "http://localhost:11434/v1"
MODEL_NAME = "llama2"
```

### Adjust Task Difficulty

Edit `tasks/task_configs.py` to modify task parameters:

```python
TASKS["easy_single_intersection"].max_steps = 200  # Shorter episodes
TASKS["easy_single_intersection"].disruption_probability = 0.02  # Fewer disruptions
```

## Development Tips

### Running Individual Tasks

```python
from env import TrafficSignalEnv, DisruptionWrapper
from tasks import get_task

config, grader = get_task("easy_single_intersection")
env = TrafficSignalEnv(config.num_intersections, config.max_steps)
# ... your code
```

### Debugging Disruptions

```python
from env import TrafficSignalEnv, DisruptionWrapper
from env.models import DisruptionType

env = TrafficSignalEnv(num_intersections=1, max_steps=100)
env.reset()

# Manually inject disruption
env.inject_disruption(0, DisruptionType.LANE_CLOSURE, severity=0.8)

# Check state
obs = env._get_observation()
print(obs.intersections[0].active_disruption)
```

### Custom Grading

Create your own grader in `tasks/task_configs.py`:

```python
def my_custom_grader(env, info):
    # Your grading logic
    score = calculate_score(env, info)
    return min(1.0, max(0.0, score))

GRADERS["my_task"] = my_custom_grader
```

## Next Steps

1. Experiment with different prompting strategies in `inference.py`
2. Try different LLM models
3. Implement custom policies (RL, rule-based, hybrid)
4. Add visualization of traffic flow
5. Extend with more disruption types
6. Fine-tune models on traffic control tasks

## Support

For issues or questions:
- Open an issue on GitHub
- Check the README.md for detailed documentation
- Review the validation output for specific errors

## Resources

- [OpenEnv Documentation](https://github.com/meta-pytorch/OpenEnv)
- [Hugging Face Spaces Guide](https://huggingface.co/docs/hub/spaces)
- [Docker Documentation](https://docs.docker.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
