#!/bin/bash

# Start Gunicorn processes
echo Starting Server.
uvicorn app.main:app --proxy-headers --host 0.0.0.0 --port 8862 --reload # --log-level=trace
