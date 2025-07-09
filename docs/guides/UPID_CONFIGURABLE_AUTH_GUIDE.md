# UPID Configurable Authentication Guide

## Overview

UPID CLI now supports configurable authentication that allows organizations to use their preferred authentication methods via environment variables, while keeping it simple for individual users with kubectl access.

## Authentication Types

### 1. Kubectl Authentication (Default for Individuals)

**Perfect for individual users with kubectl access**

```bash
# No environment variables needed if kubectl is configured
export UPID_AUTH_TYPE=kubectl

# Optional: Specify certificate paths for kubectl
export UPID_AUTH_CERT_PATH=/path/to/client.crt
export UPID_AUTH_KEY_PATH=/path/to/client.key
export UPID_AUTH_CA_PATH=/path/to/ca.crt
```

**Usage:**
```bash
# Test kubectl authentication
upid configurable-auth test

# Show status
upid configurable-auth status
```

### 2. OIDC Authentication (Enterprise)

**For organizations using OIDC providers like Azure AD, AWS Cognito, Google Cloud, etc.**

```bash
# Basic OIDC configuration
export UPID_AUTH_TYPE=oidc
export UPID_AUTH_ENDPOINT=https://your-oidc-provider.com/oauth2/token
export UPID_AUTH_CLIENT_ID=your_client_id
export UPID_AUTH_CLIENT_SECRET=your_client_secret

# Optional OIDC parameters
export UPID_AUTH_SCOPE="openid profile email"
export UPID_AUTH_AUDIENCE=your_api_audience
export UPID_AUTH_ISSUER=https://your-oidc-provider.com
export UPID_AUTH_REDIRECT_URI=https://your-app.com/callback
export UPID_AUTH_PROVIDER=azure  # azure, aws, gcp, okta, auth0, etc.
```

**Usage:**
```bash
# Configure OIDC authentication
upid configurable-auth configure --auth-type oidc --endpoint https://your-oidc-provider.com/oauth2/token --client-id your_client_id --client-secret your_client_secret

# Test OIDC authentication
upid configurable-auth test
```

### 3. SAML Authentication (Enterprise)

**For organizations using SAML providers**

```bash
# Basic SAML configuration
export UPID_AUTH_TYPE=saml
export UPID_AUTH_ENDPOINT=https://your-saml-provider.com/saml/login
export UPID_AUTH_CLIENT_ID=your_client_id
export UPID_AUTH_CLIENT_SECRET=your_client_secret

# Optional SAML parameters
export UPID_AUTH_PROVIDER=azure  # azure, okta, onelogin, etc.
export UPID_AUTH_TENANT_ID=your_tenant_id
```

**Usage:**
```bash
# Configure SAML authentication
upid configurable-auth configure --auth-type saml --endpoint https://your-saml-provider.com/saml/login --client-id your_client_id --client-secret your_client_secret

# Test SAML authentication
upid configurable-auth test
```

### 4. LDAP Authentication (Enterprise)

**For organizations using LDAP/Active Directory**

```bash
# Basic LDAP configuration
export UPID_AUTH_TYPE=ldap
export UPID_AUTH_ENDPOINT=https://your-ldap-gateway.com/auth
export UPID_AUTH_USERNAME=your_username
export UPID_AUTH_PASSWORD=your_password

# Optional LDAP parameters
export UPID_AUTH_PROVIDER=active_directory  # active_directory, openldap, etc.
```

**Usage:**
```bash
# Configure LDAP authentication
upid configurable-auth configure --auth-type ldap --endpoint https://your-ldap-gateway.com/auth --username your_username --password your_password

# Test LDAP authentication
upid configurable-auth test
```

### 5. Custom Authentication (Enterprise)

**For organizations with custom authentication systems**

```bash
# Basic custom configuration
export UPID_AUTH_TYPE=custom
export UPID_AUTH_ENDPOINT=https://your-auth-service.com/authenticate

# Custom headers and parameters
export UPID_AUTH_CUSTOM_HEADERS='{"X-API-Key": "your_api_key", "X-Client-ID": "your_client_id"}'
export UPID_AUTH_CUSTOM_PARAMS='{"grant_type": "client_credentials", "scope": "read write"}'

# Or use traditional credentials
export UPID_AUTH_USERNAME=your_username
export UPID_AUTH_PASSWORD=your_password
export UPID_AUTH_TOKEN=your_token
```

**Usage:**
```bash
# Configure custom authentication
upid configurable-auth configure --auth-type custom --endpoint https://your-auth-service.com/authenticate --custom-headers '{"X-API-Key": "your_api_key"}' --custom-params '{"grant_type": "client_credentials"}'

# Test custom authentication
upid configurable-auth test
```

## Enterprise Examples

### Azure AD OIDC

```bash
export UPID_AUTH_TYPE=oidc
export UPID_AUTH_ENDPOINT=https://login.microsoftonline.com/YOUR_TENANT_ID/oauth2/v2.0/token
export UPID_AUTH_CLIENT_ID=YOUR_CLIENT_ID
export UPID_AUTH_CLIENT_SECRET=YOUR_CLIENT_SECRET
export UPID_AUTH_SCOPE="openid profile email"
export UPID_AUTH_AUDIENCE=YOUR_API_AUDIENCE
export UPID_AUTH_PROVIDER=azure
```

### AWS Cognito

```bash
export UPID_AUTH_TYPE=oidc
export UPID_AUTH_ENDPOINT=https://cognito-idp.YOUR_REGION.amazonaws.com/YOUR_USER_POOL_ID/oauth2/token
export UPID_AUTH_CLIENT_ID=YOUR_CLIENT_ID
export UPID_AUTH_CLIENT_SECRET=YOUR_CLIENT_SECRET
export UPID_AUTH_SCOPE="openid profile email"
export UPID_AUTH_PROVIDER=aws
```

### Google Cloud OIDC

```bash
export UPID_AUTH_TYPE=oidc
export UPID_AUTH_ENDPOINT=https://oauth2.googleapis.com/token
export UPID_AUTH_CLIENT_ID=YOUR_CLIENT_ID
export UPID_AUTH_CLIENT_SECRET=YOUR_CLIENT_SECRET
export UPID_AUTH_SCOPE="openid profile email"
export UPID_AUTH_PROVIDER=gcp
```

### Okta OIDC

```bash
export UPID_AUTH_TYPE=oidc
export UPID_AUTH_ENDPOINT=https://YOUR_DOMAIN.okta.com/oauth2/v1/token
export UPID_AUTH_CLIENT_ID=YOUR_CLIENT_ID
export UPID_AUTH_CLIENT_SECRET=YOUR_CLIENT_SECRET
export UPID_AUTH_SCOPE="openid profile email"
export UPID_AUTH_AUDIENCE=YOUR_API_AUDIENCE
export UPID_AUTH_PROVIDER=okta
```

### Auth0

```bash
export UPID_AUTH_TYPE=oidc
export UPID_AUTH_ENDPOINT=https://YOUR_DOMAIN.auth0.com/oauth/token
export UPID_AUTH_CLIENT_ID=YOUR_CLIENT_ID
export UPID_AUTH_CLIENT_SECRET=YOUR_CLIENT_SECRET
export UPID_AUTH_SCOPE="openid profile email"
export UPID_AUTH_AUDIENCE=YOUR_API_AUDIENCE
export UPID_AUTH_PROVIDER=auth0
```

## Commands

### Status Command

Check current authentication configuration and status:

```bash
upid configurable-auth status
```

This shows:
- Current authentication type
- Configuration details
- Authentication status
- Environment variables
- User information

### Configure Command

Configure authentication settings:

```bash
# Configure OIDC
upid configurable-auth configure --auth-type oidc --endpoint https://your-provider.com/oauth2/token --client-id your_client_id --client-secret your_client_secret

# Configure SAML
upid configurable-auth configure --auth-type saml --endpoint https://your-provider.com/saml/login --client-id your_client_id --client-secret your_client_secret

# Configure LDAP
upid configurable-auth configure --auth-type ldap --endpoint https://your-ldap-gateway.com/auth --username your_username --password your_password

# Configure Custom
upid configurable-auth configure --auth-type custom --endpoint https://your-auth-service.com/authenticate --custom-headers '{"X-API-Key": "your_api_key"}'
```

### Test Command

Test current authentication configuration:

```bash
upid configurable-auth test
```

This validates the authentication and shows:
- Success/failure status
- Authentication method used
- User information
- Error details if failed

### Reset Command

Reset to default kubectl authentication:

```bash
upid configurable-auth reset
```

This unsets all authentication environment variables and returns to kubectl-based authentication.

### Help Command

Show comprehensive help:

```bash
upid configurable-auth help
```

## Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `UPID_AUTH_TYPE` | Authentication type | Yes | `kubectl` |
| `UPID_AUTH_ENDPOINT` | Authentication endpoint URL | For non-kubectl | None |
| `UPID_AUTH_CLIENT_ID` | Client ID for OIDC/SAML | For OIDC/SAML | None |
| `UPID_AUTH_CLIENT_SECRET` | Client secret for OIDC/SAML | For OIDC/SAML | None |
| `UPID_AUTH_USERNAME` | Username for authentication | For LDAP/Custom | None |
| `UPID_AUTH_PASSWORD` | Password for authentication | For LDAP/Custom | None |
| `UPID_AUTH_TOKEN` | Authentication token | Optional | None |
| `UPID_AUTH_PROVIDER` | Authentication provider | Optional | None |
| `UPID_AUTH_SCOPE` | OIDC scope | Optional | `openid profile email` |
| `UPID_AUTH_AUDIENCE` | OIDC audience | Optional | None |
| `UPID_AUTH_ISSUER` | OIDC issuer | Optional | None |
| `UPID_AUTH_TENANT_ID` | Tenant ID for SAML | Optional | None |
| `UPID_AUTH_REDIRECT_URI` | OIDC redirect URI | Optional | None |
| `UPID_AUTH_CERT_PATH` | Certificate path for kubectl | Optional | None |
| `UPID_AUTH_KEY_PATH` | Key path for kubectl | Optional | None |
| `UPID_AUTH_CA_PATH` | CA certificate path for kubectl | Optional | None |
| `UPID_AUTH_CUSTOM_HEADERS` | Custom headers as JSON | For Custom | None |
| `UPID_AUTH_CUSTOM_PARAMS` | Custom parameters as JSON | For Custom | None |

## Integration with Existing Commands

The configurable authentication system integrates seamlessly with all existing UPID CLI commands:

```bash
# All commands will use the configured authentication
upid cluster list
upid analyze my-cluster
upid optimize my-cluster
upid report my-cluster
```

## Security Best Practices

1. **Environment Variables**: Store sensitive values in environment variables, not in scripts
2. **Secrets Management**: Use your organization's secrets management system
3. **Certificate Security**: Secure certificate files with appropriate permissions
4. **Token Rotation**: Implement token rotation for long-lived tokens
5. **Audit Logging**: Enable audit logging for authentication events

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Check environment variables are set correctly
   - Verify endpoint URLs are accessible
   - Ensure credentials are valid

2. **kubectl Not Working**
   - Verify kubectl is installed and configured
   - Check kubeconfig file permissions
   - Test with `kubectl cluster-info`

3. **OIDC Issues**
   - Verify client ID and secret
   - Check scope and audience settings
   - Ensure redirect URI is configured

4. **SAML Issues**
   - Verify SAML endpoint is accessible
   - Check client ID and secret
   - Ensure proper certificate configuration

### Debug Commands

```bash
# Check current configuration
upid configurable-auth status

# Test authentication
upid configurable-auth test

# Reset to defaults
upid configurable-auth reset

# Show help
upid configurable-auth help
```

## Migration from Traditional Auth

If you're currently using the traditional UPID authentication system:

1. **For Individual Users**: No migration needed - kubectl authentication works out of the box
2. **For Enterprise Users**: Configure your preferred authentication method using the examples above
3. **For Organizations**: Set up environment variables in your CI/CD pipeline or deployment scripts

## Support

For support with configurable authentication:

1. Check the help command: `upid configurable-auth help`
2. Review the status command: `upid configurable-auth status`
3. Test your configuration: `upid configurable-auth test`
4. Contact support with your configuration details (excluding sensitive information) 