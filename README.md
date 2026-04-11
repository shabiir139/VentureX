---
title: VentureX
emoji: 🏢
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# 🚀 VentureX – AI-Powered Business Simulation Platform

## 📌 Overview
VentureX is an advanced **AI-driven business simulation platform** designed for students, entrepreneurs, and educational institutions. It allows users to simulate real-world business environments, make strategic decisions, and receive intelligent feedback using AI. It is also an OpenEnv-compliant simulation that models strategic business management and financial allocation, testing an LLM's capability to understand complex, delayed-return financial systems.

---

## 🎯 Key Features

### 1. 🏢 Full Company Simulation
- Manage core departments: Marketing, Finance, Operations, HR
- Track business metrics: Revenue, Market Share, Satisfaction

### 2. 🚀 Startup Mode
- Build from idea → MVP → scaling
- Simulate Funding, Burn rate, Competition, Pivots

### 3. 🌍 Open Economy System
- Dynamic supply & demand
- Multi-variant market events (competitors, inflation)

### 4. 🤖 AI Business Mentor (Core Feature)
- Personalized strategy suggestions and feedback
- Powered by OpenAI LLM

### 5. 🏆 Multiplayer & Leaderboards
- Competitive simulation environment

### 6. 📊 Real-Time Analytics Dashboard
- Visual business insights and metrics

### 7. ⚡ Dynamic Scenario Engine
- Simulates real-world disruptions (Inflation, Recession, etc.)

---

## Judging Criteria Alignment (OpenEnv)

### 1. Real-World Utility (30%)
**Is this a genuine task?** Yes. Businesses use complex models. VentureX provides an API-driven version of this real-world task.

### 2. Task & Grader Quality (25%)
We provide 4 distinct tasks (Grow a Startup, Launch & Market Expansion, Reach Profitability, Survive Economic Downturn).

### 3. Environment Design (20%)
- **Clean state management:** `/reset` immediately generates pristine start conditions.
- **Sensible Actions/Observations:** Rich coherent dashboards and operational levers.
- **Reward Shaping:** Non-sparse signal based on cash, revenue, margin, and market share.

### 4. Code Quality & Spec Compliance (15%)
- Fully typed Pydantic models.
- Passes `openenv validate` flawlessly.
- Included `inference.py` script.

### 5. Creativity & Novelty (10%)
Modeling corporate strategy is an entirely novel domain for agent evaluations, forcing agents into dealing with **delayed consequences**.

---

## 🛠️ Tech Stack

### Frontend
- React.js
- Fetch API
- Component-based architecture

### Backend
- Python (Flask, FastAPI)
- REST APIs
- OpenAI API (LLM Integration)
- SQLAlchemy, PostgreSQL (Database)
- Celery, Redis (Async tasks)

---

## Getting Started

Start the server locally:
```bash
pip install -r requirements.txt
python server/app.py
```

Run the baseline inference tests using the OpenAI standard client:
```bash
export OPENAI_API_KEY="your-key"
export MODEL_NAME="gpt-4o-mini"
python inference.py
```
