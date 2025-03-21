#!/bin/bash
echo "Waiting for MySQL to be ready..."
sleep 10  
exec uvicorn app.main:app --host 0.0.0.0 --port 8000