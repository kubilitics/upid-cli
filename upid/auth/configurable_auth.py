"""
Configurable Authentication Loader for UPID CLI
Supports dynamic, user-configurable authentication backends
"""

import logging
from typing import Dict, Any, Optional, List
from upid.auth.universal_auth import (
    AuthProviderType,
    KubeconfigAuthProvider,
    TokenAuthProvider,
    OIDCAuthProvider
)
from upid.auth.rbac import RBACManager

logger = logging.getLogger(__name__)

# Placeholder imports for enterprise providers
try:
    from upid.auth.ldap_auth import LDAPAuthProvider
except ImportError:
    LDAPAuthProvider = None
try:
    from upid.auth.saml_auth import SAMLAuthProvider
except ImportError:
    SAMLAuthProvider = None
try:
    from upid.auth.oidc_auth import OIDCAuthProvider as CustomOIDCAuthProvider
except ImportError:
    CustomOIDCAuthProvider = None

# Cloud IAM providers (placeholders)
try:
    from upid.auth.cloud import AWSIAMAuthProvider, GCPAuthProvider, AzureADAuthProvider
except ImportError:
    AWSIAMAuthProvider = None
    GCPAuthProvider = None
    AzureADAuthProvider = None


class ConfigurableAuthLoader:
    """
    Loads and manages authentication providers based on user/admin configuration
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.providers: Dict[AuthProviderType, Any] = {}
        self.rbac_manager = RBACManager()
        self._load_providers()

    def _load_providers(self):
        """Load providers from config"""
        enabled = self.config.get("enabled_providers", [])
        provider_configs = self.config.get("provider_configs", {})

        for provider in enabled:
            if provider == AuthProviderType.KUBECONFIG.value:
                self.providers[AuthProviderType.KUBECONFIG] = KubeconfigAuthProvider()
            elif provider == AuthProviderType.TOKEN.value:
                secret = provider_configs.get("token", {}).get("secret_key")
                self.providers[AuthProviderType.TOKEN] = TokenAuthProvider(secret)
            elif provider == AuthProviderType.OIDC.value:
                oidc_conf = provider_configs.get("oidc", {})
                self.providers[AuthProviderType.OIDC] = OIDCAuthProvider(
                    issuer_url=oidc_conf.get("issuer_url", "https://accounts.google.com"),
                    client_id=oidc_conf.get("client_id", "mock-client-id"),
                    client_secret=oidc_conf.get("client_secret", "mock-client-secret")
                )
            elif provider == AuthProviderType.LDAP.value and LDAPAuthProvider:
                ldap_conf = provider_configs.get("ldap", {})
                self.providers[AuthProviderType.LDAP] = LDAPAuthProvider(**ldap_conf)
            elif provider == AuthProviderType.SAML.value and SAMLAuthProvider:
                saml_conf = provider_configs.get("saml", {})
                self.providers[AuthProviderType.SAML] = SAMLAuthProvider(**saml_conf)
            elif provider == AuthProviderType.AWS_IAM.value and AWSIAMAuthProvider:
                aws_conf = provider_configs.get("aws_iam", {})
                self.providers[AuthProviderType.AWS_IAM] = AWSIAMAuthProvider(**aws_conf)
            elif provider == AuthProviderType.GCP_IAM.value and GCPAuthProvider:
                gcp_conf = provider_configs.get("gcp_iam", {})
                self.providers[AuthProviderType.GCP_IAM] = GCPAuthProvider(**gcp_conf)
            elif provider == AuthProviderType.AZURE_AD.value and AzureADAuthProvider:
                azure_conf = provider_configs.get("azure_ad", {})
                self.providers[AuthProviderType.AZURE_AD] = AzureADAuthProvider(**azure_conf)
            else:
                logger.warning(f"Unknown or unsupported provider: {provider}")

    def get_provider(self, provider_type: AuthProviderType):
        return self.providers.get(provider_type)

    def list_enabled_providers(self) -> List[str]:
        return [ptype.value for ptype in self.providers.keys()]

    def reload(self, new_config: Dict[str, Any]):
        self.config = new_config
        self.providers.clear()
        self._load_providers()

    def get_rbac_manager(self):
        return self.rbac_manager 