"""
Phase 1: Advanced Analytics & Intelligence Engine
Provides pattern recognition, anomaly detection, predictive analytics, and business intelligence.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
from dataclasses import dataclass
from upid.core.metrics_collector import RealTimeAnalyzer


@dataclass
class Pattern:
    """Represents a detected pattern in data"""
    pattern_type: str
    confidence: float
    description: str
    data_points: List[Dict]
    start_time: datetime
    end_time: datetime
    severity: str = "info"  # info, warning, critical


@dataclass
class Anomaly:
    """Represents a detected anomaly"""
    anomaly_type: str
    severity: str  # low, medium, high, critical
    confidence: float
    description: str
    detected_at: datetime
    affected_metrics: List[str]
    baseline_value: float
    current_value: float
    deviation_percentage: float


@dataclass
class Prediction:
    """Represents a prediction for future resource needs"""
    resource_type: str  # cpu, memory, network, cost
    predicted_value: float
    confidence: float
    time_horizon: str  # 1h, 6h, 24h, 7d
    prediction_date: datetime
    trend: str  # increasing, decreasing, stable
    recommendation: str


class PatternRecognitionEngine:
    """
    Advanced pattern recognition engine for Kubernetes workloads.
    Identifies complex usage patterns, business cycles, and operational patterns.
    """
    
    def __init__(self):
        self.patterns = []
        self.pattern_detectors = {
            'business_cycles': self._detect_business_cycles,
            'resource_spikes': self._detect_resource_spikes,
            'request_patterns': self._detect_request_patterns,
            'error_patterns': self._detect_error_patterns,
            'cost_patterns': self._detect_cost_patterns
        }
    
    def analyze_patterns(self, data: Dict[str, Any]) -> List[Pattern]:
        """
        Comprehensive pattern analysis across all data sources.
        """
        patterns = []
        
        for pattern_type, detector in self.pattern_detectors.items():
            try:
                detected_patterns = detector(data)
                patterns.extend(detected_patterns)
            except Exception as e:
                print(f"Error in {pattern_type} detection: {e}")
                continue
        
        self.patterns = patterns
        return patterns
    
    def _detect_business_cycles(self, data: Dict[str, Any]) -> List[Pattern]:
        """
        Detect business cycles (daily, weekly, monthly patterns).
        """
        patterns = []
        
        if 'log_analysis' in data and 'request_patterns' in data['log_analysis']:
            hourly_dist = data['log_analysis']['request_patterns'].get('hourly_distribution', {})
            
            if len(hourly_dist) >= 24:  # Need full day of data
                # Find peak hours
                peak_hours = sorted(hourly_dist.items(), key=lambda x: x[1], reverse=True)[:3]
                avg_requests = statistics.mean(hourly_dist.values())
                
                if peak_hours[0][1] > avg_requests * 2:  # 2x average is significant
                    patterns.append(Pattern(
                        pattern_type="business_cycle",
                        confidence=0.85,
                        description=f"Peak business hours detected: {peak_hours[0][0]}:00-{peak_hours[0][0]+1}:00",
                        data_points=[{"hour": hour, "requests": count} for hour, count in peak_hours],
                        start_time=datetime.now() - timedelta(hours=24),
                        end_time=datetime.now(),
                        severity="info"
                    ))
        
        return patterns
    
    def _detect_resource_spikes(self, data: Dict[str, Any]) -> List[Pattern]:
        """
        Detect unusual resource usage spikes.
        """
        patterns = []
        
        if 'metrics_analysis' in data:
            metrics = data['metrics_analysis']
            cpu_usage = metrics.get('cpu_usage', {}).get('average', 0)
            memory_usage = metrics.get('memory_usage', {}).get('average', 0)
            
            # Detect CPU spikes (>80% for extended periods)
            if cpu_usage > 80:
                patterns.append(Pattern(
                    pattern_type="resource_spike",
                    confidence=0.90,
                    description=f"High CPU usage detected: {cpu_usage:.1f}%",
                    data_points=[{"metric": "cpu", "value": cpu_usage}],
                    start_time=datetime.now() - timedelta(hours=1),
                    end_time=datetime.now(),
                    severity="warning"
                ))
            
            # Detect memory spikes (>85% for extended periods)
            if memory_usage > 85:
                patterns.append(Pattern(
                    pattern_type="resource_spike",
                    confidence=0.90,
                    description=f"High memory usage detected: {memory_usage:.1f}%",
                    data_points=[{"metric": "memory", "value": memory_usage}],
                    start_time=datetime.now() - timedelta(hours=1),
                    end_time=datetime.now(),
                    severity="warning"
                ))
        
        return patterns
    
    def _detect_request_patterns(self, data: Dict[str, Any]) -> List[Pattern]:
        """
        Detect patterns in request flows and API usage.
        """
        patterns = []
        
        if 'log_analysis' in data and 'request_patterns' in data['log_analysis']:
            req_patterns = data['log_analysis']['request_patterns']
            
            # Detect API endpoint popularity
            endpoints = req_patterns.get('endpoints', {})
            if endpoints:
                top_endpoints = sorted(endpoints.items(), key=lambda x: x[1], reverse=True)[:3]
                total_requests = sum(endpoints.values())
                
                for endpoint, count in top_endpoints:
                    percentage = (count / total_requests) * 100
                    if percentage > 30:  # More than 30% of traffic
                        patterns.append(Pattern(
                            pattern_type="request_pattern",
                            confidence=0.80,
                            description=f"High traffic endpoint: {endpoint} ({percentage:.1f}% of requests)",
                            data_points=[{"endpoint": endpoint, "requests": count, "percentage": percentage}],
                            start_time=datetime.now() - timedelta(hours=1),
                            end_time=datetime.now(),
                            severity="info"
                        ))
        
        return patterns
    
    def _detect_error_patterns(self, data: Dict[str, Any]) -> List[Pattern]:
        """
        Detect patterns in error rates and types.
        """
        patterns = []
        
        if 'log_analysis' in data and 'request_patterns' in data['log_analysis']:
            status_codes = data['log_analysis']['request_patterns'].get('status_codes', {})
            total_requests = sum(status_codes.values())
            
            if total_requests > 0:
                error_codes = {k: v for k, v in status_codes.items() if k.startswith('4') or k.startswith('5')}
                error_rate = sum(error_codes.values()) / total_requests
                
                if error_rate > 0.05:  # More than 5% error rate
                    patterns.append(Pattern(
                        pattern_type="error_pattern",
                        confidence=0.95,
                        description=f"High error rate detected: {error_rate:.1%}",
                        data_points=[{"error_rate": error_rate, "error_codes": error_codes}],
                        start_time=datetime.now() - timedelta(hours=1),
                        end_time=datetime.now(),
                        severity="critical"
                    ))
        
        return patterns
    
    def _detect_cost_patterns(self, data: Dict[str, Any]) -> List[Pattern]:
        """
        Detect patterns in cost and resource efficiency.
        """
        patterns = []
        
        if 'business_impact' in data:
            impact = data['business_impact']
            efficiency_score = impact.get('efficiency_score', 0)
            business_ratio = impact.get('business_request_ratio', 0)
            
            # Detect low efficiency
            if efficiency_score < 50:
                patterns.append(Pattern(
                    pattern_type="cost_pattern",
                    confidence=0.85,
                    description=f"Low resource efficiency: {efficiency_score:.1f}%",
                    data_points=[{"efficiency_score": efficiency_score, "business_ratio": business_ratio}],
                    start_time=datetime.now() - timedelta(hours=1),
                    end_time=datetime.now(),
                    severity="warning"
                ))
        
        return patterns


class AnomalyDetectionEngine:
    """
    Advanced anomaly detection engine using statistical analysis and ML techniques.
    Detects unusual behavior patterns in resource usage, request flows, and costs.
    """
    
    def __init__(self):
        self.baselines = {}
        self.anomalies = []
        self.detection_methods = {
            'statistical': self._statistical_anomaly_detection,
            'threshold': self._threshold_anomaly_detection,
            'trend': self._trend_anomaly_detection
        }
    
    def detect_anomalies(self, data: Dict[str, Any], historical_data: Optional[List[Dict]] = None) -> List[Anomaly]:
        """
        Comprehensive anomaly detection across all metrics.
        """
        anomalies = []
        
        # Update baselines with historical data
        if historical_data:
            self._update_baselines(historical_data)
        
        # Detect anomalies using multiple methods
        for method_name, detector in self.detection_methods.items():
            try:
                detected_anomalies = detector(data)
                anomalies.extend(detected_anomalies)
            except Exception as e:
                print(f"Error in {method_name} anomaly detection: {e}")
                continue
        
        self.anomalies = anomalies
        return anomalies
    
    def _update_baselines(self, historical_data: List[Dict]):
        """
        Update baseline values from historical data.
        """
        if not historical_data:
            return
        
        # Calculate baselines for different metrics
        cpu_values = []
        memory_values = []
        request_counts = []
        
        for data_point in historical_data:
            if 'metrics_analysis' in data_point:
                metrics = data_point['metrics_analysis']
                cpu_values.append(metrics.get('cpu_usage', {}).get('average', 0))
                memory_values.append(metrics.get('memory_usage', {}).get('average', 0))
            
            if 'log_analysis' in data_point:
                request_counts.append(data_point['log_analysis'].get('total_requests', 0))
        
        # Store baselines
        if cpu_values:
            self.baselines['cpu'] = {
                'mean': statistics.mean(cpu_values),
                'std': statistics.stdev(cpu_values) if len(cpu_values) > 1 else 0,
                'percentile_95': np.percentile(cpu_values, 95) if len(cpu_values) > 0 else 0
            }
        
        if memory_values:
            self.baselines['memory'] = {
                'mean': statistics.mean(memory_values),
                'std': statistics.stdev(memory_values) if len(memory_values) > 1 else 0,
                'percentile_95': np.percentile(memory_values, 95) if len(memory_values) > 0 else 0
            }
        
        if request_counts:
            self.baselines['requests'] = {
                'mean': statistics.mean(request_counts),
                'std': statistics.stdev(request_counts) if len(request_counts) > 1 else 0,
                'percentile_95': np.percentile(request_counts, 95) if len(request_counts) > 0 else 0
            }
    
    def _statistical_anomaly_detection(self, data: Dict[str, Any]) -> List[Anomaly]:
        """
        Statistical anomaly detection using z-score and percentile analysis.
        """
        anomalies = []
        
        if 'metrics_analysis' in data:
            metrics = data['metrics_analysis']
            current_cpu = metrics.get('cpu_usage', {}).get('average', 0)
            current_memory = metrics.get('memory_usage', {}).get('average', 0)
            
            # CPU anomaly detection
            if 'cpu' in self.baselines and self.baselines['cpu']['std'] > 0:
                cpu_z_score = abs(current_cpu - self.baselines['cpu']['mean']) / self.baselines['cpu']['std']
                
                if cpu_z_score > 2.5:  # Significant deviation
                    deviation_pct = ((current_cpu - self.baselines['cpu']['mean']) / self.baselines['cpu']['mean']) * 100
                    severity = "critical" if cpu_z_score > 4 else "high" if cpu_z_score > 3 else "medium"
                    
                    anomalies.append(Anomaly(
                        anomaly_type="statistical",
                        severity=severity,
                        confidence=min(0.95, cpu_z_score / 5),
                        description=f"CPU usage anomaly: {current_cpu:.1f}% (baseline: {self.baselines['cpu']['mean']:.1f}%)",
                        detected_at=datetime.now(),
                        affected_metrics=["cpu"],
                        baseline_value=self.baselines['cpu']['mean'],
                        current_value=current_cpu,
                        deviation_percentage=deviation_pct
                    ))
            
            # Memory anomaly detection
            if 'memory' in self.baselines and self.baselines['memory']['std'] > 0:
                memory_z_score = abs(current_memory - self.baselines['memory']['mean']) / self.baselines['memory']['std']
                
                if memory_z_score > 2.5:
                    deviation_pct = ((current_memory - self.baselines['memory']['mean']) / self.baselines['memory']['mean']) * 100
                    severity = "critical" if memory_z_score > 4 else "high" if memory_z_score > 3 else "medium"
                    
                    anomalies.append(Anomaly(
                        anomaly_type="statistical",
                        severity=severity,
                        confidence=min(0.95, memory_z_score / 5),
                        description=f"Memory usage anomaly: {current_memory:.1f}% (baseline: {self.baselines['memory']['mean']:.1f}%)",
                        detected_at=datetime.now(),
                        affected_metrics=["memory"],
                        baseline_value=self.baselines['memory']['mean'],
                        current_value=current_memory,
                        deviation_percentage=deviation_pct
                    ))
        
        return anomalies
    
    def _threshold_anomaly_detection(self, data: Dict[str, Any]) -> List[Anomaly]:
        """
        Threshold-based anomaly detection for critical metrics.
        """
        anomalies = []
        
        if 'metrics_analysis' in data:
            metrics = data['metrics_analysis']
            current_cpu = metrics.get('cpu_usage', {}).get('average', 0)
            current_memory = metrics.get('memory_usage', {}).get('average', 0)
            
            # CPU threshold anomalies
            if current_cpu > 90:
                anomalies.append(Anomaly(
                    anomaly_type="threshold",
                    severity="critical",
                    confidence=0.95,
                    description=f"Critical CPU usage: {current_cpu:.1f}%",
                    detected_at=datetime.now(),
                    affected_metrics=["cpu"],
                    baseline_value=90,
                    current_value=current_cpu,
                    deviation_percentage=((current_cpu - 90) / 90) * 100
                ))
            elif current_cpu > 80:
                anomalies.append(Anomaly(
                    anomaly_type="threshold",
                    severity="high",
                    confidence=0.85,
                    description=f"High CPU usage: {current_cpu:.1f}%",
                    detected_at=datetime.now(),
                    affected_metrics=["cpu"],
                    baseline_value=80,
                    current_value=current_cpu,
                    deviation_percentage=((current_cpu - 80) / 80) * 100
                ))
            
            # Memory threshold anomalies
            if current_memory > 95:
                anomalies.append(Anomaly(
                    anomaly_type="threshold",
                    severity="critical",
                    confidence=0.95,
                    description=f"Critical memory usage: {current_memory:.1f}%",
                    detected_at=datetime.now(),
                    affected_metrics=["memory"],
                    baseline_value=95,
                    current_value=current_memory,
                    deviation_percentage=((current_memory - 95) / 95) * 100
                ))
            elif current_memory > 85:
                anomalies.append(Anomaly(
                    anomaly_type="threshold",
                    severity="high",
                    confidence=0.85,
                    description=f"High memory usage: {current_memory:.1f}%",
                    detected_at=datetime.now(),
                    affected_metrics=["memory"],
                    baseline_value=85,
                    current_value=current_memory,
                    deviation_percentage=((current_memory - 85) / 85) * 100
                ))
        
        return anomalies
    
    def _trend_anomaly_detection(self, data: Dict[str, Any]) -> List[Anomaly]:
        """
        Trend-based anomaly detection for gradual changes.
        """
        # This would require historical data points to detect trends
        # For now, return empty list - can be enhanced with time-series analysis
        return []


class PredictiveAnalyticsEngine:
    """
    Predictive analytics engine for forecasting resource needs and costs.
    Uses time-series analysis and machine learning techniques.
    """
    
    def __init__(self):
        self.models = {}
        self.predictions = []
    
    def generate_predictions(self, data: Dict[str, Any], historical_data: Optional[List[Dict]] = None) -> List[Prediction]:
        """
        Generate predictions for resource needs and costs.
        """
        predictions = []
        
        # CPU prediction
        cpu_prediction = self._predict_cpu_usage(data, historical_data)
        if cpu_prediction:
            predictions.append(cpu_prediction)
        
        # Memory prediction
        memory_prediction = self._predict_memory_usage(data, historical_data)
        if memory_prediction:
            predictions.append(memory_prediction)
        
        # Cost prediction
        cost_prediction = self._predict_cost_trends(data, historical_data)
        if cost_prediction:
            predictions.append(cost_prediction)
        
        self.predictions = predictions
        return predictions
    
    def _predict_cpu_usage(self, data: Dict[str, Any], historical_data: Optional[List[Dict]]) -> Optional[Prediction]:
        """
        Predict CPU usage for next 24 hours.
        """
        if not historical_data or len(historical_data) < 7:  # Need at least a week of data
            return None
        
        # Simple linear regression for now
        cpu_values = []
        timestamps = []
        
        for data_point in historical_data[-7:]:  # Last 7 days
            if 'metrics_analysis' in data_point:
                cpu = data_point['metrics_analysis'].get('cpu_usage', {}).get('average', 0)
                cpu_values.append(cpu)
                timestamps.append(len(cpu_values))  # Simple time index
        
        if len(cpu_values) < 3:
            return None
        
        # Calculate trend
        current_cpu = data.get('metrics_analysis', {}).get('cpu_usage', {}).get('average', 0)
        avg_cpu = statistics.mean(cpu_values)
        
        if current_cpu > avg_cpu * 1.2:
            trend = "increasing"
            predicted_value = min(100, current_cpu * 1.1)  # Conservative increase
        elif current_cpu < avg_cpu * 0.8:
            trend = "decreasing"
            predicted_value = max(0, current_cpu * 0.9)  # Conservative decrease
        else:
            trend = "stable"
            predicted_value = current_cpu
        
        return Prediction(
            resource_type="cpu",
            predicted_value=predicted_value,
            confidence=0.75,
            time_horizon="24h",
            prediction_date=datetime.now(),
            trend=trend,
            recommendation=f"CPU usage is {trend}. Monitor for scaling needs."
        )
    
    def _predict_memory_usage(self, data: Dict[str, Any], historical_data: Optional[List[Dict]]) -> Optional[Prediction]:
        """
        Predict memory usage for next 24 hours.
        """
        if not historical_data or len(historical_data) < 7:
            return None
        
        memory_values = []
        for data_point in historical_data[-7:]:
            if 'metrics_analysis' in data_point:
                memory = data_point['metrics_analysis'].get('memory_usage', {}).get('average', 0)
                memory_values.append(memory)
        
        if len(memory_values) < 3:
            return None
        
        current_memory = data.get('metrics_analysis', {}).get('memory_usage', {}).get('average', 0)
        avg_memory = statistics.mean(memory_values)
        
        if current_memory > avg_memory * 1.2:
            trend = "increasing"
            predicted_value = min(100, current_memory * 1.1)
        elif current_memory < avg_memory * 0.8:
            trend = "decreasing"
            predicted_value = max(0, current_memory * 0.9)
        else:
            trend = "stable"
            predicted_value = current_memory
        
        return Prediction(
            resource_type="memory",
            predicted_value=predicted_value,
            confidence=0.75,
            time_horizon="24h",
            prediction_date=datetime.now(),
            trend=trend,
            recommendation=f"Memory usage is {trend}. Consider optimization if {trend}."
        )
    
    def _predict_cost_trends(self, data: Dict[str, Any], historical_data: Optional[List[Dict]]) -> Optional[Prediction]:
        """
        Predict cost trends based on resource usage and efficiency.
        """
        if 'business_impact' not in data:
            return None
        
        efficiency_score = data['business_impact'].get('efficiency_score', 0)
        business_ratio = data['business_impact'].get('business_request_ratio', 0)
        
        # Simple cost prediction based on efficiency
        if efficiency_score < 50:
            trend = "increasing"
            predicted_value = 1.2  # 20% increase
            recommendation = "Low efficiency detected. Consider optimization to reduce costs."
        elif efficiency_score > 80:
            trend = "decreasing"
            predicted_value = 0.9  # 10% decrease
            recommendation = "High efficiency. Costs likely to remain stable or decrease."
        else:
            trend = "stable"
            predicted_value = 1.0  # No change
            recommendation = "Efficiency is acceptable. Monitor for changes."
        
        return Prediction(
            resource_type="cost",
            predicted_value=predicted_value,
            confidence=0.70,
            time_horizon="7d",
            prediction_date=datetime.now(),
            trend=trend,
            recommendation=recommendation
        )


class BusinessIntelligenceEngine:
    """
    Business intelligence engine that correlates technical metrics with business KPIs.
    Provides executive-level insights and recommendations.
    """
    
    def __init__(self):
        self.kpi_correlations = {}
        self.business_insights = []
    
    def analyze_business_impact(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive business impact analysis.
        """
        insights = {
            'efficiency_analysis': self._analyze_efficiency(data),
            'cost_analysis': self._analyze_cost_impact(data),
            'performance_analysis': self._analyze_performance_impact(data),
            'recommendations': self._generate_business_recommendations(data),
            'risk_assessment': self._assess_business_risks(data)
        }
        
        self.business_insights.append({
            'timestamp': datetime.now().isoformat(),
            'insights': insights
        })
        
        return insights
    
    def _analyze_efficiency(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze resource efficiency and business impact.
        """
        if 'business_impact' not in data:
            return {'status': 'no_data'}
        
        efficiency_score = data['business_impact'].get('efficiency_score', 0)
        business_ratio = data['business_impact'].get('business_request_ratio', 0)
        
        analysis = {
            'efficiency_score': efficiency_score,
            'business_request_ratio': business_ratio,
            'efficiency_level': 'high' if efficiency_score > 80 else 'medium' if efficiency_score > 60 else 'low',
            'business_impact': 'excellent' if business_ratio > 0.8 else 'good' if business_ratio > 0.6 else 'poor',
            'optimization_potential': max(0, 100 - efficiency_score)
        }
        
        return analysis
    
    def _analyze_cost_impact(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze cost impact and optimization opportunities.
        """
        if 'metrics_analysis' not in data:
            return {'status': 'no_data'}
        
        metrics = data['metrics_analysis']
        cpu_usage = metrics.get('cpu_usage', {}).get('average', 0)
        memory_usage = metrics.get('memory_usage', {}).get('average', 0)
        
        # Calculate cost efficiency
        resource_efficiency = (cpu_usage + memory_usage) / 2
        cost_optimization_potential = max(0, 100 - resource_efficiency)
        
        analysis = {
            'current_resource_usage': resource_efficiency,
            'cost_optimization_potential': cost_optimization_potential,
            'resource_waste': max(0, 100 - resource_efficiency),
            'cost_impact': 'high' if resource_efficiency > 80 else 'medium' if resource_efficiency > 60 else 'low'
        }
        
        return analysis
    
    def _analyze_performance_impact(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze performance impact on business operations.
        """
        if 'log_analysis' not in data:
            return {'status': 'no_data'}
        
        log_analysis = data['log_analysis']
        total_requests = log_analysis.get('total_requests', 0)
        business_requests = log_analysis.get('business_requests', 0)
        error_summary = log_analysis.get('error_summary', {})
        
        # Calculate error rate
        total_errors = sum(error_summary.values())
        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
        
        analysis = {
            'total_requests': total_requests,
            'business_requests': business_requests,
            'error_rate': error_rate,
            'performance_impact': 'critical' if error_rate > 5 else 'moderate' if error_rate > 2 else 'minimal',
            'availability_score': max(0, 100 - error_rate)
        }
        
        return analysis
    
    def _generate_business_recommendations(self, data: Dict[str, Any]) -> List[str]:
        """
        Generate business-focused recommendations.
        """
        recommendations = []
        
        if 'business_impact' in data:
            efficiency_score = data['business_impact'].get('efficiency_score', 0)
            business_ratio = data['business_impact'].get('business_request_ratio', 0)
            
            if efficiency_score < 50:
                recommendations.append("Critical: Low resource efficiency detected. Immediate optimization required.")
            elif efficiency_score < 70:
                recommendations.append("Warning: Resource efficiency below optimal levels. Consider optimization.")
            
            if business_ratio < 0.3:
                recommendations.append("Critical: Low business request ratio. Review health check frequency.")
            elif business_ratio < 0.6:
                recommendations.append("Warning: Business request ratio below optimal. Monitor traffic patterns.")
        
        if 'metrics_analysis' in data:
            metrics = data['metrics_analysis']
            cpu_usage = metrics.get('cpu_usage', {}).get('average', 0)
            memory_usage = metrics.get('memory_usage', {}).get('average', 0)
            
            if cpu_usage > 80:
                recommendations.append("High CPU usage detected. Consider scaling up or optimization.")
            if memory_usage > 85:
                recommendations.append("High memory usage detected. Consider memory optimization or scaling.")
        
        return recommendations
    
    def _assess_business_risks(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess business risks based on technical metrics.
        """
        risks = {
            'high_risk': [],
            'medium_risk': [],
            'low_risk': []
        }
        
        if 'business_impact' in data:
            efficiency_score = data['business_impact'].get('efficiency_score', 0)
            if efficiency_score < 30:
                risks['high_risk'].append("Critical resource inefficiency")
            elif efficiency_score < 50:
                risks['medium_risk'].append("Low resource efficiency")
        
        if 'metrics_analysis' in data:
            metrics = data['metrics_analysis']
            cpu_usage = metrics.get('cpu_usage', {}).get('average', 0)
            memory_usage = metrics.get('memory_usage', {}).get('average', 0)
            
            if cpu_usage > 90:
                risks['high_risk'].append("Critical CPU usage")
            elif cpu_usage > 80:
                risks['medium_risk'].append("High CPU usage")
            
            if memory_usage > 95:
                risks['high_risk'].append("Critical memory usage")
            elif memory_usage > 85:
                risks['medium_risk'].append("High memory usage")
        
        return risks


class AdvancedAnalyticsEngine:
    """
    Main advanced analytics engine that orchestrates all analytics components.
    Provides comprehensive intelligence and insights.
    """
    
    def __init__(self):
        self.pattern_engine = PatternRecognitionEngine()
        self.anomaly_engine = AnomalyDetectionEngine()
        self.predictive_engine = PredictiveAnalyticsEngine()
        self.business_engine = BusinessIntelligenceEngine()
        self.analyzer = RealTimeAnalyzer()
    
    async def comprehensive_analysis(self, pod_name: str, namespace: str = "default", 
                                  time_range: str = "1h", historical_data: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Perform comprehensive advanced analytics on a pod.
        """
        # Get current data
        current_data = await self.analyzer.analyze_pod_batch(pod_name, namespace, time_range)
        
        # Pattern recognition
        patterns = self.pattern_engine.analyze_patterns(current_data)
        
        # Anomaly detection
        anomalies = self.anomaly_engine.detect_anomalies(current_data, historical_data)
        
        # Predictive analytics
        predictions = self.predictive_engine.generate_predictions(current_data, historical_data)
        
        # Business intelligence
        business_insights = self.business_engine.analyze_business_impact(current_data)
        
        # Compile comprehensive report
        analysis_report = {
            'pod_name': pod_name,
            'namespace': namespace,
            'analysis_timestamp': datetime.now().isoformat(),
            'time_range': time_range,
            'current_metrics': current_data,
            'patterns': [self._pattern_to_dict(p) for p in patterns],
            'anomalies': [self._anomaly_to_dict(a) for a in anomalies],
            'predictions': [self._prediction_to_dict(p) for p in predictions],
            'business_insights': business_insights,
            'summary': self._generate_summary(patterns, anomalies, predictions, business_insights)
        }
        
        return analysis_report
    
    def _pattern_to_dict(self, pattern: Pattern) -> Dict[str, Any]:
        """Convert Pattern to dictionary for serialization."""
        return {
            'pattern_type': pattern.pattern_type,
            'confidence': pattern.confidence,
            'description': pattern.description,
            'severity': pattern.severity,
            'start_time': pattern.start_time.isoformat(),
            'end_time': pattern.end_time.isoformat(),
            'data_points': pattern.data_points
        }
    
    def _anomaly_to_dict(self, anomaly: Anomaly) -> Dict[str, Any]:
        """Convert Anomaly to dictionary for serialization."""
        return {
            'anomaly_type': anomaly.anomaly_type,
            'severity': anomaly.severity,
            'confidence': anomaly.confidence,
            'description': anomaly.description,
            'detected_at': anomaly.detected_at.isoformat(),
            'affected_metrics': anomaly.affected_metrics,
            'baseline_value': anomaly.baseline_value,
            'current_value': anomaly.current_value,
            'deviation_percentage': anomaly.deviation_percentage
        }
    
    def _prediction_to_dict(self, prediction: Prediction) -> Dict[str, Any]:
        """Convert Prediction to dictionary for serialization."""
        return {
            'resource_type': prediction.resource_type,
            'predicted_value': prediction.predicted_value,
            'confidence': prediction.confidence,
            'time_horizon': prediction.time_horizon,
            'prediction_date': prediction.prediction_date.isoformat(),
            'trend': prediction.trend,
            'recommendation': prediction.recommendation
        }
    
    def _generate_summary(self, patterns: List[Pattern], anomalies: List[Anomaly], 
                         predictions: List[Prediction], business_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary of all analytics."""
        critical_anomalies = [a for a in anomalies if a.severity == "critical"]
        high_anomalies = [a for a in anomalies if a.severity == "high"]
        
        summary = {
            'total_patterns': len(patterns),
            'total_anomalies': len(anomalies),
            'critical_anomalies': len(critical_anomalies),
            'high_anomalies': len(high_anomalies),
            'total_predictions': len(predictions),
            'overall_health': 'critical' if critical_anomalies else 'warning' if high_anomalies else 'healthy',
            'key_insights': [
                f"Detected {len(patterns)} patterns in resource usage",
                f"Found {len(anomalies)} anomalies requiring attention",
                f"Generated {len(predictions)} predictions for resource planning"
            ]
        }
        
        return summary 