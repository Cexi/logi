# Loginexia - Guía de Instalación para cPanel

## Características del Producto

**Loginexia** es una plataforma completa de gestión de repartidores que incluye:

✅ **Dashboard en tiempo real** con KPIs y métricas
✅ **Sistema de alertas inteligentes** con IA
✅ **Integración con APIs de Delivery Hero**
✅ **Servicios de IA con OpenAI** (NL to SQL, RAG, recomendaciones)
✅ **Notificaciones automáticas por WhatsApp** 📱
✅ **Sistema multi-tenant** para múltiples organizaciones
✅ **Autenticación JWT** completa
✅ **API REST** documentada

## Pasos de Instalación

### 1. Subir Archivos
- Sube todos los archivos de esta carpeta al directorio `/backend` de tu servidor
- Asegúrate de que `app.py` esté en la raíz del directorio `/backend`

### 2. Configurar Python App en cPanel
1. Ve a "Setup Python App" en cPanel
2. Crea nueva aplicación:
   - **Python Version**: 3.11
   - **Application Root**: `/backend`
   - **Application URL**: `loginexia.com/backend`
   - **Application Startup File**: `app.py`
   - **Application Entry Point**: `application`

### 3. Instalar Dependencias
En el terminal de la Python App, ejecuta:
```bash
pip install -r requirements.txt
```

### 4. Configurar Base de Datos
La base de datos se configura automáticamente al iniciar la app.
Si hay problemas, revisa los logs de la aplicación en cPanel.

### 5. Acceder a la Aplicación
- **URL**: `https://loginexia.com/backend`
- **Credenciales demo**:
  - Email: demo@loginexia.com
  - Password: demo123

## Configuración de WhatsApp (Opcional)

Para habilitar notificaciones automáticas por WhatsApp:

1. **Obtener credenciales** de WhatsApp Business API
2. **Configurar en el dashboard**: Configuración → APIs → WhatsApp
3. **Probar funcionamiento** con mensaje de prueba

Ver `WHATSAPP_SETUP.md` para instrucciones detalladas.

## Estructura de Archivos
```
/backend/
├── app.py                    # Punto de entrada WSGI
├── requirements.txt          # Dependencias Python
├── INSTALL.md               # Esta guía
├── WHATSAPP_SETUP.md        # Configuración de WhatsApp
├── src/                     # Código fuente del backend
│   ├── main.py              # Aplicación Flask principal
│   ├── models/              # Modelos de base de datos
│   ├── routes/              # Endpoints de la API
│   ├── services/            # Servicios (IA, WhatsApp, etc.)
│   └── database/            # Configuración de BD
└── static/                  # Frontend compilado
```

## APIs Disponibles

### Autenticación
- `POST /api/auth/login` - Iniciar sesión
- `POST /api/auth/register` - Registrar usuario
- `POST /api/auth/refresh` - Renovar token

### Repartidores
- `GET /api/riders/overview` - Vista general de repartidores
- `GET /api/riders/{id}` - Detalles de repartidor
- `GET /api/riders/alerts` - Alertas activas

### Inteligencia Artificial
- `POST /api/ai/nl-to-sql` - Consultas en lenguaje natural
- `POST /api/ai/recommendations` - Recomendaciones personalizadas
- `POST /api/ai/chat` - Chat assistant

### WhatsApp (Nuevo)
- `POST /api/whatsapp/send-alert` - Enviar alerta individual
- `POST /api/whatsapp/send-bulk-alert` - Enviar alerta masiva
- `POST /api/whatsapp/auto-send-critical` - Procesar alertas críticas
- `GET/POST /api/whatsapp/config` - Configurar WhatsApp
- `POST /api/whatsapp/test` - Probar configuración

## Modelo de Negocio

### Tiers de Suscripción
- **Básico** ($99/mes): Hasta 50 repartidores, alertas básicas
- **Profesional** ($299/mes): Hasta 200 repartidores, IA + WhatsApp
- **Enterprise** ($799/mes): Ilimitado, soporte prioritario

### Gestión de APIs
- **OpenAI**: Pool centralizado (markup incluido)
- **Delivery Hero**: Claves individuales por cliente
- **WhatsApp**: Claves individuales por cliente

## Solución de Problemas

### La app no inicia
- Revisa los logs en cPanel → Python Apps
- Verifica que `app.py` esté en la raíz
- Asegúrate de que las dependencias estén instaladas

### Error de base de datos
- La base de datos SQLite se crea automáticamente
- Si persiste el error, elimina `src/database/app.db` y reinicia

### WhatsApp no funciona
- Verifica las credenciales en Configuración → APIs
- Comprueba que los números estén en formato internacional
- Revisa los logs de WhatsApp en el dashboard

### Frontend no carga
- Verifica que la carpeta `static/` contenga los archivos
- Comprueba la configuración de rutas en cPanel
- Asegúrate de que `index.html` esté en `static/`

## Soporte

Para soporte técnico:
- **Email**: soporte@loginexia.com
- **Documentación**: Ver archivos MD incluidos
- **Logs**: Revisar logs de la aplicación en cPanel

## Actualizaciones

Para actualizar Loginexia:
1. Hacer backup de la base de datos
2. Subir nuevos archivos
3. Reiniciar la aplicación Python
4. Verificar funcionamiento

---

**¡Loginexia está listo para usar!** 🚀

Accede a `https://loginexia.com/backend` y comienza a gestionar tus repartidores con inteligencia artificial y notificaciones automáticas por WhatsApp.

