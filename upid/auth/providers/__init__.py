"""
Enterprise Authentication Providers for UPID CLI
Following the gold standard blueprint for robust, secure, and maintainable identity systems
"""

from .base_provider import AuthProvider
from .kubeconfig_provider import KubeconfigAuthProvider
from .token_provider import TokenAuthProvider
from .oidc_provider import OIDCAuthProvider
from .ldap_provider import LDAPAuthProvider
from .saml_provider import SAMLAuthProvider
from .aws_iam_provider import AWSIAMAuthProvider
from .gcp_iam_provider import GCPIAMAuthProvider
from .azure_ad_provider import AzureADAuthProvider

__all__ = [
    'AuthProvider',
    'KubeconfigAuthProvider',
    'TokenAuthProvider',
    'OIDCAuthProvider',
    'LDAPAuthProvider',
    'SAMLAuthProvider',
    'AWSIAMAuthProvider',
    'GCPIAMAuthProvider',
    'AzureADAuthProvider'
] 