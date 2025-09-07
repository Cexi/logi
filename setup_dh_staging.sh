#!/bin/bash

echo "🚚 Configurando Delivery Hero STAGING para fleet.loginexia.com"

# 1. ACTUALIZAR .env con URLs de STAGING
echo "📝 Actualizando .env con configuración de STAGING..."

# Hacer backup del .env actual
cp .env .env.backup

# Crear nuevo .env con configuración de STAGING
cat > .env << 'EOF'
# ============================================
# CONFIGURACIÓN DE STAGING - fleet.loginexia.com
# ============================================

# Flask Configuration
FLASK_ENV=production
FLASK_APP=app:application
DEBUG=False

# Claves de seguridad
SECRET_KEY=fleet-loginexia-secret-key-change-in-real-production-2024
JWT_SECRET_KEY=fleet-loginexia-jwt-key-change-in-real-production-2024

# Base de Datos
DATABASE_URL=sqlite:///data/app.db

# Redis
REDIS_URL=redis://redis:6379/0

# ============================================
# 🚚 DELIVERY HERO - CONFIGURACIÓN STAGING
# ============================================
# IMPORTANTE: Estas son las URLs de STAGING (no producción)
DH_ENVIRONMENT=staging

# URLs de STAGING de Delivery Hero
DH_API_BASE_URL=https://gv-pl.usehurrier.com
DH_STS_BASE_URL=https://sts-st.dh-auth.io

# Credenciales de STAGING (CAMBIAR POR LAS TUYAS)
DH_CLIENT_ID=loginexia-87
DH_KEY_ID=loginexia-87-key-id
DH_AUDIENCE=https://sts-st.dh-auth.io/oauth2/token

# Ruta a la clave privada RSA
DH_PRIVATE_KEY_PATH=/app/keys/dh_private_key.pem

# Scopes necesarios
DH_SCOPES=read write

# Timeouts y configuración
DH_TOKEN_EXPIRY=7200
DH_REQUEST_TIMEOUT=30

# ============================================
# 🤖 OPENAI API (si la tienes)
# ============================================
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4-turbo-preview

# ============================================
# 📱 WHATSAPP (Opcional)
# ============================================
WHATSAPP_ACCESS_TOKEN=
WHATSAPP_PHONE_NUMBER_ID=

# ============================================
# 🌐 URLs Configuration
# ============================================
API_URL=https://fleet.loginexia.com
FRONTEND_URL=https://loginexia.com
ALLOWED_ORIGINS=https://loginexia.com,https://www.loginexia.com,https://fleet.loginexia.com

# ============================================
# 📊 Logs y Monitoring
# ============================================
LOG_LEVEL=DEBUG
ENABLE_DH_DEBUG=true
EOF

echo "✅ .env actualizado con URLs de STAGING"

# 2. CREAR SERVICIO MEJORADO PARA DELIVERY HERO STAGING
echo "📦 Creando servicio actualizado para DH Staging..."

mkdir -p src/services/delivery_hero

cat > src/services/delivery_hero/dh_auth_staging.py << 'EOF'
"""
Servicio de autenticación para Delivery Hero STAGING
Compatible con el ambiente de staging/testing
"""

import os
import jwt
import json
import time
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if os.getenv('ENABLE_DH_DEBUG') == 'true' else logging.INFO)

class DeliveryHeroStagingAuth:
    """
    Cliente de autenticación para Delivery Hero STAGING
    URLs de staging configuradas
    """
    
    def __init__(self):
        # Cargar configuración desde variables de entorno
        self.environment = os.getenv('DH_ENVIRONMENT', 'staging')
        self.client_id = os.getenv('DH_CLIENT_ID', 'loginexia-87')
        self.key_id = os.getenv('DH_KEY_ID', 'loginexia-87-key-id')
        
        # URLs de STAGING
        self.api_base_url = os.getenv('DH_API_BASE_URL', 'https://gv-pl.usehurrier.com')
        self.sts_url = os.getenv('DH_STS_BASE_URL', 'https://sts-st.dh-auth.io')
        self.token_endpoint = f"{self.sts_url}/oauth2/token"
        
        # Cargar clave privada
        self.private_key = self._load_private_key()
        
        # Cache de token
        self._cached_token = None
        self._token_expiry = None
        
        logger.info(f"DH Auth inicializado - Environment: {self.environment}")
        logger.info(f"STS URL: {self.sts_url}")
        logger.info(f"API URL: {self.api_base_url}")
        logger.info(f"Client ID: {self.client_id}")
    
    def _load_private_key(self) -> str:
        """Carga la clave privada RSA desde archivo o variable de entorno"""
        # Primero intentar desde archivo
        key_path = os.getenv('DH_PRIVATE_KEY_PATH', '/app/keys/dh_private_key.pem')
        
        if os.path.exists(key_path):
            try:
                with open(key_path, 'r') as f:
                    key = f.read()
                logger.info(f"Clave privada cargada desde: {key_path}")
                return key
            except Exception as e:
                logger.error(f"Error leyendo clave privada: {e}")
        
        # Si no hay archivo, intentar desde variable de entorno
        key_from_env = os.getenv('DH_PRIVATE_KEY')
        if key_from_env:
            logger.info("Clave privada cargada desde variable de entorno")
            return key_from_env
        
        logger.warning("⚠️ No se encontró clave privada RSA. Generando una de ejemplo...")
        return self._generate_example_key()
    
    def _generate_example_key(self) -> str:
        """Genera una clave de ejemplo (solo para testing)"""
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.backends import default_backend
        
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        # Guardar la clave generada
        os.makedirs('/app/keys', exist_ok=True)
        with open('/app/keys/dh_private_key.pem', 'wb') as f:
            f.write(pem)
        
        logger.info("✅ Clave RSA de ejemplo generada en /app/keys/dh_private_key.pem")
        return pem.decode('utf-8')
    
    def create_jwt_assertion(self) -> str:
        """
        Crea el JWT assertion para autenticación con STS
        Según especificaciones de Delivery Hero
        """
        now = int(time.time())
        
        # Payload del JWT
        payload = {
            "iss": self.client_id,  # Issuer
            "sub": self.client_id,  # Subject
            "aud": self.token_endpoint,  # Audience
            "iat": now,  # Issued at
            "exp": now + 60,  # Expira en 60 segundos
            "jti": f"{self.client_id}_{now}"  # JWT ID único
        }
        
        # Headers
        headers = {
            "alg": "RS256",
            "typ": "JWT",
            "kid": self.key_id
        }
        
        try:
            # Firmar el JWT
            token = jwt.encode(
                payload,
                self.private_key,
                algorithm="RS256",
                headers=headers
            )
            
            # Asegurar que es string
            if isinstance(token, bytes):
                token = token.decode('utf-8')
            
            logger.debug(f"JWT Assertion creado: {token[:50]}...")
            return token
            
        except Exception as e:
            logger.error(f"Error creando JWT assertion: {e}")
            raise
    
    def get_access_token(self, force_refresh: bool = False) -> str:
        """
        Obtiene un access token del STS
        Usa cache si el token aún es válido
        """
        # Verificar cache
        if not force_refresh and self._cached_token and self._token_expiry:
            if datetime.now() < self._token_expiry:
                logger.debug("Usando token cacheado")
                return self._cached_token
        
        logger.info("Solicitando nuevo access token...")
        
        # Crear JWT assertion
        client_assertion = self.create_jwt_assertion()
        
        # Preparar request
        data = {
            "grant_type": "client_credentials",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": client_assertion
        }
        
        # Si hay scopes configurados
        scopes = os.getenv('DH_SCOPES', 'read write')
        if scopes:
            data["scope"] = scopes
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        
        try:
            # Hacer request al STS
            logger.debug(f"POST {self.token_endpoint}")
            response = requests.post(
                self.token_endpoint,
                data=data,
                headers=headers,
                timeout=30
            )
            
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                token_data = response.json()
                
                # Guardar en cache
                self._cached_token = token_data['access_token']
                expires_in = token_data.get('expires_in', 7200)
                self._token_expiry = datetime.now() + timedelta(seconds=expires_in - 60)
                
                logger.info(f"✅ Access token obtenido, expira en {expires_in} segundos")
                return self._cached_token
            else:
                logger.error(f"❌ Error del STS: {response.status_code}")
                logger.error(f"Response: {response.text}")
                raise Exception(f"STS error: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error de conexión con STS: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Error obteniendo token: {e}")
            raise
    
    def make_api_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """
        Hace una request autenticada a la API de Delivery Hero
        """
        # Obtener token
        token = self.get_access_token()
        
        # Preparar headers
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'Bearer {token}'
        headers['Accept'] = 'application/json'
        kwargs['headers'] = headers
        
        # Construir URL completa
        url = f"{self.api_base_url}{endpoint}"
        
        logger.info(f"{method} {url}")
        
        try:
            response = requests.request(method, url, **kwargs)
            
            if response.status_code == 401:
                # Token expirado, renovar y reintentar
                logger.info("Token expirado, renovando...")
                token = self.get_access_token(force_refresh=True)
                headers['Authorization'] = f'Bearer {token}'
                response = requests.request(method, url, **kwargs)
            
            response.raise_for_status()
            return response.json() if response.text else {}
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"API Error: {e}")
            logger.error(f"Response: {e.response.text if e.response else 'No response'}")
            raise
        except Exception as e:
            logger.error(f"Request error: {e}")
            raise
    
    def test_connection(self) -> Dict:
        """
        Prueba la conexión con el API de staging
        """
        logger.info("=" * 50)
        logger.info("🧪 TESTING DELIVERY HERO STAGING CONNECTION")
        logger.info("=" * 50)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'environment': self.environment,
            'client_id': self.client_id,
            'sts_url': self.sts_url,
            'api_url': self.api_base_url,
            'tests': {}
        }
        
        # Test 1: Verificar clave privada
        try:
            if self.private_key:
                results['tests']['private_key'] = '✅ Clave privada cargada'
            else:
                results['tests']['private_key'] = '❌ Sin clave privada'
        except Exception as e:
            results['tests']['private_key'] = f'❌ Error: {str(e)}'
        
        # Test 2: Crear JWT
        try:
            jwt_token = self.create_jwt_assertion()
            results['tests']['jwt_creation'] = f'✅ JWT creado ({len(jwt_token)} chars)'
        except Exception as e:
            results['tests']['jwt_creation'] = f'❌ Error: {str(e)}'
        
        # Test 3: Obtener Access Token
        try:
            access_token = self.get_access_token(force_refresh=True)
            results['tests']['access_token'] = f'✅ Token obtenido ({len(access_token)} chars)'
            results['access_token_preview'] = f"{access_token[:20]}..."
        except Exception as e:
            results['tests']['access_token'] = f'❌ Error: {str(e)}'
        
        # Test 4: Hacer request de prueba
        try:
            # Intentar obtener información básica
            test_response = self.make_api_request('GET', '/health')
            results['tests']['api_request'] = '✅ API respondiendo'
            results['api_response'] = test_response
        except Exception as e:
            results['tests']['api_request'] = f'⚠️ Error (puede ser normal): {str(e)}'
        
        # Resumen
        logger.info("=" * 50)
        logger.info("📊 RESULTADOS DEL TEST:")
        for test, result in results['tests'].items():
            logger.info(f"  {test}: {result}")
        logger.info("=" * 50)
        
        return results


# Función helper para testing
def test_delivery_hero_staging():
    """Función para probar la conexión con DH Staging"""
    auth = DeliveryHeroStagingAuth()
    return auth.test_connection()


if __name__ == "__main__":
    # Si se ejecuta directamente, hacer test
    test_delivery_hero_staging()
EOF

echo "✅ Servicio de DH Staging creado"

# 3. CREAR SCRIPT DE TEST
echo "🧪 Creando script de test..."

cat > test_dh_staging.py << 'EOF'
#!/usr/bin/env python3
"""
Script para probar la conexión con Delivery Hero STAGING
"""

import os
import sys
sys.path.insert(0, '/app')

# Configurar logging
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from src.services.delivery_hero.dh_auth_staging import test_delivery_hero_staging

if __name__ == "__main__":
    print("🚀 Probando conexión con Delivery Hero STAGING...")
    print("=" * 60)
    
    # Mostrar configuración actual
    print("📋 Configuración actual:")
    print(f"  CLIENT_ID: {os.getenv('DH_CLIENT_ID', 'No configurado')}")
    print(f"  KEY_ID: {os.getenv('DH_KEY_ID', 'No configurado')}")
    print(f"  STS URL: {os.getenv('DH_STS_BASE_URL', 'No configurado')}")
    print(f"  API URL: {os.getenv('DH_API_BASE_URL', 'No configurado')}")
    print("=" * 60)
    
    # Ejecutar test
    try:
        results = test_delivery_hero_staging()
        print("\n✅ Test completado. Ver logs arriba para detalles.")
    except Exception as e:
        print(f"\n❌ Error en el test: {e}")
        import traceback
        traceback.print_exc()
EOF

chmod +x test_dh_staging.py

# 4. CREAR LA CLAVE RSA SI NO EXISTE
echo "🔑 Verificando clave RSA..."

if [ ! -f "keys/dh_private_key.pem" ]; then
    echo "Generando par de claves RSA..."
    mkdir -p keys
    openssl genrsa -out keys/dh_private_key.pem 2048
    openssl rsa -in keys/dh_private_key.pem -pubout -out keys/dh_public_key.pem
    
    echo "✅ Claves RSA generadas:"
    echo "  - Privada: keys/dh_private_key.pem"
    echo "  - Pública: keys/dh_public_key.pem"
    echo ""
    echo "⚠️  IMPORTANTE: Envía keys/dh_public_key.pem a Delivery Hero"
else
    echo "✅ Clave RSA ya existe"
fi

# 5. REINICIAR DOCKER
echo "🐳 Reiniciando Docker con nueva configuración..."
docker-compose restart

echo ""
echo "=========================================="
echo "✅ CONFIGURACIÓN COMPLETADA"
echo "=========================================="
echo ""
echo "📋 PRÓXIMOS PASOS:"
echo ""
echo "1. VERIFICAR tu Client ID y Key ID en .env:"
echo "   nano .env"
echo "   - DH_CLIENT_ID=loginexia-87"
echo "   - DH_KEY_ID=(el key ID que te dieron)"
echo ""
echo "2. ENVIAR tu clave pública a Delivery Hero:"
echo "   cat keys/dh_public_key.pem"
echo "   (Enviar este contenido a DH para que la registren)"
echo ""
echo "3. PROBAR la conexión:"
echo "   docker exec -it fleet_loginexia python test_dh_staging.py"
echo ""
echo "4. VER los logs:"
echo "   docker-compose logs -f"
echo ""
echo "=========================================="
echo "🔗 URLs de STAGING configuradas:"
echo "  - STS: https://sts-st.dh-auth.io/oauth2/token"
echo "  - API: https://gv-pl.usehurrier.com"
echo "=========================================="
