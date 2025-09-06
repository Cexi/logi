from flask import Blueprint, request, jsonify
from src.services.auth_service import token_required, api_key_required
from src.services.rider_service import RiderExternalService, RiderAnalyticsService
from src.models.support import Alert
from src.models.user import db
from datetime import datetime

riders_bp = Blueprint('riders', __name__)

@riders_bp.route('/contracts', methods=['GET'])
@token_required
def get_contracts(current_user):
    """Get available contracts"""
    try:
        rider_service = RiderExternalService(current_user.organization)
        contracts = rider_service.get_contracts()
        return jsonify(contracts), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@riders_bp.route('/vehicle-types', methods=['GET'])
@token_required
def get_vehicle_types(current_user):
    """Get available vehicle types"""
    try:
        rider_service = RiderExternalService(current_user.organization)
        vehicle_types = rider_service.get_vehicle_types()
        return jsonify(vehicle_types), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@riders_bp.route('/starting-points', methods=['GET'])
@token_required
def get_starting_points(current_user):
    """Get available starting points"""
    try:
        rider_service = RiderExternalService(current_user.organization)
        starting_points = rider_service.get_starting_points()
        return jsonify(starting_points), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@riders_bp.route('/cities', methods=['GET'])
@token_required
def get_cities(current_user):
    """Get available cities"""
    try:
        rider_service = RiderExternalService(current_user.organization)
        cities = rider_service.get_cities()
        return jsonify(cities), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@riders_bp.route('/', methods=['POST'])
@token_required
def create_rider(current_user):
    """Create a new rider"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'contract_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        rider_service = RiderExternalService(current_user.organization)
        result = rider_service.create_rider(data)
        
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@riders_bp.route('/', methods=['GET'])
@token_required
def get_riders(current_user):
    """Get list of riders with optional filters"""
    try:
        # Get query parameters for filtering
        filters = {}
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('city_id'):
            filters['city_id'] = request.args.get('city_id')
        if request.args.get('limit'):
            filters['limit'] = int(request.args.get('limit'))
        if request.args.get('offset'):
            filters['offset'] = int(request.args.get('offset'))
        
        rider_service = RiderExternalService(current_user.organization)
        riders = rider_service.get_riders(filters)
        
        return jsonify(riders), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@riders_bp.route('/<employee_id>', methods=['GET'])
@token_required
def get_rider(current_user, employee_id):
    """Get rider details"""
    try:
        rider_service = RiderExternalService(current_user.organization)
        rider = rider_service.get_rider(employee_id)
        return jsonify(rider), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@riders_bp.route('/<employee_id>', methods=['PUT'])
@token_required
def update_rider(current_user, employee_id):
    """Update rider information"""
    try:
        data = request.get_json()
        rider_service = RiderExternalService(current_user.organization)
        result = rider_service.update_rider(employee_id, data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@riders_bp.route('/<employee_id>/vehicles', methods=['POST'])
@token_required
def assign_vehicle(current_user, employee_id):
    """Assign vehicle to rider"""
    try:
        data = request.get_json()
        rider_service = RiderExternalService(current_user.organization)
        result = rider_service.assign_vehicle(employee_id, data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@riders_bp.route('/<employee_id>/starting-points', methods=['POST'])
@token_required
def assign_starting_points(current_user, employee_id):
    """Assign starting points to rider"""
    try:
        data = request.get_json()
        rider_service = RiderExternalService(current_user.organization)
        result = rider_service.assign_starting_points(employee_id, data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@riders_bp.route('/<employee_id>/contracts', methods=['POST'])
@token_required
def assign_contract(current_user, employee_id):
    """Assign contract to rider"""
    try:
        data = request.get_json()
        rider_service = RiderExternalService(current_user.organization)
        result = rider_service.assign_contract(employee_id, data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@riders_bp.route('/live/<city_id>', methods=['GET'])
@token_required
def get_live_riders(current_user, city_id):
    """Get live riders overview for a city"""
    try:
        # Get query parameters for filtering
        filters = {}
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('limit'):
            filters['limit'] = int(request.args.get('limit'))
        if request.args.get('offset'):
            filters['offset'] = int(request.args.get('offset'))
        
        rider_service = RiderExternalService(current_user.organization)
        riders = rider_service.get_live_riders(city_id, filters)
        
        return jsonify(riders), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@riders_bp.route('/live/<city_id>/<rider_id>', methods=['GET'])
@token_required
def get_live_rider_details(current_user, city_id, rider_id):
    """Get detailed live data for a specific rider"""
    try:
        rider_service = RiderExternalService(current_user.organization)
        rider_details = rider_service.get_live_rider_details(city_id, rider_id)
        return jsonify(rider_details), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@riders_bp.route('/analytics/kpis/<city_id>', methods=['GET'])
@token_required
def get_kpis(current_user, city_id):
    """Get KPIs for a city"""
    try:
        rider_service = RiderExternalService(current_user.organization)
        analytics_service = RiderAnalyticsService(rider_service)
        
        # Get date range from query parameters
        date_range = None
        if request.args.get('start_date') and request.args.get('end_date'):
            date_range = {
                'start_date': request.args.get('start_date'),
                'end_date': request.args.get('end_date')
            }
        
        kpis = analytics_service.calculate_kpis(city_id, date_range)
        return jsonify(kpis), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@riders_bp.route('/analytics/alerts/<city_id>', methods=['GET'])
@token_required
def get_alerts(current_user, city_id):
    """Get alerts for a city"""
    try:
        rider_service = RiderExternalService(current_user.organization)
        analytics_service = RiderAnalyticsService(rider_service)
        
        alerts = analytics_service.detect_alerts(city_id)
        
        # Store alerts in database for tracking
        for alert_data in alerts:
            existing_alert = Alert.query.filter_by(
                organization_id=current_user.organization_id,
                rider_id=alert_data.get('rider_id'),
                alert_type=alert_data.get('type'),
                status='active'
            ).first()
            
            if not existing_alert:
                alert = Alert(
                    organization_id=current_user.organization_id,
                    alert_type=alert_data.get('type'),
                    rider_id=alert_data.get('rider_id'),
                    title=alert_data.get('message'),
                    description=alert_data.get('message'),
                    severity=alert_data.get('severity'),
                    data=alert_data.get('data')
                )
                db.session.add(alert)
        
        db.session.commit()
        
        return jsonify({'alerts': alerts}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@riders_bp.route('/analytics/report/<city_id>', methods=['GET'])
@token_required
def get_performance_report(current_user, city_id):
    """Get comprehensive performance report"""
    try:
        rider_service = RiderExternalService(current_user.organization)
        analytics_service = RiderAnalyticsService(rider_service)
        
        # Get date range from query parameters
        date_range = None
        if request.args.get('start_date') and request.args.get('end_date'):
            date_range = {
                'start_date': request.args.get('start_date'),
                'end_date': request.args.get('end_date')
            }
        
        report = analytics_service.generate_performance_report(city_id, date_range)
        return jsonify(report), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@riders_bp.route('/companies/<city_id>', methods=['GET'])
@token_required
def get_companies_overview(current_user, city_id):
    """Get companies overview for a city"""
    try:
        rider_service = RiderExternalService(current_user.organization)
        companies = rider_service.get_companies_overview(city_id)
        return jsonify(companies), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@riders_bp.route('/companies/<city_id>/<company_id>', methods=['GET'])
@token_required
def get_company_data(current_user, city_id, company_id):
    """Get detailed company data"""
    try:
        rider_service = RiderExternalService(current_user.organization)
        company_data = rider_service.get_company_data(city_id, company_id)
        return jsonify(company_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API Key endpoints (for external integrations)
@riders_bp.route('/api/live/<city_id>', methods=['GET'])
@api_key_required
def api_get_live_riders(organization, city_id):
    """API endpoint for external integrations to get live riders"""
    try:
        filters = {}
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('limit'):
            filters['limit'] = int(request.args.get('limit'))
        
        rider_service = RiderExternalService(organization)
        riders = rider_service.get_live_riders(city_id, filters)
        
        return jsonify(riders), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@riders_bp.route('/api/kpis/<city_id>', methods=['GET'])
@api_key_required
def api_get_kpis(organization, city_id):
    """API endpoint for external integrations to get KPIs"""
    try:
        rider_service = RiderExternalService(organization)
        analytics_service = RiderAnalyticsService(rider_service)
        
        kpis = analytics_service.calculate_kpis(city_id)
        return jsonify(kpis), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

