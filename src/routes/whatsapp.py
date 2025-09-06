from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
from src.models.user import db
from src.models.support import Alert
from src.models.organization import APIConfiguration
from src.services.whatsapp_service import WhatsAppService
from src.services.auth_service import token_required

logger = logging.getLogger(__name__)

whatsapp_bp = Blueprint('whatsapp', __name__)

@whatsapp_bp.route('/send-alert', methods=['POST'])
@token_required
def send_whatsapp_alert(current_user):
    """
    Envía una alerta por WhatsApp a un repartidor específico
    """
    try:
        data = request.get_json()
        alert_id = data.get('alert_id')
        rider_phone = data.get('rider_phone')
        
        if not alert_id or not rider_phone:
            return jsonify({'error': 'alert_id and rider_phone are required'}), 400
        
        # Obtener la alerta
        alert = Alert.query.filter_by(
            id=alert_id,
            organization_id=current_user.organization_id
        ).first()
        
        if not alert:
            return jsonify({'error': 'Alert not found'}), 404
        
        # Obtener configuración de WhatsApp de la organización
        whatsapp_config = APIConfiguration.query.filter_by(
            organization_id=current_user.organization_id,
            api_type='whatsapp',
            is_active=True
        ).first()
        
        if not whatsapp_config:
            return jsonify({'error': 'WhatsApp configuration not found'}), 404
        
        # Inicializar servicio de WhatsApp
        whatsapp_service = WhatsAppService(
            access_token=whatsapp_config.credentials.get('access_token'),
            phone_number_id=whatsapp_config.credentials.get('phone_number_id')
        )
        
        # Enviar mensaje
        success = whatsapp_service.send_alert_message(rider_phone, alert.to_dict())
        
        if success:
            # Actualizar la alerta con información de WhatsApp
            alert.whatsapp_sent = True
            alert.whatsapp_sent_at = datetime.utcnow()
            alert.whatsapp_status = 'sent'
            alert.rider_phone = rider_phone
            db.session.commit()
            
            return jsonify({
                'message': 'WhatsApp alert sent successfully',
                'alert_id': alert_id,
                'rider_phone': rider_phone
            }), 200
        else:
            return jsonify({'error': 'Failed to send WhatsApp alert'}), 500
            
    except Exception as e:
        logger.error(f"Error sending WhatsApp alert: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@whatsapp_bp.route('/send-bulk-alert', methods=['POST'])
@token_required
def send_bulk_whatsapp_alert(current_user):
    """
    Envía una alerta por WhatsApp a múltiples repartidores
    """
    try:
        data = request.get_json()
        alert_id = data.get('alert_id')
        rider_phones = data.get('rider_phones', [])
        
        if not alert_id or not rider_phones:
            return jsonify({'error': 'alert_id and rider_phones are required'}), 400
        
        # Obtener la alerta
        alert = Alert.query.filter_by(
            id=alert_id,
            organization_id=current_user.organization_id
        ).first()
        
        if not alert:
            return jsonify({'error': 'Alert not found'}), 404
        
        # Obtener configuración de WhatsApp
        whatsapp_config = APIConfiguration.query.filter_by(
            organization_id=current_user.organization_id,
            api_type='whatsapp',
            is_active=True
        ).first()
        
        if not whatsapp_config:
            return jsonify({'error': 'WhatsApp configuration not found'}), 404
        
        # Inicializar servicio de WhatsApp
        whatsapp_service = WhatsAppService(
            access_token=whatsapp_config.credentials.get('access_token'),
            phone_number_id=whatsapp_config.credentials.get('phone_number_id')
        )
        
        # Enviar mensajes en lote
        results = whatsapp_service.send_bulk_alerts(rider_phones, alert.to_dict())
        
        # Contar éxitos y fallos
        successful_sends = sum(1 for success in results.values() if success)
        failed_sends = len(rider_phones) - successful_sends
        
        return jsonify({
            'message': f'Bulk WhatsApp alerts processed',
            'successful_sends': successful_sends,
            'failed_sends': failed_sends,
            'results': results
        }), 200
        
    except Exception as e:
        logger.error(f"Error sending bulk WhatsApp alerts: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@whatsapp_bp.route('/auto-send-critical', methods=['POST'])
@token_required
def auto_send_critical_alerts(current_user):
    """
    Envía automáticamente alertas críticas por WhatsApp
    """
    try:
        # Obtener alertas críticas no enviadas por WhatsApp
        critical_alerts = Alert.query.filter_by(
            organization_id=current_user.organization_id,
            severity='critical',
            whatsapp_sent=False,
            status='active'
        ).all()
        
        if not critical_alerts:
            return jsonify({'message': 'No critical alerts to send'}), 200
        
        # Obtener configuración de WhatsApp
        whatsapp_config = APIConfiguration.query.filter_by(
            organization_id=current_user.organization_id,
            api_type='whatsapp',
            is_active=True
        ).first()
        
        if not whatsapp_config:
            return jsonify({'error': 'WhatsApp configuration not found'}), 404
        
        # Inicializar servicio de WhatsApp
        whatsapp_service = WhatsAppService(
            access_token=whatsapp_config.credentials.get('access_token'),
            phone_number_id=whatsapp_config.credentials.get('phone_number_id')
        )
        
        sent_count = 0
        failed_count = 0
        
        for alert in critical_alerts:
            # Obtener número de teléfono del repartidor desde los datos de la alerta
            rider_phone = alert.data.get('rider_phone') if alert.data else None
            
            if rider_phone:
                success = whatsapp_service.send_alert_message(rider_phone, alert.to_dict())
                
                if success:
                    alert.whatsapp_sent = True
                    alert.whatsapp_sent_at = datetime.utcnow()
                    alert.whatsapp_status = 'sent'
                    alert.rider_phone = rider_phone
                    sent_count += 1
                else:
                    alert.whatsapp_status = 'failed'
                    failed_count += 1
            else:
                logger.warning(f"No phone number found for alert {alert.id}")
                failed_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': 'Critical alerts processed',
            'sent_count': sent_count,
            'failed_count': failed_count,
            'total_alerts': len(critical_alerts)
        }), 200
        
    except Exception as e:
        logger.error(f"Error auto-sending critical alerts: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@whatsapp_bp.route('/config', methods=['GET', 'POST'])
@token_required
def whatsapp_config(current_user):
    """
    Gestiona la configuración de WhatsApp para la organización
    """
    if request.method == 'GET':
        # Obtener configuración actual
        config = APIConfiguration.query.filter_by(
            organization_id=current_user.organization_id,
            api_type='whatsapp'
        ).first()
        
        if config:
            return jsonify({
                'configured': True,
                'is_active': config.is_active,
                'phone_number_id': config.credentials.get('phone_number_id', ''),
                'created_at': config.created_at.isoformat() if config.created_at else None
            }), 200
        else:
            return jsonify({'configured': False}), 200
    
    elif request.method == 'POST':
        # Configurar WhatsApp
        data = request.get_json()
        access_token = data.get('access_token')
        phone_number_id = data.get('phone_number_id')
        
        if not access_token or not phone_number_id:
            return jsonify({'error': 'access_token and phone_number_id are required'}), 400
        
        # Buscar configuración existente
        config = APIConfiguration.query.filter_by(
            organization_id=current_user.organization_id,
            api_type='whatsapp'
        ).first()
        
        if config:
            # Actualizar configuración existente
            config.credentials = {
                'access_token': access_token,
                'phone_number_id': phone_number_id
            }
            config.is_active = True
        else:
            # Crear nueva configuración
            import uuid
            config = APIConfiguration(
                id=str(uuid.uuid4()),
                organization_id=current_user.organization_id,
                api_type='whatsapp',
                credentials={
                    'access_token': access_token,
                    'phone_number_id': phone_number_id
                },
                is_active=True
            )
            db.session.add(config)
        
        db.session.commit()
        
        return jsonify({'message': 'WhatsApp configuration saved successfully'}), 200

@whatsapp_bp.route('/test', methods=['POST'])
@token_required
def test_whatsapp(current_user):
    """
    Envía un mensaje de prueba por WhatsApp
    """
    try:
        data = request.get_json()
        test_phone = data.get('phone_number')
        
        if not test_phone:
            return jsonify({'error': 'phone_number is required'}), 400
        
        # Obtener configuración de WhatsApp
        whatsapp_config = APIConfiguration.query.filter_by(
            organization_id=current_user.organization_id,
            api_type='whatsapp',
            is_active=True
        ).first()
        
        if not whatsapp_config:
            return jsonify({'error': 'WhatsApp configuration not found'}), 404
        
        # Inicializar servicio de WhatsApp
        whatsapp_service = WhatsAppService(
            access_token=whatsapp_config.credentials.get('access_token'),
            phone_number_id=whatsapp_config.credentials.get('phone_number_id')
        )
        
        # Crear mensaje de prueba
        test_alert = {
            'alert_type': 'test',
            'severity': 'low',
            'title': 'Mensaje de Prueba',
            'description': 'Este es un mensaje de prueba de Loginexia. ¡La configuración de WhatsApp funciona correctamente!'
        }
        
        success = whatsapp_service.send_alert_message(test_phone, test_alert)
        
        if success:
            return jsonify({'message': 'Test message sent successfully'}), 200
        else:
            return jsonify({'error': 'Failed to send test message'}), 500
            
    except Exception as e:
        logger.error(f"Error sending test WhatsApp message: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

