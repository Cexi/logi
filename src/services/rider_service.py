import requests
import json
from datetime import datetime, timedelta
from flask import current_app
from src.models.organization import APIConfiguration
from src.services.encryption_service import EncryptionService

class RiderExternalService:
    def __init__(self, organization):
        self.organization = organization
        self.base_url = "https://api.deliveryhero.com"  # Replace with actual base URL
        self.credentials = self._get_credentials()
        self.session = requests.Session()
        
    def _get_credentials(self):
        """Get decrypted credentials for the organization"""
        config = APIConfiguration.query.filter_by(
            organization_id=self.organization.id,
            api_type='rider_external',
            is_active=True
        ).first()
        
        if not config:
            raise ValueError("No RiderExternal API configuration found for organization")
        
        encryption_service = EncryptionService()
        return encryption_service.decrypt_credentials(config.credentials)
    
    def _get_auth_token(self):
        """Get authentication token using STS"""
        # Implementation for Security Token Service authentication
        # This would use the JWT generation process described in the PDF
        auth_url = f"{self.base_url}/auth/token"
        
        # Generate JWT using private key and client credentials
        jwt_token = self._generate_jwt()
        
        response = self.session.post(auth_url, json={
            'grant_type': 'client_credentials',
            'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
            'client_assertion': jwt_token
        })
        
        if response.status_code == 200:
            return response.json()['access_token']
        else:
            raise Exception(f"Failed to get auth token: {response.text}")
    
    def _generate_jwt(self):
        """Generate JWT for STS authentication"""
        # This would implement the JWT generation using the organization's private key
        # For now, returning a placeholder
        return "placeholder_jwt_token"
    
    def _make_request(self, method, endpoint, **kwargs):
        """Make authenticated request to RiderExternal API"""
        token = self._get_auth_token()
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'Bearer {token}'
        headers['Content-Type'] = 'application/json'
        kwargs['headers'] = headers
        
        url = f"{self.base_url}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            raise Exception(f"API request failed: {response.status_code} - {response.text}")
    
    # Rider Management APIs
    def get_contracts(self):
        """Get available contracts"""
        return self._make_request('GET', '/v3/external/contracts')
    
    def get_vehicle_types(self):
        """Get available vehicle types"""
        return self._make_request('GET', '/v3/external/vehicle-types')
    
    def get_starting_points(self):
        """Get available starting points"""
        return self._make_request('GET', '/v3/external/starting-points')
    
    def get_cities(self):
        """Get available cities"""
        return self._make_request('GET', '/v3/external/cities')
    
    def create_rider(self, rider_data):
        """Create a new rider"""
        return self._make_request('POST', '/v3/external/employees', json=rider_data)
    
    def get_rider(self, employee_id):
        """Get rider details"""
        return self._make_request('GET', f'/v3/external/employees/{employee_id}')
    
    def update_rider(self, employee_id, rider_data):
        """Update rider information"""
        return self._make_request('PUT', f'/v3/external/employees/{employee_id}', json=rider_data)
    
    def get_riders(self, filters=None):
        """Get list of riders with optional filters"""
        params = filters or {}
        return self._make_request('GET', '/v3/external/employees', params=params)
    
    def assign_vehicle(self, employee_id, vehicle_data):
        """Assign vehicle to rider"""
        return self._make_request('POST', f'/v3/external/employees/{employee_id}/vehicles', json=vehicle_data)
    
    def assign_starting_points(self, employee_id, starting_points_data):
        """Assign starting points to rider"""
        return self._make_request('POST', f'/v3/external/employees/{employee_id}/starting-points', json=starting_points_data)
    
    def assign_contract(self, employee_id, contract_data):
        """Assign contract to rider"""
        return self._make_request('POST', f'/v3/external/employees/{employee_id}/contracts', json=contract_data)
    
    # Live Data APIs
    def get_live_riders(self, city_id, filters=None):
        """Get live riders overview for a city"""
        params = filters or {}
        return self._make_request('GET', f'/v1/external/city/{city_id}/riders', params=params)
    
    def get_live_rider_details(self, city_id, rider_id):
        """Get detailed live data for a specific rider"""
        return self._make_request('GET', f'/v1/external/city/{city_id}/rider/{rider_id}')
    
    def get_company_data(self, city_id, company_id):
        """Get detailed company data"""
        return self._make_request('GET', f'/v1/external/city/{city_id}/company/{company_id}')
    
    def get_companies_overview(self, city_id):
        """Get companies overview for a city"""
        return self._make_request('GET', f'/v1/external/city/{city_id}/companies')

class RiderAnalyticsService:
    """Service for analyzing rider data and generating insights"""
    
    def __init__(self, rider_service):
        self.rider_service = rider_service
    
    def calculate_kpis(self, city_id, date_range=None):
        """Calculate key performance indicators"""
        # Get live data
        riders_data = self.rider_service.get_live_riders(city_id)
        companies_data = self.rider_service.get_companies_overview(city_id)
        
        # Calculate KPIs
        kpis = {
            'total_riders': len(riders_data.get('riders', [])),
            'active_riders': len([r for r in riders_data.get('riders', []) if r.get('status') == 'WORKING']),
            'available_riders': len([r for r in riders_data.get('riders', []) if r.get('status') == 'AVAILABLE']),
            'riders_on_break': len([r for r in riders_data.get('riders', []) if r.get('status') == 'BREAK']),
            'companies_count': len(companies_data.get('companies', [])),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return kpis
    
    def detect_alerts(self, city_id):
        """Detect alerts based on rider data"""
        alerts = []
        riders_data = self.rider_service.get_live_riders(city_id)
        
        for rider in riders_data.get('riders', []):
            # Cash threshold alert
            if rider.get('cash_amount', 0) >= 120:
                alerts.append({
                    'type': 'cash_threshold',
                    'rider_id': rider.get('id'),
                    'severity': 'high',
                    'message': f"Rider {rider.get('name')} has cash amount ≥ €120",
                    'data': {'cash_amount': rider.get('cash_amount')}
                })
            
            # No-show alert
            if rider.get('status') == 'LATE' and rider.get('late_duration_minutes', 0) > 30:
                alerts.append({
                    'type': 'no_show',
                    'rider_id': rider.get('id'),
                    'severity': 'medium',
                    'message': f"Rider {rider.get('name')} is late for {rider.get('late_duration_minutes')} minutes",
                    'data': {'late_duration': rider.get('late_duration_minutes')}
                })
            
            # Battery low alert
            if rider.get('battery_level', 100) < 20:
                alerts.append({
                    'type': 'battery_low',
                    'rider_id': rider.get('id'),
                    'severity': 'medium',
                    'message': f"Rider {rider.get('name')} has low battery: {rider.get('battery_level')}%",
                    'data': {'battery_level': rider.get('battery_level')}
                })
        
        return alerts
    
    def generate_performance_report(self, city_id, date_range=None):
        """Generate comprehensive performance report"""
        kpis = self.calculate_kpis(city_id, date_range)
        alerts = self.detect_alerts(city_id)
        
        report = {
            'kpis': kpis,
            'alerts': alerts,
            'summary': {
                'total_alerts': len(alerts),
                'critical_alerts': len([a for a in alerts if a.get('severity') == 'critical']),
                'high_alerts': len([a for a in alerts if a.get('severity') == 'high']),
                'medium_alerts': len([a for a in alerts if a.get('severity') == 'medium']),
                'rider_utilization': (kpis['active_riders'] / max(kpis['total_riders'], 1)) * 100
            },
            'generated_at': datetime.utcnow().isoformat()
        }
        
        return report

