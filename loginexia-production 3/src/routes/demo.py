from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import random

demo_bp = Blueprint('demo', __name__)

# Demo data for testing without external APIs
DEMO_RIDERS = [
    {
        "id": "rider_001",
        "name": "Carlos Rodriguez",
        "email": "carlos@example.com",
        "phone": "+34612345678",
        "status": "WORKING",
        "cash_amount": 85.50,
        "battery_level": 78,
        "vehicle_type": "motorcycle",
        "city_id": "madrid",
        "location": {"lat": 40.4168, "lng": -3.7038}
    },
    {
        "id": "rider_002", 
        "name": "Maria Garcia",
        "email": "maria@example.com",
        "phone": "+34612345679",
        "status": "AVAILABLE",
        "cash_amount": 125.75,
        "battery_level": 45,
        "vehicle_type": "bicycle",
        "city_id": "madrid",
        "location": {"lat": 40.4200, "lng": -3.7100}
    },
    {
        "id": "rider_003",
        "name": "Juan Martinez",
        "email": "juan@example.com", 
        "phone": "+34612345680",
        "status": "BREAK",
        "cash_amount": 67.25,
        "battery_level": 92,
        "vehicle_type": "motorcycle",
        "city_id": "madrid",
        "location": {"lat": 40.4150, "lng": -3.7000}
    },
    {
        "id": "rider_004",
        "name": "Ana Lopez",
        "email": "ana@example.com",
        "phone": "+34612345681", 
        "status": "LATE",
        "cash_amount": 45.00,
        "battery_level": 15,
        "vehicle_type": "bicycle",
        "city_id": "madrid",
        "location": {"lat": 40.4180, "lng": -3.7080},
        "late_duration_minutes": 35
    },
    {
        "id": "rider_005",
        "name": "Pedro Sanchez",
        "email": "pedro@example.com",
        "phone": "+34612345682",
        "status": "WORKING", 
        "cash_amount": 156.80,
        "battery_level": 88,
        "vehicle_type": "motorcycle",
        "city_id": "madrid",
        "location": {"lat": 40.4220, "lng": -3.6950}
    }
]

DEMO_COMPANIES = [
    {
        "id": "company_001",
        "name": "FastDelivery Madrid",
        "city_id": "madrid",
        "active_riders_count": 3,
        "total_deliveries_today": 127,
        "performance_score": 8.5
    },
    {
        "id": "company_002", 
        "name": "QuickRiders SL",
        "city_id": "madrid",
        "active_riders_count": 2,
        "total_deliveries_today": 89,
        "performance_score": 7.8
    }
]

@demo_bp.route('/riders/live/<city_id>', methods=['GET'])
def get_demo_live_riders(city_id):
    """Demo endpoint for live riders data"""
    city_riders = [r for r in DEMO_RIDERS if r['city_id'] == city_id]
    
    # Add some randomization to make it feel live
    for rider in city_riders:
        rider['last_update'] = datetime.utcnow().isoformat()
        # Slightly randomize battery and cash
        rider['battery_level'] = max(5, min(100, rider['battery_level'] + random.randint(-5, 5)))
        rider['cash_amount'] = max(0, rider['cash_amount'] + random.uniform(-10, 10))
    
    return jsonify({
        "riders": city_riders,
        "total_count": len(city_riders),
        "timestamp": datetime.utcnow().isoformat()
    })

@demo_bp.route('/riders/analytics/kpis/<city_id>', methods=['GET'])
def get_demo_kpis(city_id):
    """Demo endpoint for KPIs"""
    city_riders = [r for r in DEMO_RIDERS if r['city_id'] == city_id]
    
    kpis = {
        'total_riders': len(city_riders),
        'active_riders': len([r for r in city_riders if r['status'] == 'WORKING']),
        'available_riders': len([r for r in city_riders if r['status'] == 'AVAILABLE']),
        'riders_on_break': len([r for r in city_riders if r['status'] == 'BREAK']),
        'companies_count': len(DEMO_COMPANIES),
        'timestamp': datetime.utcnow().isoformat()
    }
    
    return jsonify(kpis)

@demo_bp.route('/riders/analytics/alerts/<city_id>', methods=['GET'])
def get_demo_alerts(city_id):
    """Demo endpoint for alerts"""
    alerts = []
    city_riders = [r for r in DEMO_RIDERS if r['city_id'] == city_id]
    
    for rider in city_riders:
        # Cash threshold alert
        if rider['cash_amount'] >= 120:
            alerts.append({
                'type': 'cash_threshold',
                'rider_id': rider['id'],
                'severity': 'high',
                'message': f"Rider {rider['name']} has cash amount ≥ €120 ({rider['cash_amount']:.2f}€)",
                'data': {'cash_amount': rider['cash_amount']}
            })
        
        # Battery low alert
        if rider['battery_level'] < 20:
            alerts.append({
                'type': 'battery_low',
                'rider_id': rider['id'],
                'severity': 'medium',
                'message': f"Rider {rider['name']} has low battery: {rider['battery_level']}%",
                'data': {'battery_level': rider['battery_level']}
            })
        
        # No-show alert
        if rider['status'] == 'LATE' and rider.get('late_duration_minutes', 0) > 30:
            alerts.append({
                'type': 'no_show',
                'rider_id': rider['id'],
                'severity': 'medium',
                'message': f"Rider {rider['name']} is late for {rider.get('late_duration_minutes')} minutes",
                'data': {'late_duration': rider.get('late_duration_minutes')}
            })
    
    return jsonify({'alerts': alerts})

@demo_bp.route('/ai/recommendations', methods=['POST'])
def get_demo_recommendations():
    """Demo endpoint for AI recommendations"""
    data = request.get_json()
    recommendation_type = data.get('type', 'general')
    
    recommendations_by_type = {
        'general': [
            {
                'title': 'Optimize Peak Hour Coverage',
                'description': 'Consider adding 2 more riders during lunch hours (12-14h) to reduce delivery times. Current average wait time is 18 minutes.',
                'priority': 'high',
                'category': 'operational'
            },
            {
                'title': 'Battery Management Alert',
                'description': 'Set up automatic notifications when rider battery drops below 25% to prevent service interruptions.',
                'priority': 'medium',
                'category': 'maintenance'
            },
            {
                'title': 'Cash Collection Schedule',
                'description': 'Implement daily cash collection for riders exceeding €100 to reduce security risks and improve cash flow.',
                'priority': 'high',
                'category': 'financial'
            }
        ],
        'performance': [
            {
                'title': 'Rider Training Program',
                'description': 'Provide navigation training for riders with delivery times above average. Focus on route optimization.',
                'priority': 'medium',
                'category': 'training'
            },
            {
                'title': 'Incentive Program',
                'description': 'Implement performance bonuses for riders maintaining >95% on-time delivery rate.',
                'priority': 'low',
                'category': 'motivation'
            }
        ],
        'scheduling': [
            {
                'title': 'Shift Pattern Optimization',
                'description': 'Adjust shift patterns based on demand forecasting. Peak demand occurs at 13:00-14:00 and 20:00-21:30.',
                'priority': 'high',
                'category': 'scheduling'
            },
            {
                'title': 'Weekend Coverage',
                'description': 'Increase weekend staffing by 30% to handle higher order volumes.',
                'priority': 'medium',
                'category': 'scheduling'
            }
        ]
    }
    
    recommendations = recommendations_by_type.get(recommendation_type, recommendations_by_type['general'])
    
    return jsonify({
        'recommendations': recommendations,
        'type': recommendation_type,
        'confidence': 'high',
        'generated_at': datetime.utcnow().isoformat()
    })

@demo_bp.route('/ai/nl-to-sql', methods=['POST'])
def demo_nl_to_sql():
    """Demo endpoint for NL to SQL conversion"""
    data = request.get_json()
    natural_query = data.get('query', '')
    
    # Simple mapping of common queries to SQL
    query_mappings = {
        'show all riders': 'SELECT * FROM riders WHERE organization_id = \'demo_org\';',
        'count active riders': 'SELECT COUNT(*) FROM riders WHERE status = \'WORKING\' AND organization_id = \'demo_org\';',
        'riders with low battery': 'SELECT * FROM riders WHERE battery_level < 20 AND organization_id = \'demo_org\';',
        'riders with high cash': 'SELECT * FROM riders WHERE cash_amount >= 120 AND organization_id = \'demo_org\';',
        'average delivery time': 'SELECT AVG(delivery_time_minutes) FROM deliveries WHERE organization_id = \'demo_org\' AND DATE(created_at) = CURRENT_DATE;'
    }
    
    # Find best match
    sql_query = None
    for key, sql in query_mappings.items():
        if key.lower() in natural_query.lower():
            sql_query = sql
            break
    
    if not sql_query:
        sql_query = f"-- Could not parse query: {natural_query}\n-- Please try: 'show all riders', 'count active riders', 'riders with low battery', etc."
    
    return jsonify({
        'sql_query': sql_query,
        'natural_query': natural_query,
        'confidence': 'high' if sql_query and not sql_query.startswith('--') else 'low',
        'generated_at': datetime.utcnow().isoformat()
    })

@demo_bp.route('/ai/query-knowledge', methods=['POST'])
def demo_query_knowledge():
    """Demo endpoint for knowledge base queries"""
    data = request.get_json()
    question = data.get('question', '')
    
    # Simple knowledge base responses
    knowledge_responses = {
        'rider states': 'Rider states in Loginexia include: WORKING (actively delivering), AVAILABLE (ready for orders), BREAK (on break), LATE (late for shift), NOT_WORKING (off duty), READY (ready to start), STARTING (about to start), TEMP_NOT_WORKING (temporarily offline).',
        'alerts': 'Loginexia monitors several alert types: Cash threshold (≥€120), Battery low (<20%), No-show (late >30min), Off-zone (outside area). Alerts are categorized by severity: critical, high, medium, low.',
        'kpis': 'Key performance indicators include: Total riders, Active riders, Available riders, Riders on break, Average delivery time, Customer satisfaction, Order completion rate.',
        'api': 'Loginexia integrates with Delivery Hero APIs for rider management and provides AI-powered insights. The platform supports real-time monitoring, automated alerts, and predictive analytics.'
    }
    
    # Find best match
    answer = "I can help you with information about rider states, alerts, KPIs, and API integrations. Please ask specific questions about these topics."
    
    for key, response in knowledge_responses.items():
        if key in question.lower():
            answer = response
            break
    
    return jsonify({
        'answer': answer,
        'question': question,
        'confidence': 'high',
        'generated_at': datetime.utcnow().isoformat()
    })

@demo_bp.route('/companies/<city_id>', methods=['GET'])
def get_demo_companies(city_id):
    """Demo endpoint for companies data"""
    city_companies = [c for c in DEMO_COMPANIES if c['city_id'] == city_id]
    
    return jsonify({
        'companies': city_companies,
        'total_count': len(city_companies),
        'timestamp': datetime.utcnow().isoformat()
    })

@demo_bp.route('/master-data/contracts', methods=['GET'])
def get_demo_contracts():
    """Demo endpoint for contracts"""
    return jsonify({
        'contracts': [
            {'id': 'contract_001', 'name': 'Standard Delivery Contract', 'type': 'full_time'},
            {'id': 'contract_002', 'name': 'Part-time Evening Contract', 'type': 'part_time'},
            {'id': 'contract_003', 'name': 'Weekend Only Contract', 'type': 'weekend'}
        ]
    })

@demo_bp.route('/master-data/vehicle-types', methods=['GET'])
def get_demo_vehicle_types():
    """Demo endpoint for vehicle types"""
    return jsonify({
        'vehicle_types': [
            {'id': 'motorcycle', 'name': 'Motorcycle', 'capacity': 'large'},
            {'id': 'bicycle', 'name': 'Bicycle', 'capacity': 'small'},
            {'id': 'car', 'name': 'Car', 'capacity': 'extra_large'},
            {'id': 'scooter', 'name': 'Electric Scooter', 'capacity': 'medium'}
        ]
    })

@demo_bp.route('/master-data/cities', methods=['GET'])
def get_demo_cities():
    """Demo endpoint for cities"""
    return jsonify({
        'cities': [
            {'id': 'madrid', 'name': 'Madrid', 'country': 'Spain'},
            {'id': 'barcelona', 'name': 'Barcelona', 'country': 'Spain'},
            {'id': 'valencia', 'name': 'Valencia', 'country': 'Spain'}
        ]
    })

@demo_bp.route('/auth/demo-login', methods=['POST'])
def demo_login():
    """Demo login endpoint that doesn't require external authentication"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    # Demo credentials
    if email == 'demo@loginexia.com' and password == 'demo123':
        # Generate demo tokens (in real app, these would be proper JWTs)
        demo_user = {
            'id': 'demo_user_001',
            'email': 'demo@loginexia.com',
            'first_name': 'Demo',
            'last_name': 'User',
            'role': 'admin',
            'organization_id': 'demo_org_001',
            'is_active': True,
            'created_at': datetime.utcnow().isoformat(),
            'last_login': datetime.utcnow().isoformat()
        }
        
        demo_organization = {
            'id': 'demo_org_001',
            'name': 'Demo Organization',
            'subscription_tier': 'professional',
            'api_quota_limit': 10000,
            'is_active': True,
            'created_at': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'user': demo_user,
            'organization': demo_organization,
            'access_token': 'demo_access_token_12345',
            'refresh_token': 'demo_refresh_token_67890',
            'expires_in': 3600,
            'token_type': 'Bearer'
        }), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

