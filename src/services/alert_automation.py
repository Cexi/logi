import logging
from datetime import datetime
from typing import Dict, List, Optional
from src.models.user import db
from src.models.support import Alert
from src.models.organization import APIConfiguration
from src.services.whatsapp_service import WhatsAppService

logger = logging.getLogger(__name__)

class AlertAutomationService:
    """
    Servicio para automatizar el envío de alertas críticas por WhatsApp
    """
    
    @staticmethod
    def process_new_alert(alert: Alert) -> bool:
        """
        Procesa una nueva alerta y envía notificación por WhatsApp si es crítica
        
        Args:
            alert: Objeto Alert recién creado
            
        Returns:
            bool: True si se procesó correctamente
        """
        try:
            # Solo procesar alertas críticas o de alta severidad
            if alert.severity not in ['critical', 'high']:
                logger.info(f"Alert {alert.id} is not critical/high, skipping WhatsApp notification")
                return True
            
            # Verificar si ya se envió por WhatsApp
            if alert.whatsapp_sent:
                logger.info(f"Alert {alert.id} already sent via WhatsApp")
                return True
            
            # Obtener configuración de WhatsApp de la organización
            whatsapp_config = APIConfiguration.query.filter_by(
                organization_id=alert.organization_id,
                api_type='whatsapp',
                is_active=True
            ).first()
            
            if not whatsapp_config:
                logger.warning(f"No WhatsApp configuration found for organization {alert.organization_id}")
                return False
            
            # Obtener número de teléfono del repartidor
            rider_phone = AlertAutomationService._get_rider_phone(alert)
            
            if not rider_phone:
                logger.warning(f"No phone number found for rider in alert {alert.id}")
                return False
            
            # Inicializar servicio de WhatsApp
            whatsapp_service = WhatsAppService(
                access_token=whatsapp_config.credentials.get('access_token'),
                phone_number_id=whatsapp_config.credentials.get('phone_number_id')
            )
            
            # Enviar mensaje
            success = whatsapp_service.send_alert_message(rider_phone, alert.to_dict())
            
            if success:
                # Actualizar la alerta
                alert.whatsapp_sent = True
                alert.whatsapp_sent_at = datetime.utcnow()
                alert.whatsapp_status = 'sent'
                alert.rider_phone = rider_phone
                db.session.commit()
                
                logger.info(f"WhatsApp alert sent successfully for alert {alert.id}")
                return True
            else:
                alert.whatsapp_status = 'failed'
                db.session.commit()
                logger.error(f"Failed to send WhatsApp alert for alert {alert.id}")
                return False
                
        except Exception as e:
            logger.error(f"Error processing alert {alert.id}: {str(e)}")
            return False
    
    @staticmethod
    def _get_rider_phone(alert: Alert) -> Optional[str]:
        """
        Extrae el número de teléfono del repartidor desde los datos de la alerta
        
        Args:
            alert: Objeto Alert
            
        Returns:
            str: Número de teléfono o None si no se encuentra
        """
        try:
            # Buscar en los datos de la alerta
            if alert.data:
                # Buscar directamente el teléfono
                if 'rider_phone' in alert.data:
                    return alert.data['rider_phone']
                
                # Buscar en información del repartidor
                if 'rider_info' in alert.data and 'phone' in alert.data['rider_info']:
                    return alert.data['rider_info']['phone']
                
                # Buscar en contacto del repartidor
                if 'contact' in alert.data and 'phone' in alert.data['contact']:
                    return alert.data['contact']['phone']
            
            # Si no se encuentra en los datos, intentar obtener desde la API de riders
            if alert.rider_id:
                # Aquí se podría hacer una llamada a la API de Delivery Hero
                # para obtener la información del repartidor
                pass
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting rider phone from alert {alert.id}: {str(e)}")
            return None
    
    @staticmethod
    def process_pending_alerts(organization_id: str) -> Dict[str, int]:
        """
        Procesa todas las alertas críticas pendientes de una organización
        
        Args:
            organization_id: ID de la organización
            
        Returns:
            Dict con estadísticas del procesamiento
        """
        try:
            # Obtener alertas críticas no enviadas
            pending_alerts = Alert.query.filter_by(
                organization_id=organization_id,
                whatsapp_sent=False,
                status='active'
            ).filter(Alert.severity.in_(['critical', 'high'])).all()
            
            stats = {
                'total_alerts': len(pending_alerts),
                'sent_successfully': 0,
                'failed_to_send': 0,
                'no_phone_number': 0
            }
            
            for alert in pending_alerts:
                success = AlertAutomationService.process_new_alert(alert)
                
                if success and alert.whatsapp_sent:
                    stats['sent_successfully'] += 1
                elif not AlertAutomationService._get_rider_phone(alert):
                    stats['no_phone_number'] += 1
                else:
                    stats['failed_to_send'] += 1
            
            logger.info(f"Processed {stats['total_alerts']} pending alerts for organization {organization_id}")
            return stats
            
        except Exception as e:
            logger.error(f"Error processing pending alerts for organization {organization_id}: {str(e)}")
            return {'error': str(e)}
    
    @staticmethod
    def create_alert_with_whatsapp(organization_id: str, alert_data: Dict, rider_phone: str = None) -> Alert:
        """
        Crea una nueva alerta y automáticamente envía notificación por WhatsApp si es crítica
        
        Args:
            organization_id: ID de la organización
            alert_data: Datos de la alerta
            rider_phone: Número de teléfono del repartidor (opcional)
            
        Returns:
            Alert: Objeto Alert creado
        """
        try:
            import uuid
            
            # Agregar teléfono a los datos si se proporciona
            if rider_phone and 'data' in alert_data:
                if alert_data['data'] is None:
                    alert_data['data'] = {}
                alert_data['data']['rider_phone'] = rider_phone
            
            # Crear la alerta
            alert = Alert(
                id=str(uuid.uuid4()),
                organization_id=organization_id,
                **{k: v for k, v in alert_data.items() if k != 'id'}
            )
            
            db.session.add(alert)
            db.session.commit()
            
            # Procesar automáticamente para WhatsApp
            AlertAutomationService.process_new_alert(alert)
            
            logger.info(f"Created alert {alert.id} with automatic WhatsApp processing")
            return alert
            
        except Exception as e:
            logger.error(f"Error creating alert with WhatsApp: {str(e)}")
            db.session.rollback()
            raise

# Función helper para usar en otros servicios
def auto_send_critical_alert(alert: Alert) -> bool:
    """
    Función helper para enviar automáticamente alertas críticas
    
    Args:
        alert: Objeto Alert
        
    Returns:
        bool: True si se procesó correctamente
    """
    return AlertAutomationService.process_new_alert(alert)

