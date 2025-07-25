"""
UPID CLI API Server - User Database Service
Enterprise user management and authentication database operations
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
import uuid

from api_server.database.models import User, AuditLog, UserRole
from api_server.core.auth import hash_password, verify_password

logger = logging.getLogger(__name__)


class UserService:
    """Database service for user operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_user(
        self,
        username: str,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        role: UserRole = UserRole.USER,
        is_superuser: bool = False
    ) -> User:
        """Create a new user account"""
        try:
            # Check if username or email already exists
            existing = self.db.query(User).filter(
                or_(User.username == username, User.email == email)
            ).first()
            
            if existing:
                if existing.username == username:
                    raise ValueError(f"Username '{username}' already exists")
                else:
                    raise ValueError(f"Email '{email}' already exists")
            
            # Create new user
            user = User(
                username=username,
                email=email,
                hashed_password=hash_password(password),
                full_name=full_name,
                role=role,
                is_superuser=is_superuser,
                is_active=True,
                created_at=datetime.utcnow(),
                preferences={}
            )
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            # Log user creation
            await self._log_audit(
                user_id=str(user.id),
                action="create_user",
                status="success",
                details={"username": username, "email": email, "role": role.value}
            )
            
            logger.info(f"✅ Created user: {username} ({user.id})")
            return user
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Failed to create user {username}: {e}")
            raise
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username/password"""
        try:
            user = self.db.query(User).filter(
                or_(User.username == username, User.email == username)
            ).first()
            
            if not user:
                await self._log_audit(
                    user_id=None,
                    action="login_attempt",
                    status="failure",
                    details={"username": username, "error": "user_not_found"}
                )
                return None
            
            if not user.is_active:
                await self._log_audit(
                    user_id=str(user.id),
                    action="login_attempt",
                    status="failure",
                    details={"username": username, "error": "user_inactive"}
                )
                return None
            
            if not verify_password(password, user.hashed_password):
                await self._log_audit(
                    user_id=str(user.id),
                    action="login_attempt",
                    status="failure",
                    details={"username": username, "error": "invalid_password"}
                )
                return None
            
            # Update last login
            user.last_login = datetime.utcnow()
            self.db.commit()
            
            # Log successful login
            await self._log_audit(
                user_id=str(user.id),
                action="login",
                status="success",
                details={"username": username}
            )
            
            logger.info(f"✅ User authenticated: {username}")
            return user
            
        except Exception as e:
            logger.error(f"❌ Authentication failed for {username}: {e}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            return user
        except Exception as e:
            logger.error(f"❌ Failed to get user {user_id}: {e}")
            return None
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            user = self.db.query(User).filter(User.username == username).first()
            return user
        except Exception as e:
            logger.error(f"❌ Failed to get user {username}: {e}")
            return None
    
    async def update_user(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> Optional[User]:
        """Update user information"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return None
            
            # Track changes for audit
            changes = {}
            
            # Update allowed fields
            if "full_name" in updates:
                changes["full_name"] = {"old": user.full_name, "new": updates["full_name"]}
                user.full_name = updates["full_name"]
            
            if "email" in updates:
                # Check email uniqueness
                existing = self.db.query(User).filter(
                    and_(User.email == updates["email"], User.id != user_id)
                ).first()
                if existing:
                    raise ValueError(f"Email '{updates['email']}' already exists")
                
                changes["email"] = {"old": user.email, "new": updates["email"]}
                user.email = updates["email"]
            
            if "is_active" in updates:
                changes["is_active"] = {"old": user.is_active, "new": updates["is_active"]}
                user.is_active = updates["is_active"]
            
            if "preferences" in updates:
                user.preferences.update(updates["preferences"])
                changes["preferences"] = "updated"
            
            if "password" in updates:
                user.hashed_password = hash_password(updates["password"])
                changes["password"] = "changed"
            
            user.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(user)
            
            # Log user update
            await self._log_audit(
                user_id=user_id,
                action="update_user",
                status="success",
                details={"changes": changes}
            )
            
            logger.info(f"✅ Updated user: {user.username}")
            return user
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Failed to update user {user_id}: {e}")
            raise
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user account"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return False
            
            username = user.username
            
            # In production, you might want to soft delete or transfer ownership
            # of clusters before deleting the user
            self.db.delete(user)
            self.db.commit()
            
            # Log user deletion
            await self._log_audit(
                user_id=user_id,
                action="delete_user",
                status="success",
                details={"username": username}
            )
            
            logger.info(f"✅ Deleted user: {username}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Failed to delete user {user_id}: {e}")
            return False
    
    async def list_users(
        self,
        page: int = 1,
        per_page: int = 50,
        role: Optional[UserRole] = None,
        active_only: bool = True
    ) -> tuple[List[User], int]:
        """List users with filtering and pagination"""
        try:
            query = self.db.query(User)
            
            # Apply filters
            if active_only:
                query = query.filter(User.is_active == True)
            
            if role:
                query = query.filter(User.role == role)
            
            # Get total count
            total = query.count()
            
            # Apply pagination and ordering
            users = query.order_by(desc(User.created_at)).offset(
                (page - 1) * per_page
            ).limit(per_page).all()
            
            return users, total
            
        except Exception as e:
            logger.error(f"❌ Failed to list users: {e}")
            return [], 0
    
    async def get_user_permissions(self, user_id: str) -> List[str]:
        """Get user permissions based on role"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return []
            
            # Define role-based permissions
            permissions = ["user"]  # Base permission for all users
            
            if user.role == UserRole.ADMIN or user.is_superuser:
                permissions.extend([
                    "admin",
                    "manage_users",
                    "manage_clusters",
                    "view_all_clusters",
                    "run_optimizations",
                    "generate_reports",
                    "view_audit_logs",
                    "manage_system_config"
                ])
            elif user.role == UserRole.USER:
                permissions.extend([
                    "manage_own_clusters",
                    "run_optimizations",
                    "generate_reports"
                ])
            elif user.role == UserRole.VIEWER:
                permissions.extend([
                    "view_own_clusters",
                    "generate_reports"
                ])
            
            return permissions
            
        except Exception as e:
            logger.error(f"❌ Failed to get user permissions: {e}")
            return []
    
    async def update_user_preferences(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ) -> bool:
        """Update user preferences"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return False
            
            # Merge with existing preferences
            if user.preferences:
                user.preferences.update(preferences)
            else:
                user.preferences = preferences
            
            user.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.debug(f"✅ Updated preferences for user: {user.username}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Failed to update user preferences: {e}")
            return False
    
    async def get_user_activity(
        self,
        user_id: str,
        hours: int = 24
    ) -> List[AuditLog]:
        """Get recent user activity"""
        try:
            start_time = datetime.utcnow() - timedelta(hours=hours)
            
            activity = self.db.query(AuditLog).filter(
                and_(
                    AuditLog.user_id == user_id,
                    AuditLog.timestamp >= start_time
                )
            ).order_by(desc(AuditLog.timestamp)).limit(100).all()
            
            return activity
            
        except Exception as e:
            logger.error(f"❌ Failed to get user activity: {e}")
            return []
    
    async def initialize_default_users(self):
        """Initialize default users for development/demo"""
        try:
            # Check if users already exist
            existing_users = self.db.query(User).count()
            if existing_users > 0:
                logger.info("Users already exist, skipping initialization")
                return
            
            # Create admin user
            admin_user = await self.create_user(
                username="admin",
                email="admin@upid.io",
                password="admin123",
                full_name="UPID Administrator",
                role=UserRole.ADMIN,
                is_superuser=True
            )
            
            # Create demo user
            demo_user = await self.create_user(
                username="demo",
                email="demo@upid.io",
                password="demo123",
                full_name="Demo User",
                role=UserRole.USER,
                is_superuser=False
            )
            
            logger.info("✅ Default users initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize default users: {e}")
    
    async def _log_audit(
        self,
        user_id: Optional[str],
        action: str,
        status: str,
        details: Dict[str, Any] = None
    ):
        """Log audit trail for user operations"""
        try:
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                resource_type="user",
                resource_id=user_id,
                status=status,
                details=details or {},
                timestamp=datetime.utcnow()
            )
            
            self.db.add(audit_log)
            # Note: commit is handled by the calling function
            
        except Exception as e:
            logger.error(f"❌ Failed to log audit trail: {e}")
    
    def to_user_dict(self, user: User, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert user model to dictionary for API responses"""
        user_dict = {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "preferences": user.preferences or {}
        }
        
        if not include_sensitive:
            # Remove sensitive information
            user_dict.pop("email", None)
        
        return user_dict