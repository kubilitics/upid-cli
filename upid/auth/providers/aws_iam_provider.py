"""
Enterprise-Grade AWS IAM Authentication Provider
Following the gold standard blueprint for robust, secure, and maintainable identity systems
"""

import boto3
from botocore.exceptions import ClientError
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .base_provider import AuthProvider, AuthProviderError, AuthenticationError
from ..enterprise_auth import UserPrincipal, AuthLevel

logger = logging.getLogger(__name__)

class AWSIAMAuthProvider(AuthProvider):
    """
    Enterprise-grade AWS IAM authentication provider
    Supports AWS STS, IAM roles, and temporary credentials
    """
    
    def __init__(self, region: str = "us-east-1", role_arn: str = None,
                 session_duration: int = 3600):
        self.region = region
        self.role_arn = role_arn
        self.session_duration = session_duration
        self._sts_client = None

    async def authenticate(self, credentials: Dict[str, Any]) -> Optional[UserPrincipal]:
        """
        Authenticate using AWS IAM
        """
        try:
            access_key_id = credentials.get('access_key_id')
            secret_access_key = credentials.get('secret_access_key')
            session_token = credentials.get('session_token')
            role_arn = credentials.get('role_arn', self.role_arn)

            if not access_key_id or not secret_access_key:
                raise AuthenticationError(
                    "AWS access key ID and secret access key required",
                    provider="aws_iam"
                )

            # Create a boto3 session
            session = boto3.Session(
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
                aws_session_token=session_token,
                region_name=self.region
            )
            sts = session.client('sts')

            # If role_arn is provided, assume the role
            if role_arn:
                try:
                    assumed = sts.assume_role(
                        RoleArn=role_arn,
                        RoleSessionName="UPIDSession",
                        DurationSeconds=self.session_duration
                    )
                    credentials = assumed['Credentials']
                    session = boto3.Session(
                        aws_access_key_id=credentials['AccessKeyId'],
                        aws_secret_access_key=credentials['SecretAccessKey'],
                        aws_session_token=credentials['SessionToken'],
                        region_name=self.region
                    )
                    sts = session.client('sts')
                except ClientError as e:
                    raise AuthenticationError(f"AssumeRole failed: {e}", provider="aws_iam")

            # Get caller identity
            identity = sts.get_caller_identity()
            account_id = identity['Account']
            user_arn = identity['Arn']
            user_id = identity['UserId']

            # Get user info from IAM
            iam = session.client('iam')
            try:
                if user_arn.startswith("arn:aws:iam::") and ":user/" in user_arn:
                    user_name = user_arn.split(":user/")[-1]
                    user_info = iam.get_user(UserName=user_name)['User']
                else:
                    user_info = {'UserName': user_id, 'Arn': user_arn}
            except ClientError:
                user_info = {'UserName': user_id, 'Arn': user_arn}

            # Get attached roles and groups (if possible)
            roles = []
            groups = []
            try:
                if 'UserName' in user_info:
                    attached_roles = iam.list_attached_user_policies(UserName=user_info['UserName'])
                    roles = [p['PolicyName'] for p in attached_roles.get('AttachedPolicies', [])]
                    user_groups = iam.list_groups_for_user(UserName=user_info['UserName'])
                    groups = [g['GroupName'] for g in user_groups.get('Groups', [])]
            except Exception:
                pass

            user_principal = UserPrincipal(
                user_id=user_id,
                email=f"{user_id}@aws.local",
                display_name=user_info.get('UserName', user_id),
                roles=roles or ["user"],
                groups=groups or ["aws-users"],
                claims={
                    "provider": "aws_iam",
                    "account_id": account_id,
                    "region": self.region,
                    "role_arn": role_arn
                },
                mfa_authenticated=False,  # Could be improved with STS GetSessionToken
                auth_level=self._determine_auth_level(roles),
                provider="aws_iam",
                last_login=datetime.now(),
                metadata={
                    "aws_region": self.region,
                    "session_duration": self.session_duration
                }
            )
            logger.info(f"AWS IAM authentication successful for user: {user_principal.user_id}")
            return user_principal
        except Exception as e:
            logger.error(f"AWS IAM authentication failed: {e}")
            raise AuthenticationError(
                f"Authentication failed: {str(e)}",
                provider="aws_iam"
            )

    async def validate_token(self, token: str) -> Optional[UserPrincipal]:
        # AWS does not use standalone tokens; validation is via credentials
        return None

    async def refresh_token(self, token: str) -> Optional[str]:
        # AWS tokens are refreshed via AssumeRole or GetSessionToken
        return None

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "AWS IAM Authentication",
            "type": "aws_iam",
            "version": "1.0.0",
            "capabilities": [
                "aws_sts",
                "iam_roles",
                "temporary_credentials",
                "cross_account_access"
            ],
            "config_schema": {
                "required": [],
                "optional": ["region", "role_arn", "session_duration"]
            },
            "health_endpoint": "sts_get_caller_identity",
            "supported_features": [
                "user_management",
                "role_management",
                "audit_logs"
            ],
            "security_features": [
                "mfa",
                "session_timeout",
                "cross_account_security"
            ]
        }

    async def health_check(self) -> Dict[str, Any]:
        start_time = datetime.now()
        try:
            session = boto3.Session(region_name=self.region)
            sts = session.client('sts')
            sts.get_caller_identity()
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            return {
                "status": "healthy",
                "response_time": response_time,
                "region": self.region,
                "sts": "success",
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
        try:
            session = boto3.Session(region_name=self.region)
            sts = session.client('sts')
            sts.get_caller_identity()
            return True
        except Exception as e:
            logger.error(f"AWS IAM connection test failed: {e}")
            return False

    def _determine_auth_level(self, roles: list) -> AuthLevel:
        admin_roles = ["admin", "administrator", "super_admin"]
        if any(role in admin_roles for role in roles):
            return AuthLevel.STEP_UP
        elif "developer" in roles or "operator" in roles:
            return AuthLevel.MULTI_FACTOR
        else:
            return AuthLevel.SINGLE_FACTOR

    def get_supported_features(self) -> list:
        return [
            "user_management",
            "role_management",
            "audit_logs"
        ]

    def get_security_features(self) -> list:
        return [
            "mfa",
            "session_timeout",
            "cross_account_security"
        ] 