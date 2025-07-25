"""
Monitoring & Observability System for UPID CLI
Provides Prometheus metrics, structured logging, and health checks
"""

import os
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import threading
import psutil

# Optional imports with fallbacks
try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False
    structlog = None

try:
    from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST, CollectorRegistry
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    Counter = Gauge = Histogram = None

try:
    from opentelemetry import trace, metrics
    from opentelemetry.trace import Status, StatusCode
    from opentelemetry.metrics import Counter as OTelCounter, Histogram as OTelHistogram
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    trace = metrics = None


@dataclass
class HealthStatus:
    """Health status information"""
    service: str
    status: str  # "healthy", "degraded", "unhealthy"
    timestamp: datetime
    details: Dict[str, Any]
    response_time_ms: float


@dataclass
class SystemMetrics:
    """System-level metrics"""
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_io_bytes: Dict[str, int]
    timestamp: datetime


@dataclass
class ApplicationMetrics:
    """Application-level metrics"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time_ms: float
    active_optimizations: int
    total_cost_savings: float
    timestamp: datetime


class MonitoringSystem:
    """Comprehensive monitoring and observability system"""
    
    def __init__(self, service_name: str = "upid-cli"):
        self.service_name = service_name
        self.start_time = datetime.now()
        
        # Initialize logging
        self._setup_logging()
        
        # Initialize metrics
        self._setup_metrics()
        
        # Initialize tracing (optional)
        self._setup_tracing()
        
        # Health status tracking
        self.health_status = {
            "api_server": HealthStatus("api_server", "healthy", datetime.now(), {}, 0.0),
            "database": HealthStatus("database", "healthy", datetime.now(), {}, 0.0),
            "ml_pipeline": HealthStatus("ml_pipeline", "healthy", datetime.now(), {}, 0.0),
            "optimization_engine": HealthStatus("optimization_engine", "healthy", datetime.now(), {}, 0.0)
        }
        
        # Metrics storage
        self.system_metrics: List[SystemMetrics] = []
        self.application_metrics: List[ApplicationMetrics] = []
        
        # Request tracking
        self.request_counter = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.response_times: List[float] = []
        
        # Start background collection
        self._start_background_collection()
    
    def _setup_logging(self):
        """Setup structured logging"""
        if STRUCTLOG_AVAILABLE:
            structlog.configure(
                processors=[
                    structlog.stdlib.filter_by_level,
                    structlog.stdlib.add_logger_name,
                    structlog.stdlib.add_log_level,
                    structlog.stdlib.PositionalArgumentsFormatter(),
                    structlog.processors.TimeStamper(fmt="iso"),
                    structlog.processors.StackInfoRenderer(),
                    structlog.processors.format_exc_info,
                    structlog.processors.UnicodeDecoder(),
                    structlog.processors.JSONRenderer()
                ],
                context_class=dict,
                logger_factory=structlog.stdlib.LoggerFactory(),
                wrapper_class=structlog.stdlib.BoundLogger,
                cache_logger_on_first_use=True,
            )
            self.logger = structlog.get_logger()
        else:
            # Fallback to standard logging
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            self.logger = logging.getLogger(__name__)
    
    def _setup_metrics(self):
        """Setup Prometheus metrics"""
        if PROMETHEUS_AVAILABLE:
            # Create a custom registry to avoid conflicts
            self.registry = CollectorRegistry()
            
            # Request metrics
            self.request_counter_metric = Counter(
                'upid_cli_requests_total',
                'Total number of requests',
                ['method', 'endpoint', 'status'],
                registry=self.registry
            )
            
            self.request_duration_metric = Histogram(
                'upid_cli_request_duration_seconds',
                'Request duration in seconds',
                ['method', 'endpoint'],
                registry=self.registry
            )
            
            # Optimization metrics
            self.optimization_counter_metric = Counter(
                'upid_cli_optimizations_total',
                'Total number of optimizations',
                ['type', 'status'],
                registry=self.registry
            )
            
            self.cost_savings_metric = Gauge(
                'upid_cli_cost_savings_dollars',
                'Total cost savings in dollars',
                registry=self.registry
            )
            
            # System metrics
            self.cpu_metric = Gauge('upid_cli_system_cpu_percent', 'CPU usage percentage', registry=self.registry)
            self.memory_metric = Gauge('upid_cli_system_memory_percent', 'Memory usage percentage', registry=self.registry)
            self.disk_metric = Gauge('upid_cli_system_disk_percent', 'Disk usage percentage', registry=self.registry)
        else:
            self.logger.warning("Prometheus metrics not available - using internal metrics only")
            self.registry = None
            self.request_counter_metric = None
            self.request_duration_metric = None
            self.optimization_counter_metric = None
            self.cost_savings_metric = None
            self.cpu_metric = None
            self.memory_metric = None
            self.disk_metric = None
    
    def _setup_tracing(self):
        """Setup OpenTelemetry tracing"""
        if OPENTELEMETRY_AVAILABLE:
            # Initialize tracer
            self.tracer = trace.get_tracer(__name__)
            
            # Initialize meters
            self.meter = metrics.get_meter(__name__)
            
            # Create metrics
            self.request_counter = self.meter.create_counter(
                name="upid_cli.requests",
                description="Number of requests"
            )
            
            self.request_duration = self.meter.create_histogram(
                name="upid_cli.request.duration",
                description="Request duration"
            )
        else:
            self.logger.warning("OpenTelemetry tracing not available - using internal tracing only")
            self.tracer = None
            self.meter = None
            self.request_counter = None
            self.request_duration = None
    
    def _start_background_collection(self):
        """Start background metrics collection"""
        def collect_metrics():
            while True:
                try:
                    # Collect system metrics
                    self._collect_system_metrics()
                    
                    # Collect application metrics
                    self._collect_application_metrics()
                    
                    # Cleanup old metrics (keep last 24 hours)
                    self._cleanup_old_metrics()
                    
                    time.sleep(60)  # Collect every minute
                except Exception as e:
                    self.logger.error(f"Error in background metrics collection: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=collect_metrics, daemon=True)
        thread.start()
    
    def _collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            metrics = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_usage_percent=disk.percent,
                network_io_bytes={
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv
                },
                timestamp=datetime.now()
            )
            
            self.system_metrics.append(metrics)
            
            # Update Prometheus metrics if available
            if PROMETHEUS_AVAILABLE:
                self.cpu_metric.set(cpu_percent)
                self.memory_metric.set(memory.percent)
                self.disk_metric.set(disk.percent)
            
            self.logger.debug("System metrics collected", 
                            cpu_percent=cpu_percent,
                            memory_percent=memory.percent,
                            disk_percent=disk.percent)
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
    
    def _collect_application_metrics(self):
        """Collect application-level metrics"""
        try:
            avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
            
            metrics = ApplicationMetrics(
                total_requests=self.request_counter,
                successful_requests=self.successful_requests,
                failed_requests=self.failed_requests,
                average_response_time_ms=avg_response_time,
                active_optimizations=0,  # TODO: Get from optimization engine
                total_cost_savings=0.0,  # TODO: Get from cost manager
                timestamp=datetime.now()
            )
            
            self.application_metrics.append(metrics)
            
            self.logger.debug("Application metrics collected",
                            total_requests=self.request_counter,
                            success_rate=self.successful_requests / max(self.request_counter, 1),
                            avg_response_time=avg_response_time)
            
        except Exception as e:
            self.logger.error(f"Error collecting application metrics: {e}")
    
    def _cleanup_old_metrics(self):
        """Cleanup metrics older than 24 hours"""
        cutoff = datetime.now() - timedelta(hours=24)
        
        self.system_metrics = [m for m in self.system_metrics if m.timestamp > cutoff]
        self.application_metrics = [m for m in self.application_metrics if m.timestamp > cutoff]
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration_ms: float):
        """Record a request for metrics and tracing"""
        self.request_counter += 1
        self.response_times.append(duration_ms)
        
        if 200 <= status_code < 400:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        
        # Update Prometheus metrics
        if PROMETHEUS_AVAILABLE:
            self.request_counter_metric.labels(
                method=method,
                endpoint=endpoint,
                status=str(status_code)
            ).inc()
            
            self.request_duration_metric.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration_ms / 1000.0)
        
        # Update OpenTelemetry metrics
        if OPENTELEMETRY_AVAILABLE:
            self.request_counter.add(1, {"method": method, "endpoint": endpoint})
            self.request_duration.record(duration_ms / 1000.0, {"method": method, "endpoint": endpoint})
        
        self.logger.info("Request recorded",
                        method=method,
                        endpoint=endpoint,
                        status_code=status_code,
                        duration_ms=duration_ms)
    
    def record_error(self, error_type: str, error_message: str, context: Dict[str, Any] = None):
        """Record an error for monitoring"""
        self.logger.error("Error recorded",
                         error_type=error_type,
                         error_message=error_message,
                         context=context or {})
    
    def record_optimization(self, optimization_type: str, status: str, cost_savings: float = 0.0):
        """Record an optimization event"""
        if PROMETHEUS_AVAILABLE:
            self.optimization_counter_metric.labels(
                type=optimization_type,
                status=status
            ).inc()
            
            if cost_savings > 0:
                self.cost_savings_metric.inc(cost_savings)
        
        self.logger.info("Optimization recorded",
                        type=optimization_type,
                        status=status,
                        cost_savings=cost_savings)
    
    def update_health_status(self, service: str, status: str, details: Dict[str, Any] = None, response_time_ms: float = 0.0):
        """Update health status for a service"""
        self.health_status[service] = HealthStatus(
            service=service,
            status=status,
            timestamp=datetime.now(),
            details=details or {},
            response_time_ms=response_time_ms
        )
        
        self.logger.info("Health status updated",
                        service=service,
                        status=status,
                        response_time_ms=response_time_ms)
    
    def get_health_status(self) -> Dict[str, HealthStatus]:
        """Get current health status for all services"""
        return self.health_status.copy()
    
    def get_system_metrics(self, hours: int = 1) -> List[SystemMetrics]:
        """Get system metrics for the last N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [m for m in self.system_metrics if m.timestamp > cutoff]
    
    def get_application_metrics(self, hours: int = 1) -> List[ApplicationMetrics]:
        """Get application metrics for the last N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [m for m in self.application_metrics if m.timestamp > cutoff]
    
    def get_uptime(self) -> timedelta:
        """Get system uptime"""
        return datetime.now() - self.start_time
    
    def get_prometheus_metrics(self) -> str:
        """Get Prometheus metrics in text format"""
        if PROMETHEUS_AVAILABLE:
            return generate_latest(self.registry).decode('utf-8')
        else:
            return "# Prometheus metrics not available\n"
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of all metrics"""
        latest_system = self.system_metrics[-1] if self.system_metrics else None
        latest_app = self.application_metrics[-1] if self.application_metrics else None
        
        return {
            "uptime_seconds": self.get_uptime().total_seconds(),
            "system_metrics": asdict(latest_system) if latest_system else None,
            "application_metrics": asdict(latest_app) if latest_app else None,
            "health_status": {k: asdict(v) for k, v in self.health_status.items()},
            "prometheus_available": PROMETHEUS_AVAILABLE,
            "opentelemetry_available": OPENTELEMETRY_AVAILABLE,
            "structlog_available": STRUCTLOG_AVAILABLE
        }


class HealthCheckEndpoint:
    """Health check endpoint for monitoring"""
    
    def __init__(self, monitoring_system: MonitoringSystem):
        self.monitoring = monitoring_system
    
    def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": self.monitoring.get_uptime().total_seconds(),
            "services": {}
        }
        
        # Check each service
        for service_name, health_status in self.monitoring.get_health_status().items():
            service_health = {
                "status": health_status.status,
                "last_check": health_status.timestamp.isoformat(),
                "response_time_ms": health_status.response_time_ms,
                "details": health_status.details
            }
            
            health_data["services"][service_name] = service_health
            
            # Overall status is degraded if any service is not healthy
            if health_status.status != "healthy":
                health_data["status"] = "degraded"
        
        return health_data
    
    def metrics_endpoint(self) -> str:
        """Prometheus metrics endpoint"""
        return self.monitoring.get_prometheus_metrics()
    
    def detailed_metrics(self) -> Dict[str, Any]:
        """Detailed metrics endpoint"""
        return self.monitoring.get_metrics_summary()


# Global monitoring instance
monitoring_system = MonitoringSystem() 