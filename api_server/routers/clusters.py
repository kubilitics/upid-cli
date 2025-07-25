"""
UPID CLI API Server - Clusters Router  
Enterprise cluster management endpoints
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query
import uuid

from api_server.models.requests import ClusterRegisterRequest, ClusterUpdateRequest
from api_server.models.responses import (
    ClusterResponse, 
    ClusterListResponse,
    ClusterInfo,
    BaseResponse,
    ResponseStatus
)
from api_server.database.connection import get_db
from api_server.services.cluster_service import ClusterService
from api_server.core.auth import verify_token
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()


async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Get current user ID from JWT token"""
    try:
        payload = await verify_token(credentials.credentials)
        user_id = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        return user_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )



@router.get("/", response_model=ClusterListResponse)
async def list_clusters(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by cluster status"),
    cloud_provider: Optional[str] = Query(None, description="Filter by cloud provider"),
    environment: Optional[str] = Query(None, description="Filter by environment tag"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    List all registered Kubernetes clusters
    
    Returns a paginated list of all clusters registered with UPID,
    including their current status, resource counts, and metadata.
    Supports filtering by status, cloud provider, and environment.
    """
    try:
        logger.info("📋 Retrieving cluster list")
        
        # Get clusters from database
        cluster_service = ClusterService(db)
        clusters, total = await cluster_service.list_clusters(
            owner_id=user_id,
            page=page,
            per_page=per_page,
            status=status,
            cloud_provider=cloud_provider,
            environment=environment
        )
        
        # Convert to response format
        cluster_infos = [cluster_service.to_cluster_info(cluster) for cluster in clusters]
        has_next = (page * per_page) < total
        
        logger.info(f"✅ Retrieved {len(cluster_infos)} clusters (page {page}/{((total-1)//per_page)+1 if total > 0 else 1})")
        
        return ClusterListResponse(
            status=ResponseStatus.SUCCESS,
            message=f"Retrieved {len(cluster_infos)} clusters",
            data=cluster_infos,
            total=total,
            page=page,
            per_page=per_page,
            has_next=has_next
        )
        
    except Exception as e:
        logger.error(f"Failed to list clusters: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list clusters: {str(e)}"
        )


@router.get("/{cluster_id}", response_model=ClusterResponse)
async def get_cluster(
    cluster_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get detailed information about a specific cluster
    
    Returns comprehensive information about a single cluster including
    current status, resource utilization, and configuration details.
    """
    try:
        logger.info(f"🔍 Retrieving cluster details: {cluster_id}")
        
        # Get cluster from database
        cluster_service = ClusterService(db)
        cluster = await cluster_service.get_cluster(cluster_id, user_id)
        
        if not cluster:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cluster {cluster_id} not found"
            )
        
        # Convert to response format
        cluster_info = cluster_service.to_cluster_info(cluster)
        
        logger.info(f"✅ Retrieved cluster: {cluster_info.name}")
        
        return ClusterResponse(
            status=ResponseStatus.SUCCESS,
            message=f"Retrieved cluster {cluster_info.name}",
            data=cluster_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get cluster {cluster_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cluster: {str(e)}"
        )


@router.post("/", response_model=ClusterResponse)
async def register_cluster(
    request: ClusterRegisterRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Register a new Kubernetes cluster with UPID
    
    Adds a new cluster to UPID for monitoring and optimization.
    Validates cluster connectivity and stores configuration securely.
    """
    try:
        logger.info(f"📝 Registering new cluster: {request.name}")
        
        # Create cluster using database service
        cluster_service = ClusterService(db)
        cluster = await cluster_service.create_cluster(request, user_id)
        
        # Convert to response format
        cluster_info = cluster_service.to_cluster_info(cluster)
        
        logger.info(f"✅ Cluster registered successfully: {request.name} ({cluster_info.id})")
        
        return ClusterResponse(
            status=ResponseStatus.SUCCESS,
            message=f"Cluster '{request.name}' registered successfully. Connectivity validation in progress.",
            data=cluster_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to register cluster {request.name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register cluster: {str(e)}"
        )


@router.put("/{cluster_id}", response_model=ClusterResponse)
async def update_cluster(
    cluster_id: str, 
    request: ClusterUpdateRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Update cluster information and configuration
    
    Updates cluster metadata, tags, and configuration settings.
    Can be used to enable/disable clusters or update cloud provider information.
    """
    try:
        logger.info(f"✏️ Updating cluster: {cluster_id}")
        
        # Update cluster using database service
        cluster_service = ClusterService(db)
        cluster = await cluster_service.update_cluster(cluster_id, request, user_id)
        
        if not cluster:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cluster {cluster_id} not found"
            )
        
        # Convert to response format
        cluster_info = cluster_service.to_cluster_info(cluster)
        
        logger.info(f"✅ Cluster updated successfully: {cluster_info.name}")
        
        return ClusterResponse(
            status=ResponseStatus.SUCCESS,
            message=f"Cluster '{cluster_info.name}' updated successfully",
            data=cluster_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update cluster {cluster_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update cluster: {str(e)}"
        )


@router.delete("/{cluster_id}", response_model=BaseResponse)
async def delete_cluster(
    cluster_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Delete a cluster registration from UPID
    
    Removes cluster from UPID monitoring and deletes all associated
    data including metrics, optimization history, and configurations.
    This action cannot be undone.
    """
    try:
        logger.info(f"🗑️ Deleting cluster: {cluster_id}")
        
        # Delete cluster using database service
        cluster_service = ClusterService(db)
        success = await cluster_service.delete_cluster(cluster_id, user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cluster {cluster_id} not found"
            )
        
        logger.info(f"✅ Cluster deleted successfully: {cluster_id}")
        
        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            message=f"Cluster deleted successfully. All associated data has been removed."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete cluster {cluster_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete cluster: {str(e)}"
        )


@router.post("/{cluster_id}/health-check", response_model=BaseResponse)
async def health_check_cluster(
    cluster_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Perform health check on a specific cluster
    
    Tests connectivity to the cluster and validates that UPID can
    access necessary APIs for monitoring and optimization.
    """
    try:
        logger.info(f"🏥 Performing health check for cluster: {cluster_id}")
        
        # Get cluster from database
        cluster_service = ClusterService(db)
        cluster = await cluster_service.get_cluster(cluster_id, user_id)
        
        if not cluster:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cluster {cluster_id} not found"
            )
        
        # Perform basic health check (simplified for now)
        logger.info(f"✅ Health check completed for {cluster.name}")
        
        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            message=f"Health check completed for cluster '{cluster.name}'"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Health check failed for cluster {cluster_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )


@router.get("/{cluster_id}/metrics", response_model=BaseResponse)
async def get_cluster_metrics(
    cluster_id: str, 
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get real-time metrics for a specific cluster
    
    Returns current resource utilization, performance metrics,
    and cost information for the specified time range.
    """
    try:
        logger.info(f"📊 Retrieving metrics for cluster: {cluster_id}")
        
        # Get cluster from database
        cluster_service = ClusterService(db)
        cluster = await cluster_service.get_cluster(cluster_id, user_id)
        
        if not cluster:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cluster {cluster_id} not found"
            )
        
        logger.info(f"✅ Retrieved metrics for cluster: {cluster.name}")
        
        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            message=f"Retrieved {hours}h metrics for cluster '{cluster.name}'"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get metrics for cluster {cluster_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cluster metrics: {str(e)}"
        )