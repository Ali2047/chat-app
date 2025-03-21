#!/bin/bash
echo "Waiting for MySQL to be ready..."
sleep 10  # Wait for 10 seconds to ensure MySQL is ready
exec uvicorn app.main:app --host 0.0.0.0 --port 8000