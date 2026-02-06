# AI Agent Development Workflow for PhotoSift

This document outlines the standard procedure for an AI agent (like Little Pretty A) to contribute to the PhotoSift project. This process ensures high code quality, security, and a clear audit trail for the human developer.

## Core Principles

1.  **AI-Human Collaboration:** The AI agent handles code generation and initial testing, while the human developer (Master) provides high-level direction, architectural decisions, and final quality assurance.
2.  **Privacy & Security:** The agent must never disclose personal information and must obtain approval before accessing sensitive credentials.
3.  **Local First:** All development and initial testing are performed in the local environment.

## Step-by-Step Workflow

### 1. Task Definition
The human developer defines a task, bug fix, or feature request. The agent clarifies the requirements before starting.

### 2. Feature Branching
For every new task, the agent creates a dedicated feature branch from the latest `master` branch.
```bash
git checkout master
git pull origin master
git checkout -b feature/your-task-name
```

### 3. Implementation & Local Testing
The agent implements the changes and runs local tests to ensure correctness and prevent regressions.
```bash
# Example: Run all tests
python tests/run_all_tests.py
```

### 4. Commit Changes
The agent commits the changes with a descriptive message that notes the AI collaboration.
```bash
git add .
git commit -m "Add [feature/fix] - AI-human collaboration"
```

### 5. Push to GitHub
The agent pushes the feature branch to the remote repository.
```bash
git push origin feature/your-task-name
```

### 6. Pull Request (PR)
The agent creates a Pull Request from the feature branch to the `master` branch. The PR description must include:
*   A clear summary of the changes.
*   Details of the local tests performed.
*   Any architectural decisions made.

### 7. Review & Merge
The human developer (Master) reviews the PR.
*   If changes are requested, the agent applies them to the same branch and pushes again.
*   If approved, the human developer merges the PR into `master`.

### 8. Cleanup
Once the PR is merged, the local and remote feature branches are deleted.
```bash
git checkout master
git pull origin master
git branch -d feature/your-task-name
git push origin --delete feature/your-task-name
```
