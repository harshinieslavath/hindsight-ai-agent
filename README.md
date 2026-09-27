# 🧠 Hindsight AI Agent

An AI agent with long-term memory that can remember user preferences, recall previous interactions, and adapt when preferences change.

## 🚀 Project Overview

This project demonstrates an AI agent that uses **Hindsight** as its persistent memory layer.

The agent can:

- Remember important user preferences
- Recall relevant information from previous conversations
- Learn when a user changes their preference
- Use newer preferences instead of outdated ones
- Persist memories even after restarting the backend

## 🏗️ Architecture

```text
User
  ↓
Frontend UI
  ↓
FastAPI Backend
  ↓
AI Agent
  ├── Hindsight → Long-Term Memory
  └── Groq → LLM Response