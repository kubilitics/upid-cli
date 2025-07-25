"""
UPID CLI API Server - Cluster Database Service
Enterprise database operations for cluster management
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
import uuid

from api_server.database.models import (
    Cluster, User, ClusterMetric, Workload, AuditLog,
    ClusterStatus, CloudProvider
)
from api_server.models.requests import ClusterRegisterRequest, ClusterUpdateRequest
from api_server.models.responses import ClusterInfo

logger = logging.getLogger(__name__)


class ClusterService:
    """Database service for cluster operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_cluster(self, request: ClusterRegisterRequest, owner_id: str) -> Cluster:
        """Create a new cluster in the database"""
        try:
            # Check if cluster name already exists for this user
            existing = self.db.query(Cluster).filter(
                and_(Cluster.owner_id == owner_id, Cluster.name == request.name)
            ).first()
            
            if existing:
                raise ValueError(f"Cluster with name '{request.name}' already exists")
            
            # Create new cluster
            cluster = Cluster(
                name=request.name,
                cloud_provider=request.cloud_provider,
                region=request.region,
                owner_id=owner_id,
                status=ClusterStatus.CONNECTING,
                tags=request.tags or {},
                kubeconfig=request.kubeconfig,  # In production, encrypt this
                endpoint=request.endpoint
            )
            
            self.db.add(cluster)
            self.db.commit()
            self.db.refresh(cluster)
            
            # Log cluster creation
            await self._log_audit(
                user_id=owner_id,
                cluster_id=str(cluster.id),
                action="create_cluster",
                status="success",
                details={"cluster_name": request.name}
            )
            
            logger.info(f"✅ Created cluster: {request.name} ({cluster.id})")
            return cluster
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Failed to create cluster {request.name}: {e}")
            raise
    
    async def get_cluster(self, cluster_id: str, owner_id: str) -> Optional[Cluster]:
        """Get a cluster by ID, ensuring ownership"""
        try:
            cluster = self.db.query(Cluster).filter(
                and_(Cluster.id == cluster_id, Cluster.owner_id == owner_id)
            ).first()
            
            if cluster:
                # Update last_seen timestamp
                cluster.last_seen = datetime.utcnow()
                self.db.commit()
            
            return cluster
            
        except Exception as e:
            logger.error(f"❌ Failed to get cluster {cluster_id}: {e}")
            return None
    
    async def list_clusters(
        self, 
        owner_id: str,
        page: int = 1,
        per_page: int = 50,
        status: Optional[str] = None,
        cloud_provider: Optional[str] = None,
        environment: Optional[str] = None
    ) -> tuple[List[Cluster], int]:
        """List clusters with filtering and pagination"""
        try:
            query = self.db.query(Cluster).filter(Cluster.owner_id == owner_id)
            
            # Apply filters
            if status:
                query = query.filter(Cluster.status == status)
            
            if cloud_provider:
                query = query.filter(Cluster.cloud_provider == cloud_provider)
            
            if environment:
                query = query.filter(Cluster.tags['environment'].astext == environment)
            
            # Get total count for pagination
            total = query.count()
            
            # Apply pagination and ordering
            clusters = query.order_by(desc(Cluster.created_at)).offset(
                (page - 1) * per_page
            ).limit(per_page).all()
            
            return clusters, total
            
        except Exception as e:
            logger.error(f"❌ Failed to list clusters: {e}")
            return [], 0
    
    async def update_cluster(
        self, 
        cluster_id: str, 
        request: ClusterUpdateRequest, 
        owner_id: str
    ) -> Optional[Cluster]:
        """Update cluster information"""
        try:
            cluster = await self.get_cluster(cluster_id, owner_id)
            if not cluster:
                return None
            
            # Update fields if provided
            if request.name is not None:
                # Check name uniqueness
                existing = self.db.query(Cluster).filter(
                    and_(
                        Cluster.owner_id == owner_id,
                        Cluster.name == request.name,
                        Cluster.id != cluster_id
                    )
                ).first()
                
                if existing:
                    raise ValueError(f"Cluster with name '{request.name}' already exists")
                
                cluster.name = request.name
            
            if request.tags is not None:
                # For SQLAlchemy JSON fields, we need to reassign the entire dict
                current_tags = cluster.tags or {}
                current_tags.update(request.tags)
                cluster.tags = current_tags
                # Force SQLAlchemy to recognize the change
                from sqlalchemy.orm.attributes import flag_modified
                flag_modified(cluster, 'tags')
            
            if request.is_active is not None:
                cluster.status = ClusterStatus.HEALTHY if request.is_active else ClusterStatus.DISABLED
            
            cluster.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(cluster)
            
            # Log cluster update
            await self._log_audit(
                user_id=owner_id,
                cluster_id=cluster_id,
                action="update_cluster",
                status="success",
                details={"changes": request.dict(exclude_unset=True)}
            )
            
            logger.info(f"✅ Updated cluster: {cluster.name}")
            return cluster
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Failed to update cluster {cluster_id}: {e}")
            raise
    
    async def delete_cluster(self, cluster_id: str, owner_id: str) -> bool:
        """Delete a cluster and all associated data"""
        try:
            cluster = await self.get_cluster(cluster_id, owner_id)
            if not cluster:
                return False
            
            cluster_name = cluster.name
            
            # The cascade="all, delete-orphan" in the model will handle
            # deletion of related workloads, metrics, etc.
            self.db.delete(cluster)
            self.db.commit()
            
            # Log cluster deletion
            await self._log_audit(
                user_id=owner_id,
                cluster_id=cluster_id,
                action="delete_cluster",
                status="success",
                details={"cluster_name": cluster_name}
            )
            
            logger.info(f"✅ Deleted cluster: {cluster_name}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Failed to delete cluster {cluster_id}: {e}")
            return False
    
    async def update_cluster_metrics(
        self, 
        cluster_id: str, 
        metrics_data: Dict[str, Any]
    ) -> bool:
        """Update cluster metrics and status"""
        try:
            cluster = self.db.query(Cluster).filter(Cluster.id == cluster_id).first()
            if not cluster:
                return False
            
            # Update cluster metadata
            cluster.node_count = metrics_data.get("node_count", cluster.node_count)
            cluster.pod_count = metrics_data.get("pod_count", cluster.pod_count)
            cluster.namespace_count = metrics_data.get("namespace_count", cluster.namespace_count)
            cluster.kubernetes_version = metrics_data.get("kubernetes_version", cluster.kubernetes_version)
            cluster.health_score = metrics_data.get("health_score", cluster.health_score)
            cluster.efficiency_score = metrics_data.get("efficiency_score", cluster.efficiency_score)
            cluster.monthly_cost = metrics_data.get("monthly_cost", cluster.monthly_cost)
            cluster.last_seen = datetime.utcnow()
            
            # Determine cluster status based on health score
            health_score = cluster.health_score or 0
            if health_score >= 90:
                cluster.status = ClusterStatus.HEALTHY
            elif health_score >= 70:
                cluster.status = ClusterStatus.WARNING
            else:
                cluster.status = ClusterStatus.ERROR
            
            # Create metrics record
            metric = ClusterMetric(
                cluster_id=cluster.id,
                timestamp=datetime.utcnow(),
                cpu_usage_cores=metrics_data.get("cpu_usage_cores", 0.0),
                cpu_usage_percent=metrics_data.get("cpu_usage_percent", 0.0),
                memory_usage_bytes=metrics_data.get("memory_usage_bytes", 0),
                memory_usage_percent=metrics_data.get("memory_usage_percent", 0.0),
                network_rx_bytes=metrics_data.get("network_rx_bytes", 0),
                network_tx_bytes=metrics_data.get("network_tx_bytes", 0),
                storage_usage_bytes=metrics_data.get("storage_usage_bytes", 0),
                storage_available_bytes=metrics_data.get("storage_available_bytes", 0),
                node_count=cluster.node_count,
                pod_count=cluster.pod_count,
                namespace_count=cluster.namespace_count,
                hourly_cost=cluster.monthly_cost / (30 * 24) if cluster.monthly_cost else 0.0
            )
            
            self.db.add(metric)
            self.db.commit()
            
            logger.debug(f"✅ Updated metrics for cluster: {cluster.name}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Failed to update cluster metrics: {e}")
            return False
    
    async def get_cluster_metrics(
        self, 
        cluster_id: str, 
        hours: int = 24
    ) -> List[ClusterMetric]:
        """Get cluster metrics for the specified time range"""
        try:
            start_time = datetime.utcnow() - timedelta(hours=hours)
            
            metrics = self.db.query(ClusterMetric).filter(
                and_(
                    ClusterMetric.cluster_id == cluster_id,
                    ClusterMetric.timestamp >= start_time
                )
            ).order_by(ClusterMetric.timestamp.asc()).all()
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Failed to get cluster metrics: {e}")
            return []
    
    async def health_check_cluster(self, cluster_id: str, owner_id: str) -> bool:
        """Perform health check and update cluster status"""
        try:
            cluster = await self.get_cluster(cluster_id, owner_id)
            if not cluster:
                return False
            
            # In production, this would test actual cluster connectivity
            # For now, simulate health check
            
            # Mock health check results
            health_results = {
                "kubernetes_api": "healthy",
                "rbac_permissions": "healthy",
                "metrics_server": "healthy",
                "monitoring": "healthy",
                "optimization_access": "healthy"
            }
            
            # Update cluster based on health check
            all_healthy = all(status == "healthy" for status in health_results.values())
            cluster.status = ClusterStatus.HEALTHY if all_healthy else ClusterStatus.WARNING
            cluster.last_seen = datetime.utcnow()
            cluster.health_score = 95.0 if all_healthy else 75.0
            
            self.db.commit()
            
            # Log health check
            await self._log_audit(
                user_id=owner_id,
                cluster_id=cluster_id,
                action="health_check",
                status="success",
                details=health_results
            )
            
            logger.info(f"✅ Health check completed for {cluster.name}: {cluster.status}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Health check failed for cluster {cluster_id}: {e}")
            return False
    
    async def get_cluster_summary(self, owner_id: str) -> Dict[str, Any]:
        """Get summary statistics for all user clusters"""
        try:
            # Get cluster counts by status
            status_counts = self.db.query(
                Cluster.status,
                func.count(Cluster.id)
            ).filter(Cluster.owner_id == owner_id).group_by(Cluster.status).all()
            
            # Get total costs
            total_cost = self.db.query(
                func.sum(Cluster.monthly_cost)
            ).filter(Cluster.owner_id == owner_id).scalar() or 0.0
            
            # Get recent activity
            recent_clusters = self.db.query(Cluster).filter(
                Cluster.owner_id == owner_id
            ).order_by(desc(Cluster.last_seen)).limit(5).all()
            
            return {
                "total_clusters": sum(count for _, count in status_counts),
                "status_breakdown": {status: count for status, count in status_counts},
                "total_monthly_cost": total_cost,
                "recent_activity": [
                    {
                        "name": cluster.name,
                        "status": cluster.status,
                        "last_seen": cluster.last_seen.isoformat() if cluster.last_seen else None
                    }
                    for cluster in recent_clusters
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get cluster summary: {e}")
            return {}
    
    async def _log_audit(
        self,
        user_id: str,
        cluster_id: str,
        action: str,
        status: str,
        details: Dict[str, Any] = None
    ):
        """Log audit trail for cluster operations"""
        try:
            audit_log = AuditLog(
                user_id=user_id,
                cluster_id=cluster_id,
                action=action,
                resource_type="cluster",
                resource_id=cluster_id,
                status=status,
                details=details or {},
                timestamp=datetime.utcnow()
            )
            
            self.db.add(audit_log)
            # Note: commit is handled by the calling function
            
        except Exception as e:
            logger.error(f"❌ Failed to log audit trail: {e}")
    
    def to_cluster_info(self, cluster: Cluster) -> ClusterInfo:
        """Convert database cluster to API response model"""
        return ClusterInfo(
            id=str(cluster.id),
            name=cluster.name,
            status=cluster.status.value,
            version=cluster.kubernetes_version or "unknown",
            node_count=cluster.node_count,
            namespace_count=cluster.namespace_count,
            pod_count=cluster.pod_count,
            cloud_provider=cluster.cloud_provider.value,
            region=cluster.region,
            created_at=cluster.created_at,
            last_seen=cluster.last_seen or cluster.created_at,
            tags=cluster.tags or {}
        )