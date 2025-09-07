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
