# Configuración de WhatsApp para Loginexia

## Funcionalidades de WhatsApp

Loginexia incluye un sistema completo de notificaciones por WhatsApp que permite:

- **Alertas automáticas**: Envío automático de alertas críticas y de alta severidad
- **Notificaciones personalizadas**: Mensajes formateados con emojis según el tipo de alerta
- **Gestión masiva**: Envío de alertas a múltiples repartidores simultáneamente
- **Seguimiento**: Rastreo del estado de entrega de mensajes
- **Configuración por organización**: Cada cliente puede usar sus propias credenciales

## Configuración Inicial

### 1. Obtener Credenciales de WhatsApp Business API

1. Crear una cuenta en [Meta for Developers](https://developers.facebook.com/)
2. Crear una aplicación de WhatsApp Business
3. Obtener:
   - **Access Token**: Token de acceso permanente
   - **Phone Number ID**: ID del número de teléfono verificado

### 2. Configurar en Loginexia

#### Opción A: Desde el Dashboard (Recomendado)
1. Ir a **Configuración** → **APIs** → **WhatsApp**
2. Introducir las credenciales:
   - Access Token
   - Phone Number ID
3. Hacer clic en **Guardar Configuración**
4. Probar con **Enviar Mensaje de Prueba**

#### Opción B: Desde la API
```bash
POST /api/whatsapp/config
{
  "access_token": "tu_access_token_aqui",
  "phone_number_id": "tu_phone_number_id_aqui"
}
```

## Tipos de Alertas Automáticas

### Alertas Críticas (Envío Automático)
- **cash_threshold**: Límite de efectivo superado 💰
- **emergency**: Situaciones de emergencia 🚨
- **security_alert**: Alertas de seguridad 🔒

### Alertas de Alta Severidad (Envío Automático)
- **battery_low**: Batería baja del dispositivo 🔋
- **off_zone**: Repartidor fuera de zona 📍
- **late_delivery**: Entrega tardía ⏰

### Alertas Medias/Bajas (Envío Manual)
- **no_show**: Repartidor no se presentó ⚠️
- **maintenance**: Mantenimiento programado 🔧

## Uso de la API

### Enviar Alerta Individual
```bash
POST /api/whatsapp/send-alert
{
  "alert_id": "alert_uuid",
  "rider_phone": "+34612345678"
}
```

### Enviar Alerta Masiva
```bash
POST /api/whatsapp/send-bulk-alert
{
  "alert_id": "alert_uuid",
  "rider_phones": ["+34612345678", "+34687654321"]
}
```

### Procesar Alertas Críticas Pendientes
```bash
POST /api/whatsapp/auto-send-critical
```

### Probar Configuración
```bash
POST /api/whatsapp/test
{
  "phone_number": "+34612345678"
}
```

## Formato de Mensajes

Los mensajes se formatean automáticamente con:
- **Emojis** según el tipo de alerta
- **Severidad** con colores/emojis
- **Timestamp** de la alerta
- **Enlace** al dashboard

Ejemplo de mensaje:
```
💰 *ALERTA LOGINEXIA* 🔴

*High Cash Amount Alert*
Rider Carlos Rodriguez has cash amount ≥ €120

📅 26/08/2025 15:30
🔗 Revisa tu dashboard para más detalles
```

## Números de Teléfono

### Formato Requerido
- **Internacional**: +34612345678
- **Sin espacios ni guiones**
- **Incluir código de país**

### Gestión de Números
Los números de teléfono se pueden almacenar en:
1. **Datos de la alerta**: `data.rider_phone`
2. **Información del repartidor**: `data.rider_info.phone`
3. **Contacto**: `data.contact.phone`

## Monitoreo y Logs

### Estados de Mensaje
- **sent**: Enviado correctamente
- **delivered**: Entregado al dispositivo
- **read**: Leído por el usuario
- **failed**: Error en el envío

### Logs de Actividad
Todos los envíos se registran en:
- **Base de datos**: Tabla `alerts` con campos WhatsApp
- **Logs del servidor**: `/var/log/loginexia/whatsapp.log`

## Solución de Problemas

### Error: "WhatsApp configuration not found"
- Verificar que las credenciales estén configuradas
- Comprobar que `is_active = True`

### Error: "Failed to send WhatsApp alert"
- Verificar que el Access Token sea válido
- Comprobar que el número de teléfono esté en formato internacional
- Verificar que el número esté registrado en WhatsApp

### Error: "No phone number found"
- Asegurar que las alertas incluyan el número de teléfono
- Verificar el formato de los datos de la alerta

## Límites y Consideraciones

### Límites de WhatsApp Business API
- **1000 mensajes/día** para cuentas nuevas
- **Incremento gradual** según el uso
- **24 horas** de ventana para respuestas

### Mejores Prácticas
- **No spam**: Solo enviar alertas relevantes
- **Horarios**: Respetar horarios laborales
- **Opt-out**: Permitir que los usuarios se den de baja
- **Plantillas**: Usar plantillas aprobadas para mayor entregabilidad

## Plantillas Recomendadas

Para mayor entregabilidad, crear plantillas en Meta Business:

### Plantilla: Alerta de Efectivo
```
Hola {{1}}, tienes un exceso de efectivo: €{{2}}. 
Por favor, dirígete al punto de depósito más cercano.
```

### Plantilla: Batería Baja
```
{{1}}, tu dispositivo tiene batería baja ({{2}}%). 
Busca un punto de carga para continuar operando.
```

### Plantilla: Fuera de Zona
```
{{1}}, estás fuera de tu zona asignada ({{2}}). 
Regresa a tu área de trabajo lo antes posible.
```

