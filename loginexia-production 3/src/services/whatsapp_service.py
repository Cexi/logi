import requests
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class WhatsAppService:
    """
    Servicio para enviar notificaciones de WhatsApp a repartidores
    Utiliza WhatsApp Business API para alertas críticas
    """
    
    def __init__(self, access_token: str, phone_number_id: str, version: str = "v18.0"):
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.version = version
        self.base_url = f"https://graph.facebook.com/{version}/{phone_number_id}/messages"
        
    def send_alert_message(self, rider_phone: str, alert_data: Dict) -> bool:
        """
        Envía una alerta de WhatsApp a un repartidor
        
        Args:
            rider_phone: Número de teléfono del repartidor (formato internacional)
            alert_data: Datos de la alerta
            
        Returns:
            bool: True si el mensaje se envió correctamente
        """
        try:
            message_text = self._format_alert_message(alert_data)
            
            payload = {
                "messaging_product": "whatsapp",
                "to": rider_phone,
                "type": "text",
                "text": {
                    "body": message_text
                }
            }
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                data=json.dumps(payload)
            )
            
            if response.status_code == 200:
                logger.info(f"WhatsApp alert sent successfully to {rider_phone}")
                return True
            else:
                logger.error(f"Failed to send WhatsApp alert: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending WhatsApp alert: {str(e)}")
            return False
    
    def send_template_message(self, rider_phone: str, template_name: str, parameters: List[str]) -> bool:
        """
        Envía un mensaje usando una plantilla predefinida
        
        Args:
            rider_phone: Número de teléfono del repartidor
            template_name: Nombre de la plantilla aprobada
            parameters: Parámetros para la plantilla
            
        Returns:
            bool: True si el mensaje se envió correctamente
        """
        try:
            payload = {
                "messaging_product": "whatsapp",
                "to": rider_phone,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": "es"
                    },
                    "components": [
                        {
                            "type": "body",
                            "parameters": [{"type": "text", "text": param} for param in parameters]
                        }
                    ]
                }
            }
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                data=json.dumps(payload)
            )
            
            if response.status_code == 200:
                logger.info(f"WhatsApp template message sent to {rider_phone}")
                return True
            else:
                logger.error(f"Failed to send template message: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending template message: {str(e)}")
            return False
    
    def _format_alert_message(self, alert_data: Dict) -> str:
        """
        Formatea el mensaje de alerta para WhatsApp
        
        Args:
            alert_data: Datos de la alerta
            
        Returns:
            str: Mensaje formateado
        """
        alert_type = alert_data.get('alert_type', 'unknown')
        severity = alert_data.get('severity', 'medium')
        title = alert_data.get('title', 'Alerta')
        description = alert_data.get('description', '')
        
        # Emojis según el tipo de alerta
        emoji_map = {
            'cash_threshold': '💰',
            'battery_low': '🔋',
            'no_show': '⚠️',
            'off_zone': '📍',
            'late_delivery': '⏰',
            'emergency': '🚨'
        }
        
        # Emojis según severidad
        severity_emoji = {
            'low': '🟡',
            'medium': '🟠', 
            'high': '🔴',
            'critical': '🚨'
        }
        
        emoji = emoji_map.get(alert_type, '⚠️')
        sev_emoji = severity_emoji.get(severity, '🟠')
        
        message = f"{emoji} *ALERTA LOGINEXIA* {sev_emoji}\n\n"
        message += f"*{title}*\n"
        message += f"{description}\n\n"
        message += f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        message += f"🔗 Revisa tu dashboard para más detalles"
        
        return message
    
    def send_bulk_alerts(self, riders_phones: List[str], alert_data: Dict) -> Dict[str, bool]:
        """
        Envía alertas a múltiples repartidores
        
        Args:
            riders_phones: Lista de números de teléfono
            alert_data: Datos de la alerta
            
        Returns:
            Dict[str, bool]: Resultado del envío por cada número
        """
        results = {}
        
        for phone in riders_phones:
            results[phone] = self.send_alert_message(phone, alert_data)
            
        return results
    
    def get_message_status(self, message_id: str) -> Optional[Dict]:
        """
        Obtiene el estado de un mensaje enviado
        
        Args:
            message_id: ID del mensaje
            
        Returns:
            Dict: Estado del mensaje o None si hay error
        """
        try:
            url = f"https://graph.facebook.com/{self.version}/{message_id}"
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get message status: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting message status: {str(e)}")
            return None

# Plantillas de mensajes predefinidas
WHATSAPP_TEMPLATES = {
    "cash_alert": {
        "name": "cash_threshold_alert",
        "description": "Alerta cuando el repartidor supera el límite de efectivo"
    },
    "battery_alert": {
        "name": "battery_low_alert", 
        "description": "Alerta de batería baja"
    },
    "zone_alert": {
        "name": "off_zone_alert",
        "description": "Alerta cuando el repartidor sale de zona"
    }
}

