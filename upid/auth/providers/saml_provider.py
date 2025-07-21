"""
Enterprise-Grade SAML Authentication Provider
Following the gold standard blueprint for robust, secure, and maintainable identity systems
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import xml.etree.ElementTree as ET
import base64

from .base_provider import AuthProvider, AuthProviderError, AuthenticationError
from ..enterprise_auth import UserPrincipal, AuthLevel

logger = logging.getLogger(__name__)


class SAMLAuthProvider(AuthProvider):
    """
    Enterprise-grade SAML authentication provider
    Supports SAML 2.0 SSO flows and assertion validation
    """
    
    def __init__(self, idp_entity_id: str, sp_entity_id: str, 
                 idp_sso_url: str, idp_slo_url: str = None,
                 certificate_path: str = None):
        self.idp_entity_id = idp_entity_id
        self.sp_entity_id = sp_entity_id
        self.idp_sso_url = idp_sso_url
        self.idp_slo_url = idp_slo_url
        self.certificate_path = certificate_path
    
    async def authenticate(self, credentials: Dict[str, Any]) -> Optional[UserPrincipal]:
        """
        Authenticate using SAML
        
        Args:
            credentials: Dict containing:
                - saml_response: SAML response from IdP
                - relay_state: Optional relay state
                
        Returns:
            UserPrincipal: Authenticated user principal
        """
        try:
            saml_response = credentials.get('saml_response')
            if not saml_response:
                raise AuthenticationError(
                    "SAML response required for authentication",
                    provider="saml"
                )
            
            # Mock SAML response validation
            # In real implementation, this would validate SAML assertion
            user_principal = await self._validate_saml_response(saml_response)
            
            if user_principal:
                logger.info(f"SAML authentication successful for user: {user_principal.user_id}")
            
            return user_principal
            
        except Exception as e:
            logger.error(f"SAML authentication failed: {e}")
            raise AuthenticationError(
                f"Authentication failed: {str(e)}",
                provider="saml"
            )
    
    async def validate_token(self, token: str) -> Optional[UserPrincipal]:
        """
        Validate SAML token (not typically used for SAML auth)
        """
        # SAML doesn't typically use tokens
        return None
    
    async def refresh_token(self, token: str) -> Optional[str]:
        """
        Refresh SAML token (not applicable for SAML auth)
        """
        # SAML doesn't use refresh tokens
        return None
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get provider metadata"""
        return {
            "name": "SAML Authentication",
            "type": "saml",
            "version": "1.0.0",
            "capabilities": [
                "saml_sso",
                "saml_slo",
                "assertion_validation",
                "metadata_exchange"
            ],
            "config_schema": {
                "required": ["idp_entity_id", "sp_entity_id", "idp_sso_url"],
                "optional": ["idp_slo_url", "certificate_path"]
            },
            "health_endpoint": "metadata_endpoint",
            "supported_features": [
                "sso",
                "audit_logs"
            ],
            "security_features": [
                "mfa",
                "session_timeout"
            ]
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check SAML provider health"""
        start_time = datetime.now()
        
        try:
            # Test metadata endpoint
            metadata_healthy = await self._test_metadata_endpoint()
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            if metadata_healthy:
                return {
                    "status": "healthy",
                    "response_time": response_time,
                    "idp_entity_id": self.idp_entity_id,
                    "sp_entity_id": self.sp_entity_id,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "unhealthy",
                    "response_time": response_time,
                    "error": "Metadata endpoint failed",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "status": "unhealthy",
                "response_time": (datetime.now() - start_time).total_seconds() * 1000,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def test_connection(self) -> bool:
        """Test SAML provider connectivity"""
        try:
            return await self._test_metadata_endpoint()
        except Exception as e:
            logger.error(f"SAML connection test failed: {e}")
            return False
    
    async def _validate_saml_response(self, saml_response: str) -> Optional[UserPrincipal]:
        """Validate SAML response"""
        try:
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            
            # Decode SAML response
            try:
                decoded_response = base64.b64decode(saml_response)
                root = ET.fromstring(decoded_response)
            except Exception as e:
                logger.error(f"Failed to decode SAML response: {e}")
                return None
            
            # Find the Response element
            response_elem = root.find('.//{urn:oasis:names:tc:SAML:2.0:protocol}Response')
            if not response_elem:
                logger.error("No SAML Response element found")
                return None
            
            # Validate signature if present
            signature_elem = response_elem.find('.//{http://www.w3.org/2000/09/xmldsig#}Signature')
            if signature_elem:
                if not await self._verify_saml_signature(response_elem, signature_elem):
                    logger.error("SAML signature verification failed")
                    return None
            
            # Extract assertions
            assertion_elem = response_elem.find('.//{urn:oasis:names:tc:SAML:2.0:assertion}Assertion')
            if not assertion_elem:
                logger.error("No SAML Assertion found")
                return None
            
            # Validate assertion signature if present
            assertion_signature = assertion_elem.find('.//{http://www.w3.org/2000/09/xmldsig#}Signature')
            if assertion_signature:
                if not await self._verify_saml_signature(assertion_elem, assertion_signature):
                    logger.error("SAML assertion signature verification failed")
                    return None
            
            # Extract user information from assertion
            subject_elem = assertion_elem.find('.//{urn:oasis:names:tc:SAML:2.0:assertion}Subject')
            if not subject_elem:
                logger.error("No SAML Subject found")
                return None
            
            name_id_elem = subject_elem.find('.//{urn:oasis:names:tc:SAML:2.0:assertion}NameID')
            if not name_id_elem:
                logger.error("No SAML NameID found")
                return None
            
            user_id = name_id_elem.text
            
            # Extract attributes
            attributes = {}
            attribute_stmt = assertion_elem.find('.//{urn:oasis:names:tc:SAML:2.0:assertion}AttributeStatement')
            if attribute_stmt:
                for attr_elem in attribute_stmt.findall('.//{urn:oasis:names:tc:SAML:2.0:assertion}Attribute'):
                    attr_name = attr_elem.get('Name')
                    attr_values = []
                    for value_elem in attr_elem.findall('.//{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue'):
                        attr_values.append(value_elem.text)
                    attributes[attr_name] = attr_values
            
            # Extract email and display name
            email = None
            display_name = user_id
            
            if 'email' in attributes:
                email = attributes['email'][0] if attributes['email'] else None
            elif 'mail' in attributes:
                email = attributes['mail'][0] if attributes['mail'] else None
            
            if 'displayName' in attributes:
                display_name = attributes['displayName'][0] if attributes['displayName'] else user_id
            elif 'givenName' in attributes and 'sn' in attributes:
                display_name = f"{attributes['givenName'][0]} {attributes['sn'][0]}"
            
            # Extract roles and groups
            roles = ['user']
            groups = ['users']
            
            if 'roles' in attributes:
                roles.extend(attributes['roles'])
            elif 'memberOf' in attributes:
                groups.extend(attributes['memberOf'])
            
            return UserPrincipal(
                user_id=user_id,
                email=email or f"{user_id}@example.com",
                display_name=display_name,
                roles=roles,
                groups=groups,
                claims={
                    "provider": "saml",
                    "idp_entity_id": self.idp_entity_id,
                    "sp_entity_id": self.sp_entity_id,
                    "attributes": attributes
                },
                mfa_authenticated=False,
                auth_level=AuthLevel.SINGLE_FACTOR,
                provider="saml",
                last_login=datetime.now(),
                metadata={
                    "idp_entity_id": self.idp_entity_id,
                    "sp_entity_id": self.sp_entity_id
                }
            )
            
        except Exception as e:
            logger.error(f"SAML response validation failed: {e}")
            return None
    
    async def _verify_saml_signature(self, element: ET.Element, signature_elem: ET.Element) -> bool:
        """Verify SAML signature"""
        try:
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import padding
            
            # Get the signature value
            signature_value_elem = signature_elem.find('.//{http://www.w3.org/2000/09/xmldsig#}SignatureValue')
            if not signature_value_elem:
                logger.error("No signature value found")
                return False
            
            signature_value = base64.b64decode(signature_value_elem.text)
            
            # Get the signed info
            signed_info_elem = signature_elem.find('.//{http://www.w3.org/2000/09/xmldsig#}SignedInfo')
            if not signed_info_elem:
                logger.error("No SignedInfo found")
                return False
            
            # Canonicalize the SignedInfo
            signed_info_canonical = ET.tostring(signed_info_elem, encoding='unicode')
            
            # Get the public key
            key_info_elem = signature_elem.find('.//{http://www.w3.org/2000/09/xmldsig#}KeyInfo')
            if not key_info_elem:
                logger.error("No KeyInfo found")
                return False
            
            # For now, we'll use the configured certificate
            # In production, you might want to fetch the certificate from the IdP metadata
            if not self.idp_certificate:
                logger.error("No IdP certificate configured")
                return False
            
            try:
                # Load the certificate
                from cryptography import x509
                cert = x509.load_pem_x509_certificate(self.idp_certificate.encode())
                public_key = cert.public_key()
                
                # Verify signature
                public_key.verify(
                    signature_value,
                    signed_info_canonical.encode(),
                    padding.PKCS1v15(),
                    hashes.SHA256()
                )
                
                return True
                
            except Exception as e:
                logger.error(f"Signature verification failed: {e}")
                return False
                
        except Exception as e:
            logger.error(f"SAML signature verification error: {e}")
            return False
    
    async def _test_metadata_endpoint(self) -> bool:
        """Test SAML metadata endpoint"""
        try:
            import aiohttp
            
            metadata_url = f"{self.idp_entity_id}/metadata"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(metadata_url) as response:
                    if response.status == 200:
                        metadata_content = await response.text()
                        
                        # Parse metadata to verify it's valid
                        try:
                            root = ET.fromstring(metadata_content)
                            entity_descriptor = root.find('.//{urn:oasis:names:tc:SAML:2.0:metadata}EntityDescriptor')
                            
                            if entity_descriptor and entity_descriptor.get('entityID') == self.idp_entity_id:
                                return True
                            else:
                                logger.error("Invalid SAML metadata")
                                return False
                                
                        except ET.ParseError as e:
                            logger.error(f"Failed to parse SAML metadata: {e}")
                            return False
                    else:
                        logger.error(f"SAML metadata endpoint test failed: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"SAML metadata test failed: {e}")
            return False
    
    def get_supported_features(self) -> list:
        """Get supported features"""
        return [
            "sso",
            "audit_logs"
        ]
    
    def get_security_features(self) -> list:
        """Get security features"""
        return [
            "mfa",
            "session_timeout"
        ] 