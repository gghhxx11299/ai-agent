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
    Compatible with MeshCore and standard API clients

    Request body:
    {
        "query": "Your question here"
    }
    
    Also accepts:
    {
        "message": "Your question here"
    }
    or
    {
        "input": "Your question here"
    }
    """
    try:
        # Get JSON data
        data = request.get_json() or {}
        
        # Support multiple input field names for MeshCore compatibility
        user_query = (
            data.get('query') or 
            data.get('message') or 
            data.get('input') or 
            data.get('text') or
            ''
        )

        if not user_query or not user_query.strip():
            return jsonify({
                'success': False,
                'error': 'Missing required field: query, message, or input',
                'example': {
                    'query': 'What is the weather in London?'
                }
            }), 400

        # Process query
        try:
            orch = get_orchestrator()
        except Exception as e:
            logger.error(f"Failed to get orchestrator: {e}")
            return jsonify({
                'success': False,
                'error': 'AI service unavailable. Please configure API keys in environment variables.',
                'message': str(e)
            }), 503

        # Handle async properly for production (Flask/Gunicorn)
        try:
            # Create new event loop for each request (safer for production)
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    lambda: asyncio.run(orch.process_query(user_query))
                )
                response = future.result(timeout=120)
        except concurrent.futures.TimeoutError:
            return jsonify({
                'success': False,
                'error': 'Request timeout - the query took too long to process',
                'query': user_query
            }), 504
        except Exception as e:
            logger.error(f"Query processing error: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': 'Failed to process query',
                'message': str(e),
                'query': user_query
            }), 500

        # Return response in MeshCore-compatible format
        return jsonify({
            'success': True,
            'query': user_query,
            'response': response,
            'answer': response,  # MeshCore compatibility
            'message': response,  # MeshCore compatibility
            'ai_model': orch.ai_name,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Query endpoint error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@app.route('/chat', methods=['POST'])
def chat():
    """Alias for /query endpoint - MeshCore compatible"""
    return query()


@app.route('/v1/chat', methods=['POST'])
def chat_v1():
    """MeshCore v1 API compatible endpoint"""
    return query()


@app.route('/v1/completions', methods=['POST'])
def completions_v1():
    """OpenAI-compatible completions endpoint for MeshCore"""
    try:
        data = request.get_json() or {}
        user_query = data.get('prompt') or data.get('message') or data.get('query') or ''
        
        if not user_query:
            return jsonify({
                'error': {
                    'message': 'Missing required field: prompt, message, or query',
                    'type': 'invalid_request_error'
                }
            }), 400
        
        # Process query
        try:
            orch = get_orchestrator()
        except Exception as e:
            return jsonify({
                'error': {
                    'message': 'AI service unavailable',
                    'type': 'service_error'
                }
            }), 503
        
        # Handle async
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                lambda: asyncio.run(orch.process_query(user_query))
            )
            response = future.result(timeout=120)
        
        # Return OpenAI-compatible format
        return jsonify({
            'id': f'chatcmpl-{datetime.now().timestamp()}',
            'object': 'chat.completion',
            'created': int(datetime.now().timestamp()),
            'model': orch.ai_name,
            'choices': [{
                'index': 0,
                'message': {
                    'role': 'assistant',
                    'content': response
                },
                'finish_reason': 'stop'
            }],
            'usage': {
                'prompt_tokens': len(user_query.split()),
                'completion_tokens': len(response.split()),
                'total_tokens': len(user_query.split()) + len(response.split())
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Completions error: {e}", exc_info=True)
        return jsonify({
            'error': {
                'message': str(e),
                'type': 'internal_error'
            }
        }), 500


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
