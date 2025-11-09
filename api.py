#!/usr/bin/env python3
"""
REST API for Multi-AI Agent System
Exposes endpoints for testing with Thunder Client or Postman
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import asyncio
import os
from src.orchestrator import Orchestrator
from config.config import validate_config

app = Flask(__name__, template_folder='templates')
CORS(app)  # Enable CORS for all routes

# Initialize orchestrator
orchestrator = None


def get_orchestrator():
    """Get or create orchestrator instance"""
    global orchestrator
    if orchestrator is None:
        orchestrator = Orchestrator()
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
    """Health check endpoint"""
    try:
        orch = get_orchestrator()
        return jsonify({
            'status': 'healthy',
            'ai_available': True,
            'current_ai': orch.ai_name,
            'models_loaded': len(orch.ai_models)
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

        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(orch.process_query(user_query))
        loop.close()

        return jsonify({
            'success': True,
            'query': user_query,
            'response': response,
            'ai_model': orch.ai_name
        }), 200

    except Exception as e:
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
    # Validate configuration on startup
    try:
        validate_config()
        print("✓ Configuration validated")
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        exit(1)

    # Get port from environment or use 5000
    port = int(os.environ.get('PORT', 5000))

    # Run the Flask app
    print(f"🚀 Starting Multi-AI Agent API on port {port}")
    print(f"📝 API Documentation: http://localhost:{port}/")

    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.environ.get('FLASK_ENV') == 'development'
    )
