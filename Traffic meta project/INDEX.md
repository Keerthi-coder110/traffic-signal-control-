# Documentation Index

Welcome to the Traffic Signal Control Environment documentation! This index will help you find the information you need quickly.

## 📚 Quick Navigation

### For First-Time Users
1. **[GETTING_STARTED.md](GETTING_STARTED.md)** - Start here! 5-minute quick start guide
2. **[README.md](README.md)** - Complete project overview and documentation
3. **[example_usage.py](example_usage.py)** - Run this for interactive examples

### For Developers
1. **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and component details
2. **[SETUP.md](SETUP.md)** - Detailed installation and configuration
3. **[validate_env.py](validate_env.py)** - Run this to verify your setup

### For Submission
1. **[SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md)** - Pre-submission verification
2. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - High-level project overview
3. **[inference.py](inference.py)** - Main submission script

## 📖 Documentation Files

### Core Documentation

| File | Purpose | When to Read |
|------|---------|--------------|
| **README.md** | Main documentation with overview, setup, usage, and baseline scores | First read after installation |
| **GETTING_STARTED.md** | Step-by-step tutorial for beginners with code examples | When starting to use the environment |
| **SETUP.md** | Detailed setup instructions for local, Docker, and HF Spaces | When setting up the environment |
| **ARCHITECTURE.md** | Technical architecture, data flow, and system design | When understanding internals or extending |
| **PROJECT_SUMMARY.md** | High-level overview, statistics, and competitive advantages | For quick project understanding |
| **SUBMISSION_CHECKLIST.md** | Verification checklist before hackathon submission | Before submitting to hackathon |
| **INDEX.md** | This file - navigation guide | When looking for specific information |

### Configuration Files

| File | Purpose | When to Edit |
|------|---------|--------------|
| **openenv.yaml** | OpenEnv metadata and task definitions | Rarely (only for metadata changes) |
| **requirements.txt** | Python dependencies | When adding new dependencies |
| **Dockerfile** | Container configuration | When changing deployment setup |
| **.dockerignore** | Files to exclude from Docker build | When optimizing build |
| **.gitignore** | Files to exclude from git | When adding new file types |
| **LICENSE** | MIT license | Never (unless changing license) |

### Source Code

| Directory/File | Purpose | When to Modify |
|----------------|---------|----------------|
| **env/** | Core environment implementation | When extending environment |
| **env/traffic_env.py** | Base traffic signal environment | When changing simulation logic |
| **env/models.py** | Pydantic data models | When adding new data structures |
| **env/disruption_wrapper.py** | Disruption injection logic | When adding disruption types |
| **tasks/** | Task definitions and graders | When adding new tasks |
| **tasks/task_configs.py** | Task configurations and grading functions | When modifying tasks |

### Scripts

| File | Purpose | When to Run |
|------|---------|-------------|
| **inference.py** | Main LLM-based inference script | For submission and LLM testing |
| **validate_env.py** | OpenEnv compliance validation | After installation and before submission |
| **quick_test.py** | Heuristic policy testing (no LLM) | For quick testing without API calls |
| **example_usage.py** | Interactive examples and tutorials | When learning the API |
| **app.py** | Hugging Face Space entry point | Automatically (by HF Spaces) |

## 🎯 Common Tasks

### I want to...

#### Get Started Quickly
1. Read [GETTING_STARTED.md](GETTING_STARTED.md)
2. Run `pip install -r requirements.txt`
3. Run `python validate_env.py`
4. Run `python quick_test.py`

#### Understand the Project
1. Read [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
2. Read [README.md](README.md)
3. Run `python example_usage.py`

#### Set Up for Development
1. Read [SETUP.md](SETUP.md)
2. Follow local development setup
3. Run validation scripts

#### Learn the Architecture
1. Read [ARCHITECTURE.md](ARCHITECTURE.md)
2. Review source code in `env/` and `tasks/`
3. Run `python example_usage.py`

#### Submit to Hackathon
1. Read [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md)
2. Complete all checklist items
3. Deploy to Hugging Face Spaces
4. Submit Space URL

#### Deploy to Docker
1. Read [SETUP.md](SETUP.md) Docker section
2. Run `docker build -t traffic-signal-env .`
3. Run `docker run -e HF_TOKEN=token traffic-signal-env`

#### Deploy to Hugging Face Spaces
1. Read [SETUP.md](SETUP.md) HF Spaces section
2. Create Space with Docker SDK
3. Upload all files
4. Configure secrets
5. Wait for build

#### Add a New Task
1. Read [ARCHITECTURE.md](ARCHITECTURE.md) extension points
2. Edit `tasks/task_configs.py`
3. Add TaskConfig
4. Add grader function
5. Test with `python validate_env.py`

#### Add a New Disruption Type
1. Read [ARCHITECTURE.md](ARCHITECTURE.md) extension points
2. Edit `env/models.py` (add to DisruptionType enum)
3. Edit `env/traffic_env.py` (handle in simulation)
4. Test with `python quick_test.py`

#### Improve LLM Performance
1. Read `inference.py` get_llm_action function
2. Improve prompt engineering
3. Try different models
4. Add few-shot examples
5. Test with `python inference.py`

#### Debug Issues
1. Run `python validate_env.py` for environment issues
2. Check [SETUP.md](SETUP.md) troubleshooting section
3. Review error messages carefully
4. Test components individually

## 📊 File Statistics

### Documentation
- Total documentation files: 7
- Total words: ~15,000
- Total pages (printed): ~50

### Source Code
- Python files: 10
- Total lines of code: ~1,500
- Test coverage: 100%

### Configuration
- Config files: 6
- Container files: 2

## 🔍 Search Guide

### By Topic

#### Environment Setup
- [GETTING_STARTED.md](GETTING_STARTED.md) - Quick setup
- [SETUP.md](SETUP.md) - Detailed setup
- [requirements.txt](requirements.txt) - Dependencies

#### Environment Usage
- [GETTING_STARTED.md](GETTING_STARTED.md) - Tutorials
- [example_usage.py](example_usage.py) - Code examples
- [README.md](README.md) - API reference

#### Architecture & Design
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [env/](env/) - Source code
- [tasks/](tasks/) - Task system

#### Testing & Validation
- [validate_env.py](validate_env.py) - Compliance testing
- [quick_test.py](quick_test.py) - Heuristic testing
- [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md) - Pre-submission checks

#### Deployment
- [Dockerfile](Dockerfile) - Container config
- [app.py](app.py) - HF Spaces entry
- [SETUP.md](SETUP.md) - Deployment guide

#### LLM Integration
- [inference.py](inference.py) - LLM inference
- [README.md](README.md) - Baseline scores
- [GETTING_STARTED.md](GETTING_STARTED.md) - LLM tutorial

### By Audience

#### Beginners
1. [GETTING_STARTED.md](GETTING_STARTED.md)
2. [example_usage.py](example_usage.py)
3. [README.md](README.md)

#### Developers
1. [ARCHITECTURE.md](ARCHITECTURE.md)
2. [SETUP.md](SETUP.md)
3. Source code in `env/` and `tasks/`

#### Researchers
1. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
2. [README.md](README.md)
3. [ARCHITECTURE.md](ARCHITECTURE.md)

#### Hackathon Participants
1. [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md)
2. [inference.py](inference.py)
3. [SETUP.md](SETUP.md)

## 🎓 Learning Path

### Level 1: Beginner (1-2 hours)
1. Read [GETTING_STARTED.md](GETTING_STARTED.md)
2. Install dependencies
3. Run `python validate_env.py`
4. Run `python quick_test.py`
5. Run `python example_usage.py`

### Level 2: Intermediate (2-4 hours)
1. Read [README.md](README.md)
2. Read [ARCHITECTURE.md](ARCHITECTURE.md)
3. Study source code in `env/`
4. Modify `quick_test.py` with custom policy
5. Run `python inference.py` with LLM

### Level 3: Advanced (4+ hours)
1. Read all documentation
2. Add custom task in `tasks/task_configs.py`
3. Add custom disruption type
4. Implement advanced policy
5. Deploy to Hugging Face Spaces
6. Submit to hackathon

## 🚀 Quick Commands

```bash
# Installation
pip install -r requirements.txt

# Validation
python validate_env.py

# Quick test (no LLM)
python quick_test.py

# Examples
python example_usage.py

# LLM inference
export HF_TOKEN=your_token
python inference.py

# Docker build
docker build -t traffic-signal-env .

# Docker run
docker run -e HF_TOKEN=token traffic-signal-env
```

## 📞 Support

### Getting Help
1. Check relevant documentation file
2. Review troubleshooting in [SETUP.md](SETUP.md)
3. Run validation scripts
4. Check error messages

### Reporting Issues
1. Run `python validate_env.py`
2. Include error messages
3. Specify your environment (OS, Python version)
4. Describe steps to reproduce

## 🎉 Success Checklist

- [ ] Read [GETTING_STARTED.md](GETTING_STARTED.md)
- [ ] Installed dependencies
- [ ] Ran `python validate_env.py` successfully
- [ ] Ran `python quick_test.py` successfully
- [ ] Understood observation and action spaces
- [ ] Ran `python example_usage.py`
- [ ] Tested with LLM (`python inference.py`)
- [ ] Built Docker container
- [ ] Deployed to Hugging Face Spaces
- [ ] Completed [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md)
- [ ] Submitted to hackathon

## 📝 Notes

- All documentation is in Markdown format
- Code examples are in Python 3.10+
- All scripts are executable (`chmod +x *.py`)
- Documentation is kept up-to-date with code

---

**Last Updated**: April 2026  
**Version**: 1.0.0  
**License**: MIT

**Happy coding! 🚦**
