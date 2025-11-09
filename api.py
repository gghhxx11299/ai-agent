#!/usr/bin/env python3
"""
REST API for Multi-AI Agent System
Exposes endpoints for testing with Thunder Client or Postman
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import asyncio
import os
import sys
import logging
from datetime import datetime
from src.orchestrator import Orchestrator
from config.config import validate_config

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates')
CORS(app)  # Enable CORS for all routes

# Initialize orchestrator
orchestrator = None
orchestrator_lock = asyncio.Lock()


def get_orchestrator():
    """Get or create orchestrator instance (thread-safe)"""
    global orchestrator
    if orchestrator is None:
        try:
            # Suppress console output in production
            import io
            from contextlib import redirect_stdout, redirect_stderr
            
            # Redirect stdout/stderr to avoid breaking in production
            f = io.StringIO()
            with redirect_stdout(f), redirect_stderr(f):
                orchestrator = Orchestrator()
            logger.info(f"Orchestrator initialized with {len(orchestrator.ai_models)} AI model(s)")
        except Exception as e:
            logger.error(f"Failed to initialize orchestrator: {e}")
            raise
    return orchestrator


@app.route('/', methods=['GET'])
def home():
    """Serve the HTML frontend"""
    return render_template('index.html')


@app.route('/api', methods=['GET'])
def api_info():
    """API information endpoint"""
    return jsonify({
        'status': 'online',
        'service': 'Multi-AI Agent System',
        'version': '1.0.0',
        'ai_models': {
            'primary': 'Gemini (gemini-2.5-flash)',
            'fallback_1': 'Groq (llama-3.3-70b-versatile)',
            'fallback_2': 'OpenRouter (claude-3.5-sonnet)'
        },
        'endpoints': {
            'GET /': 'HTML frontend',
            'GET /api': 'API information',
            'GET /health': 'Health check',
            'POST /query': 'Send a query to the AI',
            'POST /chat': 'Chat with the AI (alias for /query)',
            'GET /models': 'List available AI models',
            'GET /status': 'Get system status'
        },
        'documentation': 'Send POST to /query with {"query": "your question"}',
        'example': {
            'url': 'POST /query',
            'body': {
                'query': 'What is the weather in London?'
            }
        }
    }), 200


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint - lightweight, doesn't require orchestrator"""
    try:
        # Simple health check without initializing orchestrator
        return jsonify({
            'status': 'healthy',
            'service': 'Multi-AI Agent System',
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


@app.route('/models', methods=['GET'])
def models():
    """List available AI models"""
    try:
        orch = get_orchestrator()
        return jsonify({
            'current_ai': orch.ai_name,
            'available_models': [name for name, _ in orch.ai_models],
            'total_models': len(orch.ai_models)
        }), 200
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/status', methods=['GET'])
def status():
    """Get detailed system status"""
    try:
        orch = get_orchestrator()
        return jsonify({
            'system': 'Multi-AI Agent System',
            'status': 'operational',
            'ai': {
                'current': orch.ai_name,
                'available': [name for name, _ in orch.ai_models],
                'count': len(orch.ai_models)
            },
            'features': {
                'web_search': True,
                'weather_data': True,
                'global_locations': True,
                'agricultural_data': True
            },
            'data_sources': {
                'web_search': 'DuckDuckGo (free)',
                'weather': 'Open-Meteo (free)',
                'agriculture': 'Mock data'
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/query', methods=['POST'])
def query():
    """
    Process a query through the AI system

    Request body:
    {
        "query": "Your question here"
    }
    """
    try:
        # Get JSON data
        data = request.get_json()

        if not data or 'query' not in data:
            return jsonify({
                'error': 'Missing required field: query',
                'example': {
                    'query': 'What is the weather in London?'
                }
            }), 400

        user_query = data['query']

        if not user_query or not user_query.strip():
            return jsonify({
                'error': 'Query cannot be empty'
            }), 400

        # Process query
        orch = get_orchestrator()

        # Handle async properly for production (Flask/Gunicorn)
        try:
            # Try to get existing event loop
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # Create new event loop if none exists
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Run async function
        if loop.is_running():
            # If loop is already running, we need to use a different approach
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    lambda: asyncio.run(orch.process_query(user_query))
                )
                response = future.result(timeout=120)
        else:
            response = loop.run_until_complete(orch.process_query(user_query))

        return jsonify({
            'success': True,
            'query': user_query,
            'response': response,
            'ai_model': orch.ai_name
        }), 200

    except asyncio.TimeoutError:
        return jsonify({
            'success': False,
            'error': 'Request timeout - the query took too long to process',
            'query': data.get('query', '') if data else ''
        }), 504
    except Exception as e:
        logger.error(f"Query error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'query': data.get('query', '') if data else ''
        }), 500


@app.route('/chat', methods=['POST'])
def chat():
    """Alias for /query endpoint"""
    return query()


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': {
            'GET /': 'API information',
            'GET /health': 'Health check',
            'POST /query': 'Send a query',
            'POST /chat': 'Chat (alias)',
            'GET /models': 'List models',
            'GET /status': 'System status'
        }
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error',
        'message': str(error)
    }), 500


if __name__ == '__main__':
    # Validate configuration on startup (but don't exit on failure in production)
    try:
        validate_config()
        logger.info("Configuration validated")
    except Exception as e:
        logger.warning(f"Configuration error: {e}")
        # Don't exit in production, allow the app to start and handle errors gracefully
        if os.environ.get('FLASK_ENV') == 'development':
            exit(1)

    # Get port from environment or use 5000
    port = int(os.environ.get('PORT', 5000))

    # Run the Flask app
    logger.info(f"Starting Multi-AI Agent API on port {port}")
    logger.info(f"API Documentation: http://localhost:{port}/")

    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.environ.get('FLASK_ENV') == 'development'
    )
