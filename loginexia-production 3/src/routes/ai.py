from flask import Blueprint, request, jsonify
from src.services.auth_service import token_required, api_key_required
from src.services.ai_service import AIService
from src.services.rider_service import RiderExternalService

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/nl-to-sql', methods=['POST'])
@token_required
def natural_language_to_sql(current_user):
    """Convert natural language query to SQL"""
    try:
        data = request.get_json()
        natural_query = data.get('query')
        
        if not natural_query:
            return jsonify({'error': 'Query is required'}), 400
        
        ai_service = AIService()
        result = ai_service.generate_sql_from_nl(
            natural_query, 
            current_user.organization_id
        )
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/query-knowledge', methods=['POST'])
@token_required
def query_knowledge_base(current_user):
    """Query the knowledge base using RAG"""
    try:
        data = request.get_json()
        question = data.get('question')
        context_docs = data.get('context_docs')
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        ai_service = AIService()
        result = ai_service.query_knowledge_base(
            question, 
            current_user.organization_id,
            context_docs
        )
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/recommendations', methods=['POST'])
@token_required
def get_recommendations(current_user):
    """Get AI-powered recommendations"""
    try:
        data = request.get_json()
        recommendation_type = data.get('type', 'general')
        city_id = data.get('city_id')
        
        if not city_id:
            return jsonify({'error': 'City ID is required'}), 400
        
        # Get rider data for the city
        rider_service = RiderExternalService(current_user.organization)
        rider_data = rider_service.get_live_riders(city_id)
        
        ai_service = AIService()
        result = ai_service.generate_recommendations(
            rider_data,
            recommendation_type=recommendation_type
        )
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/analyze-sentiment', methods=['POST'])
@token_required
def analyze_sentiment(current_user):
    """Analyze sentiment of text (for support tickets, feedback, etc.)"""
    try:
        data = request.get_json()
        text = data.get('text')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        ai_service = AIService()
        result = ai_service.analyze_sentiment(text)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/chat', methods=['POST'])
@token_required
def ai_chat(current_user):
    """General AI chat assistant for rider management"""
    try:
        data = request.get_json()
        message = data.get('message')
        context = data.get('context', 'general')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        ai_service = AIService()
        
        # Determine the type of query and route accordingly
        if any(keyword in message.lower() for keyword in ['sql', 'query', 'database', 'select', 'count']):
            # Treat as NL to SQL query
            result = ai_service.generate_sql_from_nl(message, current_user.organization_id)
            result['type'] = 'sql_query'
        else:
            # Treat as knowledge base query
            result = ai_service.query_knowledge_base(message, current_user.organization_id)
            result['type'] = 'knowledge_query'
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/smart-alerts', methods=['POST'])
@token_required
def generate_smart_alerts(current_user):
    """Generate intelligent alerts based on rider patterns"""
    try:
        data = request.get_json()
        city_id = data.get('city_id')
        
        if not city_id:
            return jsonify({'error': 'City ID is required'}), 400
        
        # Get current rider data
        rider_service = RiderExternalService(current_user.organization)
        rider_data = rider_service.get_live_riders(city_id)
        
        ai_service = AIService()
        
        # Generate recommendations specifically for alerts
        recommendations = ai_service.generate_recommendations(
            rider_data,
            recommendation_type='alerts'
        )
        
        # Analyze patterns and suggest proactive measures
        pattern_analysis = ai_service.query_knowledge_base(
            f"Based on the current rider data, what patterns should we watch for potential issues?",
            current_user.organization_id,
            f"Current rider data: {rider_data}"
        )
        
        result = {
            'recommendations': recommendations,
            'pattern_analysis': pattern_analysis,
            'city_id': city_id,
            'generated_at': recommendations.get('generated_at')
        }
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/performance-insights', methods=['POST'])
@token_required
def get_performance_insights(current_user):
    """Get AI-powered performance insights"""
    try:
        data = request.get_json()
        city_id = data.get('city_id')
        time_period = data.get('time_period', 'today')
        
        if not city_id:
            return jsonify({'error': 'City ID is required'}), 400
        
        # Get rider and company data
        rider_service = RiderExternalService(current_user.organization)
        rider_data = rider_service.get_live_riders(city_id)
        company_data = rider_service.get_companies_overview(city_id)
        
        ai_service = AIService()
        
        # Generate performance recommendations
        performance_recs = ai_service.generate_recommendations(
            rider_data,
            recommendation_type='performance'
        )
        
        # Generate scheduling recommendations
        scheduling_recs = ai_service.generate_recommendations(
            rider_data,
            recommendation_type='scheduling'
        )
        
        # Analyze overall performance
        performance_analysis = ai_service.query_knowledge_base(
            f"Analyze the performance data and provide insights on operational efficiency for {time_period}",
            current_user.organization_id,
            f"Rider data: {rider_data}\nCompany data: {company_data}"
        )
        
        result = {
            'performance_recommendations': performance_recs,
            'scheduling_recommendations': scheduling_recs,
            'performance_analysis': performance_analysis,
            'city_id': city_id,
            'time_period': time_period
        }
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API Key endpoints for external integrations
@ai_bp.route('/api/recommendations', methods=['POST'])
@api_key_required
def api_get_recommendations(organization):
    """API endpoint for external integrations to get recommendations"""
    try:
        data = request.get_json()
        recommendation_type = data.get('type', 'general')
        city_id = data.get('city_id')
        
        if not city_id:
            return jsonify({'error': 'City ID is required'}), 400
        
        rider_service = RiderExternalService(organization)
        rider_data = rider_service.get_live_riders(city_id)
        
        ai_service = AIService()
        result = ai_service.generate_recommendations(
            rider_data,
            recommendation_type=recommendation_type
        )
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/api/nl-to-sql', methods=['POST'])
@api_key_required
def api_natural_language_to_sql(organization):
    """API endpoint for external integrations to convert NL to SQL"""
    try:
        data = request.get_json()
        natural_query = data.get('query')
        
        if not natural_query:
            return jsonify({'error': 'Query is required'}), 400
        
        ai_service = AIService()
        result = ai_service.generate_sql_from_nl(natural_query, organization.id)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

