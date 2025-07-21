"""
Storage Integration Module
Handles data persistence for users, analysis results, and audit events
"""

import json
import sqlite3
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class StorageIntegration:
    """Storage integration for UPID CLI"""
    
    def __init__(self, db_path: str = "upid_data.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Users table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id TEXT PRIMARY KEY,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT,
                        password_hash TEXT,
                        organization TEXT,
                        permissions TEXT,
                        created_at TEXT,
                        last_login TEXT,
                        mfa_enabled BOOLEAN DEFAULT FALSE,
                        mfa_secret TEXT,
                        is_active BOOLEAN DEFAULT TRUE,
                        security_level TEXT DEFAULT 'medium'
                    )
                ''')
                
                # Analysis results table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS analysis_results (
                        analysis_id TEXT PRIMARY KEY,
                        cluster_id TEXT,
                        analysis_data TEXT,
                        created_at TEXT,
                        updated_at TEXT
                    )
                ''')
                
                # Audit events table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS audit_events (
                        event_id TEXT PRIMARY KEY,
                        user_id TEXT,
                        action TEXT,
                        resource_type TEXT,
                        resource_id TEXT,
                        timestamp TEXT,
                        ip_address TEXT,
                        user_agent TEXT,
                        success BOOLEAN,
                        details TEXT,
                        security_level TEXT
                    )
                ''')
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
    
    @contextmanager
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
    
    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM users WHERE username = ?",
                    (username,)
                )
                row = cursor.fetchone()
                
                if row:
                    columns = [description[0] for description in cursor.description]
                    user_data = dict(zip(columns, row))
                    
                    # Parse permissions
                    if user_data.get('permissions'):
                        user_data['permissions'] = json.loads(user_data['permissions'])
                    
                    return user_data
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting user by username: {e}")
            return None
    
    async def update_user_last_login(self, user_id: str):
        """Update user's last login time"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET last_login = ? WHERE user_id = ?",
                    (datetime.now(timezone.utc).isoformat(), user_id)
                )
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error updating user last login: {e}")
    
    async def get_user_mfa_secret(self, user_id: str) -> Optional[str]:
        """Get user's MFA secret"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT mfa_secret FROM users WHERE user_id = ?",
                    (user_id,)
                )
                row = cursor.fetchone()
                
                return row[0] if row else None
                
        except Exception as e:
            logger.error(f"Error getting user MFA secret: {e}")
            return None
    
    async def log_audit_event(self, event_data: Dict[str, Any]):
        """Log audit event"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO audit_events 
                    (event_id, user_id, action, resource_type, resource_id, 
                     timestamp, ip_address, user_agent, success, details, security_level)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event_data['event_id'],
                    event_data['user_id'],
                    event_data['action'],
                    event_data['resource_type'],
                    event_data['resource_id'],
                    event_data['timestamp'],
                    event_data['ip_address'],
                    event_data['user_agent'],
                    event_data['success'],
                    json.dumps(event_data['details']),
                    event_data['security_level']
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error logging audit event: {e}")
    
    async def get_analysis_result(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get analysis result by ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT analysis_data FROM analysis_results WHERE analysis_id = ?",
                    (analysis_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    return json.loads(row[0])
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting analysis result: {e}")
            return None
    
    async def store_analysis_result(self, analysis_id: str, analysis_data: Dict[str, Any]):
        """Store analysis result"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO analysis_results 
                    (analysis_id, cluster_id, analysis_data, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    analysis_id,
                    analysis_data.get('cluster_id', analysis_id),
                    json.dumps(analysis_data),
                    datetime.now(timezone.utc).isoformat(),
                    datetime.now(timezone.utc).isoformat()
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error storing analysis result: {e}")
    
    async def create_default_users(self):
        """Create default users for testing"""
        try:
            from ..core.security import PasswordManager
            
            default_users = [
                {
                    'user_id': 'admin-001',
                    'username': 'admin',
                    'email': 'admin@upid.io',
                    'password_hash': PasswordManager.hash_password('admin123'),
                    'organization': 'upid',
                    'permissions': json.dumps(['read', 'write', 'admin', 'analyze', 'optimize', 'report', 'storage', 'user_management', 'system_config']),
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'last_login': datetime.now(timezone.utc).isoformat(),
                    'mfa_enabled': False,
                    'is_active': True,
                    'security_level': 'high'
                },
                {
                    'user_id': 'user-001',
                    'username': 'user',
                    'email': 'user@upid.io',
                    'password_hash': PasswordManager.hash_password('user123'),
                    'organization': 'upid',
                    'permissions': json.dumps(['read', 'analyze']),
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'last_login': datetime.now(timezone.utc).isoformat(),
                    'mfa_enabled': False,
                    'is_active': True,
                    'security_level': 'medium'
                }
            ]
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                for user in default_users:
                    cursor.execute('''
                        INSERT OR REPLACE INTO users 
                        (user_id, username, email, password_hash, organization, 
                         permissions, created_at, last_login, mfa_enabled, is_active, security_level)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        user['user_id'],
                        user['username'],
                        user['email'],
                        user['password_hash'],
                        user['organization'],
                        user['permissions'],
                        user['created_at'],
                        user['last_login'],
                        user['mfa_enabled'],
                        user['is_active'],
                        user['security_level']
                    ))
                
                conn.commit()
                logger.info("Default users created successfully")
                
        except Exception as e:
            logger.error(f"Error creating default users: {e}") 