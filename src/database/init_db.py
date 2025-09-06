import os
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash

from src.models.user import db, User
from src.models.organization import Organization, APIConfiguration
from src.models.support import Alert

def init_db(app):
    with app.app_context():
        db.create_all()

        # Check if demo organization already exists
        if not Organization.query.filter_by(id='demo_org_001').first():
            print('Initializing demo data...')

            # Create demo organization
            demo_org = Organization(
                id='demo_org_001',
                name='Demo Organization',
                subscription_tier='professional',
                api_quota_limit=10000
            )
            db.session.add(demo_org)

            # Create demo user
            demo_user = User(
                id='demo_user_001',
                email='demo@loginexia.com',
                password_hash=generate_password_hash('demo123'),
                first_name='Demo',
                last_name='User',
                role='admin',
                organization_id='demo_org_001'
            )
            db.session.add(demo_user)

            # Create demo API configurations
            api_config_dh = APIConfiguration(
                id=str(uuid.uuid4()),
                organization_id='demo_org_001',
                api_type='delivery_hero',
                credentials={'base_url': 'https://api.deliveryhero.com'},
                is_active=True
            )
            db.session.add(api_config_dh)

            api_config_openai = APIConfiguration(
                id=str(uuid.uuid4()),
                organization_id='demo_org_001',
                api_type="openai",
                credentials={"base_url": "https://api.openai.com/v1"},
                is_active=True
            )
            db.session.add(api_config_openai)

            # Create demo WhatsApp configuration
            api_config_whatsapp = APIConfiguration(
                id=str(uuid.uuid4()),
                organization_id='demo_org_001',
                api_type='whatsapp',
                credentials={
                    'access_token': 'demo_whatsapp_token_replace_with_real',
                    'phone_number_id': 'demo_phone_number_id_replace_with_real'
                },
                is_active=False  # Disabled by default for demo
            )
            db.session.add(api_config_whatsapp)

            # Create demo alerts with WhatsApp phone numbers
            alert1 = Alert(
                id=str(uuid.uuid4()),
                organization_id='demo_org_001',
                alert_type='cash_threshold',
                severity='critical',
                title='High Cash Amount Alert',
                description='Rider Carlos Rodriguez has cash amount ≥ €120',
                data={
                    'rider_id': 'rider_001', 
                    'cash_amount': 125.50,
                    'rider_phone': '+34612345678',
                    'rider_info': {
                        'name': 'Carlos Rodriguez',
                        'phone': '+34612345678'
                    }
                }
            )
            db.session.add(alert1)

            alert2 = Alert(
                id=str(uuid.uuid4()),
                organization_id='demo_org_001',
                alert_type='battery_low',
                severity='high',
                title='Low Battery Alert',
                description='Rider Ana Lopez has low battery: 15%',
                data={
                    'rider_id': 'rider_004', 
                    'battery_level': 15,
                    'rider_phone': '+34687654321',
                    'rider_info': {
                        'name': 'Ana Lopez',
                        'phone': '+34687654321'
                    }
                }
            )
            db.session.add(alert2)

            # Create additional demo alert for off-zone
            alert3 = Alert(
                id=str(uuid.uuid4()),
                organization_id='demo_org_001',
                alert_type='off_zone',
                severity='medium',
                title='Rider Outside Zone',
                description='Rider Miguel Santos is outside assigned delivery zone',
                data={
                    'rider_id': 'rider_007',
                    'current_location': {'lat': 40.4168, 'lng': -3.7038},
                    'assigned_zone': 'Zone Centro',
                    'rider_phone': '+34655443322',
                    'rider_info': {
                        'name': 'Miguel Santos',
                        'phone': '+34655443322'
                    }
                }
            )
            db.session.add(alert3)

            db.session.commit()
            print('Demo data initialized.')
        else:
            print('Demo data already exists, skipping initialization.')

if __name__ == '__main__':
    from src.main import app
    init_db(app)


