#!/bin/bash
# Start backend
cd /home/user/DQM/backend && pip install -r requirements.txt -q && uvicorn main:app --reload --port 8000 &
# Start frontend
cd /home/user/DQM/frontend && npm install && npm run dev
