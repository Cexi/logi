import os
import base64
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class EncryptionService:
    def __init__(self):
        self.key = self._get_encryption_key()
        self.cipher = Fernet(self.key)
    
    def _get_encryption_key(self):
        """Get or generate encryption key"""
        # In production, this should be stored securely (e.g., environment variable, key management service)
        key_env = os.environ.get('ENCRYPTION_KEY')
        if key_env:
            return key_env.encode()
        
        # Generate key from a password (for development)
        password = os.environ.get('ENCRYPTION_PASSWORD', 'default_dev_password').encode()
        salt = b'loginexia_salt_2024'  # In production, use random salt per organization
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encrypt_credentials(self, credentials_dict):
        """Encrypt credentials dictionary"""
        credentials_json = json.dumps(credentials_dict)
        encrypted_data = self.cipher.encrypt(credentials_json.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt_credentials(self, encrypted_credentials):
        """Decrypt credentials dictionary"""
        try:
            encrypted_data = base64.urlsafe_b64decode(encrypted_credentials.encode())
            decrypted_data = self.cipher.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except Exception as e:
            raise ValueError(f"Failed to decrypt credentials: {str(e)}")
    
    def encrypt_string(self, text):
        """Encrypt a string"""
        encrypted_data = self.cipher.encrypt(text.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt_string(self, encrypted_text):
        """Decrypt a string"""
        try:
            encrypted_data = base64.urlsafe_b64decode(encrypted_text.encode())
            decrypted_data = self.cipher.decrypt(encrypted_data)
            return decrypted_data.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt string: {str(e)}")
    
    def rotate_key(self, old_key, new_key):
        """Rotate encryption key (for key rotation scenarios)"""
        # This would be used to re-encrypt all credentials with a new key
        # Implementation would depend on specific requirements
        pass

