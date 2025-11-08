#!/bin/bash
# Start script for Render deployment

echo "🚀 Starting Multi-AI Agent API..."
echo "📝 Port: $PORT"
echo "🔧 Environment: Production"

# Run with gunicorn (production WSGI server)
exec gunicorn api:app \
    --bind 0.0.0.0:$PORT \
    --timeout 120 \
    --workers 2 \
    --access-logfile - \
    --error-logfile -
