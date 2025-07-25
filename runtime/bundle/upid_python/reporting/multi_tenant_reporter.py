"""
UPID CLI - Multi-tenant Reporter
Multi-tenant reporting and tenant isolation
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
from enum import Enum

logger = logging.getLogger(__name__)


class TenantRole(Enum):
    """Tenant roles"""
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


@dataclass
class Tenant:
    """Tenant information"""
    tenant_id: str
    name: str
    role: TenantRole
    created_at: datetime
    clusters: List[str]
    permissions: Dict[str, Any]


@dataclass
class TenantReport:
    """Tenant-specific report"""
    tenant_id: str
    report_type: str
    data: Dict[str, Any]
    generated_at: datetime
    permissions: List[str]


class MultiTenantReporter:
    """
    Multi-tenant Reporter
    
    Provides comprehensive multi-tenant reporting capabilities:
    - Tenant isolation and security
    - Role-based access control
    - Tenant-specific reporting
    - Cross-tenant analytics (admin only)
    - Audit logging for tenant actions
    """
    
    def __init__(self):
        self.tenants: Dict[str, Tenant] = {}
        self.tenant_reports: Dict[str, List[TenantReport]] = {}
        self.audit_log: List[Dict[str, Any]] = []
        
        logger.info("🔧 Initializing multi-tenant reporter")
    
    async def initialize(self) -> bool:
        """Initialize multi-tenant reporter"""
        try:
            logger.info("🚀 Initializing multi-tenant reporter...")
            
            # Setup default tenant (for demo purposes)
            await self._setup_default_tenant()
            
            logger.info("✅ Multi-tenant reporter initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize multi-tenant reporter: {e}")
            return False
    
    async def _setup_default_tenant(self):
        """Setup default tenant for demonstration"""
        default_tenant = Tenant(
            tenant_id="default",
            name="Default Organization",
            role=TenantRole.ADMIN,
            created_at=datetime.utcnow(),
            clusters=["cluster-1", "cluster-2"],
            permissions={
                'dashboard': True,
                'kpi_reports': True,
                'roi_analysis': True,
                'optimization': True,
                'export': True
            }
        )
        
        self.tenants["default"] = default_tenant
        self.tenant_reports["default"] = []
    
    async def create_tenant(self, 
                          tenant_id: str,
                          name: str,
                          role: TenantRole = TenantRole.USER,
                          clusters: List[str] = None) -> bool:
        """Create a new tenant"""
        try:
            logger.info(f"🏢 Creating tenant: {tenant_id}")
            
            if tenant_id in self.tenants:
                logger.error(f"❌ Tenant {tenant_id} already exists")
                return False
            
            # Set default permissions based on role
            permissions = await self._get_default_permissions(role)
            
            tenant = Tenant(
                tenant_id=tenant_id,
                name=name,
                role=role,
                created_at=datetime.utcnow(),
                clusters=clusters or [],
                permissions=permissions
            )
            
            self.tenants[tenant_id] = tenant
            self.tenant_reports[tenant_id] = []
            
            # Log audit event
            await self._log_audit_event(
                tenant_id, "tenant_created", 
                f"Tenant {name} created with role {role.value}"
            )
            
            logger.info(f"✅ Tenant {tenant_id} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create tenant: {e}")
            return False
    
    async def _get_default_permissions(self, role: TenantRole) -> Dict[str, Any]:
        """Get default permissions for a role"""
        if role == TenantRole.ADMIN:
            return {
                'dashboard': True,
                'kpi_reports': True,
                'roi_analysis': True,
                'optimization': True,
                'export': True,
                'cross_tenant_analytics': True,
                'user_management': True
            }
        elif role == TenantRole.USER:
            return {
                'dashboard': True,
                'kpi_reports': True,
                'roi_analysis': True,
                'optimization': True,
                'export': True,
                'cross_tenant_analytics': False,
                'user_management': False
            }
        else:  # VIEWER
            return {
                'dashboard': True,
                'kpi_reports': True,
                'roi_analysis': False,
                'optimization': False,
                'export': True,
                'cross_tenant_analytics': False,
                'user_management': False
            }
    
    async def generate_tenant_report(self, 
                                   tenant_id: str,
                                   report_type: str,
                                   data: Dict[str, Any]) -> Optional[TenantReport]:
        """Generate a report for a specific tenant"""
        try:
            logger.info(f"📊 Generating {report_type} report for tenant {tenant_id}")
            
            # Check if tenant exists
            if tenant_id not in self.tenants:
                logger.error(f"❌ Tenant {tenant_id} not found")
                return None
            
            # Check permissions
            tenant = self.tenants[tenant_id]
            if not await self._check_permission(tenant, report_type):
                logger.error(f"❌ Tenant {tenant_id} lacks permission for {report_type}")
                return None
            
            # Filter data for tenant
            filtered_data = await self._filter_data_for_tenant(tenant_id, data)
            
            # Create tenant report
            report = TenantReport(
                tenant_id=tenant_id,
                report_type=report_type,
                data=filtered_data,
                generated_at=datetime.utcnow(),
                permissions=await self._get_report_permissions(tenant, report_type)
            )
            
            # Store report
            if tenant_id not in self.tenant_reports:
                self.tenant_reports[tenant_id] = []
            self.tenant_reports[tenant_id].append(report)
            
            # Log audit event
            await self._log_audit_event(
                tenant_id, "report_generated", 
                f"Generated {report_type} report"
            )
            
            logger.info(f"✅ Report generated for tenant {tenant_id}")
            return report
            
        except Exception as e:
            logger.error(f"❌ Failed to generate tenant report: {e}")
            return None
    
    async def _check_permission(self, tenant: Tenant, permission: str) -> bool:
        """Check if tenant has permission for an action"""
        try:
            return tenant.permissions.get(permission, False)
        except Exception as e:
            logger.error(f"❌ Failed to check permission: {e}")
            return False
    
    async def _filter_data_for_tenant(self, tenant_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter data to only include tenant-specific information"""
        try:
            tenant = self.tenants.get(tenant_id)
            if not tenant:
                return {}
            
            filtered_data = {}
            
            # Filter clusters
            if 'clusters' in data:
                filtered_data['clusters'] = [
                    cluster for cluster in data['clusters']
                    if cluster in tenant.clusters
                ]
            
            # Filter costs
            if 'costs' in data:
                filtered_data['costs'] = [
                    cost for cost in data['costs']
                    if cost.get('cluster') in tenant.clusters
                ]
            
            # Filter optimizations
            if 'optimizations' in data:
                filtered_data['optimizations'] = [
                    opt for opt in data['optimizations']
                    if opt.get('cluster') in tenant.clusters
                ]
            
            # Add tenant-specific metadata
            filtered_data['tenant_info'] = {
                'tenant_id': tenant_id,
                'tenant_name': tenant.name,
                'role': tenant.role.value,
                'cluster_count': len(tenant.clusters)
            }
            
            return filtered_data
            
        except Exception as e:
            logger.error(f"❌ Failed to filter data for tenant: {e}")
            return {}
    
    async def _get_report_permissions(self, tenant: Tenant, report_type: str) -> List[str]:
        """Get permissions for a specific report type"""
        try:
            permissions = []
            
            if report_type == 'dashboard' and tenant.permissions.get('dashboard'):
                permissions.append('view_dashboard')
            
            if report_type == 'kpi' and tenant.permissions.get('kpi_reports'):
                permissions.append('view_kpi_reports')
            
            if report_type == 'roi' and tenant.permissions.get('roi_analysis'):
                permissions.append('view_roi_analysis')
            
            if tenant.permissions.get('export'):
                permissions.append('export_reports')
            
            return permissions
            
        except Exception as e:
            logger.error(f"❌ Failed to get report permissions: {e}")
            return []
    
    async def generate_cross_tenant_report(self, 
                                         admin_tenant_id: str,
                                         report_type: str) -> Optional[Dict[str, Any]]:
        """Generate cross-tenant report (admin only)"""
        try:
            logger.info(f"🌐 Generating cross-tenant {report_type} report")
            
            # Check if admin tenant
            admin_tenant = self.tenants.get(admin_tenant_id)
            if not admin_tenant or admin_tenant.role != TenantRole.ADMIN:
                logger.error(f"❌ Tenant {admin_tenant_id} is not an admin")
                return None
            
            # Check cross-tenant analytics permission
            if not await self._check_permission(admin_tenant, 'cross_tenant_analytics'):
                logger.error(f"❌ Tenant {admin_tenant_id} lacks cross-tenant analytics permission")
                return None
            
            # Aggregate data across all tenants
            aggregated_data = await self._aggregate_tenant_data(report_type)
            
            # Create cross-tenant report
            report = {
                'report_type': f'cross_tenant_{report_type}',
                'generated_at': datetime.utcnow().isoformat(),
                'admin_tenant_id': admin_tenant_id,
                'tenant_count': len(self.tenants),
                'data': aggregated_data
            }
            
            # Log audit event
            await self._log_audit_event(
                admin_tenant_id, "cross_tenant_report_generated", 
                f"Generated cross-tenant {report_type} report"
            )
            
            logger.info("✅ Cross-tenant report generated successfully")
            return report
            
        except Exception as e:
            logger.error(f"❌ Failed to generate cross-tenant report: {e}")
            return None
    
    async def _aggregate_tenant_data(self, report_type: str) -> Dict[str, Any]:
        """Aggregate data across all tenants"""
        try:
            aggregated = {
                'total_tenants': len(self.tenants),
                'total_clusters': 0,
                'total_reports': 0,
                'tenant_summaries': []
            }
            
            for tenant_id, tenant in self.tenants.items():
                tenant_summary = {
                    'tenant_id': tenant_id,
                    'tenant_name': tenant.name,
                    'role': tenant.role.value,
                    'cluster_count': len(tenant.clusters),
                    'report_count': len(self.tenant_reports.get(tenant_id, []))
                }
                
                aggregated['tenant_summaries'].append(tenant_summary)
                aggregated['total_clusters'] += len(tenant.clusters)
                aggregated['total_reports'] += len(self.tenant_reports.get(tenant_id, []))
            
            return aggregated
            
        except Exception as e:
            logger.error(f"❌ Failed to aggregate tenant data: {e}")
            return {}
    
    async def get_tenant_reports(self, 
                               tenant_id: str,
                               report_type: Optional[str] = None,
                               limit: int = 10) -> List[TenantReport]:
        """Get reports for a specific tenant"""
        try:
            logger.info(f"📋 Getting reports for tenant {tenant_id}")
            
            if tenant_id not in self.tenant_reports:
                return []
            
            reports = self.tenant_reports[tenant_id]
            
            # Filter by report type if specified
            if report_type:
                reports = [r for r in reports if r.report_type == report_type]
            
            # Sort by generation time (newest first)
            reports.sort(key=lambda x: x.generated_at, reverse=True)
            
            # Apply limit
            reports = reports[:limit]
            
            logger.info(f"✅ Retrieved {len(reports)} reports for tenant {tenant_id}")
            return reports
            
        except Exception as e:
            logger.error(f"❌ Failed to get tenant reports: {e}")
            return []
    
    async def update_tenant_permissions(self, 
                                      tenant_id: str,
                                      permissions: Dict[str, Any]) -> bool:
        """Update tenant permissions"""
        try:
            logger.info(f"🔐 Updating permissions for tenant {tenant_id}")
            
            if tenant_id not in self.tenants:
                logger.error(f"❌ Tenant {tenant_id} not found")
                return False
            
            # Update permissions
            self.tenants[tenant_id].permissions.update(permissions)
            
            # Log audit event
            await self._log_audit_event(
                tenant_id, "permissions_updated", 
                f"Updated permissions: {list(permissions.keys())}"
            )
            
            logger.info(f"✅ Permissions updated for tenant {tenant_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update tenant permissions: {e}")
            return False
    
    async def add_cluster_to_tenant(self, 
                                  tenant_id: str,
                                  cluster_id: str) -> bool:
        """Add a cluster to a tenant"""
        try:
            logger.info(f"➕ Adding cluster {cluster_id} to tenant {tenant_id}")
            
            if tenant_id not in self.tenants:
                logger.error(f"❌ Tenant {tenant_id} not found")
                return False
            
            if cluster_id in self.tenants[tenant_id].clusters:
                logger.warning(f"⚠️ Cluster {cluster_id} already belongs to tenant {tenant_id}")
                return True
            
            # Add cluster
            self.tenants[tenant_id].clusters.append(cluster_id)
            
            # Log audit event
            await self._log_audit_event(
                tenant_id, "cluster_added", 
                f"Added cluster {cluster_id} to tenant"
            )
            
            logger.info(f"✅ Cluster {cluster_id} added to tenant {tenant_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add cluster to tenant: {e}")
            return False
    
    async def remove_cluster_from_tenant(self, 
                                       tenant_id: str,
                                       cluster_id: str) -> bool:
        """Remove a cluster from a tenant"""
        try:
            logger.info(f"➖ Removing cluster {cluster_id} from tenant {tenant_id}")
            
            if tenant_id not in self.tenants:
                logger.error(f"❌ Tenant {tenant_id} not found")
                return False
            
            if cluster_id not in self.tenants[tenant_id].clusters:
                logger.warning(f"⚠️ Cluster {cluster_id} does not belong to tenant {tenant_id}")
                return True
            
            # Remove cluster
            self.tenants[tenant_id].clusters.remove(cluster_id)
            
            # Log audit event
            await self._log_audit_event(
                tenant_id, "cluster_removed", 
                f"Removed cluster {cluster_id} from tenant"
            )
            
            logger.info(f"✅ Cluster {cluster_id} removed from tenant {tenant_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to remove cluster from tenant: {e}")
            return False
    
    async def _log_audit_event(self, 
                              tenant_id: str,
                              event_type: str,
                              description: str) -> None:
        """Log an audit event"""
        try:
            audit_event = {
                'timestamp': datetime.utcnow().isoformat(),
                'tenant_id': tenant_id,
                'event_type': event_type,
                'description': description
            }
            
            self.audit_log.append(audit_event)
            
        except Exception as e:
            logger.error(f"❌ Failed to log audit event: {e}")
    
    async def get_audit_log(self, 
                           tenant_id: Optional[str] = None,
                           event_type: Optional[str] = None,
                           limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit log entries"""
        try:
            logger.info("📋 Getting audit log")
            
            # Filter audit log
            filtered_log = self.audit_log
            
            if tenant_id:
                filtered_log = [entry for entry in filtered_log if entry['tenant_id'] == tenant_id]
            
            if event_type:
                filtered_log = [entry for entry in filtered_log if entry['event_type'] == event_type]
            
            # Sort by timestamp (newest first)
            filtered_log.sort(key=lambda x: x['timestamp'], reverse=True)
            
            # Apply limit
            filtered_log = filtered_log[:limit]
            
            logger.info(f"✅ Retrieved {len(filtered_log)} audit log entries")
            return filtered_log
            
        except Exception as e:
            logger.error(f"❌ Failed to get audit log: {e}")
            return []
    
    async def get_tenant_summary(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get summary information for a tenant"""
        try:
            logger.info(f"📊 Getting summary for tenant {tenant_id}")
            
            if tenant_id not in self.tenants:
                logger.error(f"❌ Tenant {tenant_id} not found")
                return None
            
            tenant = self.tenants[tenant_id]
            reports = self.tenant_reports.get(tenant_id, [])
            
            summary = {
                'tenant_id': tenant_id,
                'tenant_name': tenant.name,
                'role': tenant.role.value,
                'created_at': tenant.created_at.isoformat(),
                'cluster_count': len(tenant.clusters),
                'report_count': len(reports),
                'permissions': tenant.permissions,
                'clusters': tenant.clusters,
                'recent_reports': [
                    {
                        'report_type': r.report_type,
                        'generated_at': r.generated_at.isoformat()
                    }
                    for r in reports[-5:]  # Last 5 reports
                ]
            }
            
            logger.info(f"✅ Retrieved summary for tenant {tenant_id}")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Failed to get tenant summary: {e}")
            return None 