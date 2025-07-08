"""
Pattern Analysis Engine for UPID Intelligence
Detects usage patterns, trends, and anomalies in Kubernetes metrics
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import logging
from collections import defaultdict
import json

logger = logging.getLogger(__name__)

class PatternAnalyzer:
    """Advanced pattern analysis for Kubernetes metrics"""
    
    def __init__(self):
        """Initialize the pattern analyzer"""
        self.pattern_types = {
            'temporal': 'Time-based usage patterns',
            'seasonal': 'Weekly/monthly recurring patterns',
            'anomaly': 'Unusual usage spikes or drops',
            'trend': 'Long-term usage trends',
            'idle': 'Idle resource patterns',
            'business': 'Business hours correlation'
        }
    
    def analyze_historical_data(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze historical data for patterns and insights"""
        analysis = {
            'cluster_id': historical_data['cluster_id'],
            'analysis_period': historical_data['period_days'],
            'generated_at': datetime.utcnow().isoformat(),
            'patterns': {},
            'trends': {},
            'anomalies': {},
            'recommendations': [],
            'confidence_scores': {}
        }
        
        try:
            # Analyze CPU utilization patterns
            if 'cpu_utilization' in historical_data['metrics']:
                cpu_data = historical_data['metrics']['cpu_utilization']
                analysis['patterns']['cpu'] = self._analyze_cpu_patterns(cpu_data)
                analysis['trends']['cpu'] = self._analyze_trends(cpu_data)
                analysis['anomalies']['cpu'] = self._detect_anomalies(cpu_data)
            
            # Analyze memory utilization patterns
            if 'memory_utilization' in historical_data['metrics']:
                memory_data = historical_data['metrics']['memory_utilization']
                analysis['patterns']['memory'] = self._analyze_memory_patterns(memory_data)
                analysis['trends']['memory'] = self._analyze_trends(memory_data)
                analysis['anomalies']['memory'] = self._detect_anomalies(memory_data)
            
            # Generate recommendations
            analysis['recommendations'] = self._generate_recommendations(analysis)
            
            # Calculate confidence scores
            analysis['confidence_scores'] = self._calculate_confidence_scores(analysis)
            
            logger.info(f"Completed pattern analysis for cluster {historical_data['cluster_id']}")
            
        except Exception as e:
            logger.error(f"Error analyzing historical data: {e}")
            analysis['error'] = str(e)
        
        return analysis
    
    def _analyze_cpu_patterns(self, cpu_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze CPU utilization patterns"""
        if not cpu_data:
            return {}
        
        values = [point['value'] for point in cpu_data]
        timestamps = [point['timestamp'] for point in cpu_data]
        
        patterns = {
            'average_utilization': np.mean(values),
            'peak_utilization': np.max(values),
            'min_utilization': np.min(values),
            'utilization_std': np.std(values),
            'utilization_variance': np.var(values)
        }
        
        # Detect business hours pattern
        business_pattern = self._detect_business_hours_pattern(timestamps, values)
        if business_pattern:
            patterns['business_hours_pattern'] = business_pattern
        
        # Detect weekend pattern
        weekend_pattern = self._detect_weekend_pattern(timestamps, values)
        if weekend_pattern:
            patterns['weekend_pattern'] = weekend_pattern
        
        # Detect idle periods
        idle_pattern = self._detect_idle_periods(values, timestamps)
        if idle_pattern:
            patterns['idle_periods'] = idle_pattern
        
        return patterns
    
    def _analyze_memory_patterns(self, memory_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze memory utilization patterns"""
        if not memory_data:
            return {}
        
        values = [point['value'] for point in memory_data]
        timestamps = [point['timestamp'] for point in memory_data]
        
        patterns = {
            'average_utilization': np.mean(values),
            'peak_utilization': np.max(values),
            'min_utilization': np.min(values),
            'utilization_std': np.std(values),
            'utilization_variance': np.var(values)
        }
        
        # Detect memory leaks
        memory_leak = self._detect_memory_leak(values, timestamps)
        if memory_leak:
            patterns['memory_leak'] = memory_leak
        
        # Detect memory pressure
        memory_pressure = self._detect_memory_pressure(values)
        if memory_pressure:
            patterns['memory_pressure'] = memory_pressure
        
        return patterns
    
    def _analyze_trends(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze long-term trends in data"""
        if len(data) < 2:
            return {}
        
        values = [point['value'] for point in data]
        timestamps = [point['timestamp'] for point in data]
        
        # Calculate trend direction
        x = np.arange(len(values))
        slope, intercept = np.polyfit(x, values, 1)
        
        trend_direction = 'increasing' if slope > 0.01 else 'decreasing' if slope < -0.01 else 'stable'
        
        # Calculate trend strength
        trend_strength = abs(slope) / np.std(values) if np.std(values) > 0 else 0
        
        return {
            'direction': trend_direction,
            'slope': slope,
            'strength': trend_strength,
            'confidence': min(100, max(0, 100 - abs(trend_strength - 1) * 50))
        }
    
    def _detect_anomalies(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect anomalies in the data"""
        if len(data) < 10:
            return []
        
        values = [point['value'] for point in data]
        timestamps = [point['timestamp'] for point in data]
        
        anomalies = []
        
        # Statistical anomaly detection (3-sigma rule)
        mean = np.mean(values)
        std = np.std(values)
        
        for i, value in enumerate(values):
            z_score = abs(value - mean) / std if std > 0 else 0
            
            if z_score > 3:  # 3-sigma threshold
                anomalies.append({
                    'timestamp': timestamps[i],
                    'value': value,
                    'z_score': z_score,
                    'severity': 'high' if z_score > 4 else 'medium',
                    'type': 'statistical_outlier'
                })
        
        # Detect sudden spikes or drops
        for i in range(1, len(values)):
            change = abs(values[i] - values[i-1])
            avg_change = np.mean([abs(values[j] - values[j-1]) for j in range(1, len(values))])
            
            if change > avg_change * 3:  # 3x average change
                anomalies.append({
                    'timestamp': timestamps[i],
                    'value': values[i],
                    'change': change,
                    'severity': 'high' if change > avg_change * 5 else 'medium',
                    'type': 'sudden_change'
                })
        
        return anomalies
    
    def _detect_business_hours_pattern(self, timestamps: List[str], values: List[float]) -> Optional[Dict[str, Any]]:
        """Detect business hours usage pattern"""
        if len(timestamps) < 24:  # Need at least 24 hours of data
            return None
        
        # Group by hour of day
        hourly_usage = defaultdict(list)
        
        for timestamp, value in zip(timestamps, values):
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                hour = dt.hour
                hourly_usage[hour].append(value)
            except:
                continue
        
        if len(hourly_usage) < 12:  # Need data for most hours
            return None
        
        # Calculate average usage by hour
        hourly_averages = {}
        for hour in range(24):
            if hour in hourly_usage:
                hourly_averages[hour] = np.mean(hourly_usage[hour])
            else:
                hourly_averages[hour] = 0
        
        # Detect business hours (9 AM - 6 PM)
        business_hours = list(range(9, 18))
        non_business_hours = [h for h in range(24) if h not in business_hours]
        
        business_avg = np.mean([hourly_averages[h] for h in business_hours])
        non_business_avg = np.mean([hourly_averages[h] for h in non_business_hours])
        
        if business_avg > non_business_avg * 1.5:  # 50% higher during business hours
            return {
                'pattern_type': 'business_hours',
                'business_hours_avg': business_avg,
                'non_business_avg': non_business_avg,
                'ratio': business_avg / non_business_avg if non_business_avg > 0 else 0,
                'confidence': min(100, max(0, (business_avg - non_business_avg) / business_avg * 100))
            }
        
        return None
    
    def _detect_weekend_pattern(self, timestamps: List[str], values: List[float]) -> Optional[Dict[str, Any]]:
        """Detect weekend usage pattern"""
        if len(timestamps) < 48:  # Need at least 2 days of data
            return None
        
        # Group by day of week
        daily_usage = defaultdict(list)
        
        for timestamp, value in zip(timestamps, values):
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                day_of_week = dt.weekday()  # 0=Monday, 6=Sunday
                daily_usage[day_of_week].append(value)
            except:
                continue
        
        if len(daily_usage) < 5:  # Need data for most days
            return None
        
        # Calculate average usage by day
        daily_averages = {}
        for day in range(7):
            if day in daily_usage:
                daily_averages[day] = np.mean(daily_usage[day])
            else:
                daily_averages[day] = 0
        
        # Weekend vs weekday comparison
        weekday_avg = np.mean([daily_averages[d] for d in range(5)])  # Mon-Fri
        weekend_avg = np.mean([daily_averages[d] for d in [5, 6]])  # Sat-Sun
        
        if weekday_avg > weekend_avg * 1.3:  # 30% higher on weekdays
            return {
                'pattern_type': 'weekend',
                'weekday_avg': weekday_avg,
                'weekend_avg': weekend_avg,
                'ratio': weekday_avg / weekend_avg if weekend_avg > 0 else 0,
                'confidence': min(100, max(0, (weekday_avg - weekend_avg) / weekday_avg * 100))
            }
        
        return None
    
    def _detect_idle_periods(self, values: List[float], timestamps: List[str]) -> Optional[Dict[str, Any]]:
        """Detect idle periods in resource usage"""
        if len(values) < 10:
            return None
        
        # Define idle threshold (e.g., < 10% utilization)
        idle_threshold = 10.0
        idle_periods = []
        
        for i, value in enumerate(values):
            if value < idle_threshold:
                idle_periods.append({
                    'timestamp': timestamps[i],
                    'value': value,
                    'duration_hours': 1  # Assuming hourly data points
                })
        
        if len(idle_periods) > len(values) * 0.5:  # More than 50% idle
            return {
                'pattern_type': 'idle_periods',
                'idle_percentage': len(idle_periods) / len(values) * 100,
                'total_idle_periods': len(idle_periods),
                'average_idle_utilization': np.mean([p['value'] for p in idle_periods]),
                'confidence': min(100, len(idle_periods) / len(values) * 100)
            }
        
        return None
    
    def _detect_memory_leak(self, values: List[float], timestamps: List[str]) -> Optional[Dict[str, Any]]:
        """Detect potential memory leaks"""
        if len(values) < 24:  # Need at least 24 hours of data
            return None
        
        # Look for consistent upward trend
        x = np.arange(len(values))
        slope, _ = np.polyfit(x, values, 1)
        
        # Calculate R-squared to measure trend strength
        y_pred = slope * x + np.mean(values)
        ss_res = np.sum((values - y_pred) ** 2)
        ss_tot = np.sum((values - np.mean(values)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        if slope > 0.5 and r_squared > 0.7:  # Strong upward trend
            return {
                'pattern_type': 'memory_leak',
                'slope': slope,
                'r_squared': r_squared,
                'confidence': min(100, r_squared * 100),
                'severity': 'high' if slope > 1.0 else 'medium'
            }
        
        return None
    
    def _detect_memory_pressure(self, values: List[float]) -> Optional[Dict[str, Any]]:
        """Detect memory pressure patterns"""
        if len(values) < 10:
            return None
        
        # Check for high memory utilization
        high_usage_threshold = 80.0
        high_usage_periods = [v for v in values if v > high_usage_threshold]
        
        if len(high_usage_periods) > len(values) * 0.3:  # More than 30% high usage
            return {
                'pattern_type': 'memory_pressure',
                'high_usage_percentage': len(high_usage_periods) / len(values) * 100,
                'average_high_usage': np.mean(high_usage_periods),
                'confidence': min(100, len(high_usage_periods) / len(values) * 100),
                'severity': 'high' if len(high_usage_periods) > len(values) * 0.5 else 'medium'
            }
        
        return None
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate optimization recommendations based on analysis"""
        recommendations = []
        
        # CPU-based recommendations
        if 'cpu' in analysis['patterns']:
            cpu_patterns = analysis['patterns']['cpu']
            
            # Idle periods recommendation
            if 'idle_periods' in cpu_patterns:
                idle_data = cpu_patterns['idle_periods']
                if idle_data['idle_percentage'] > 50:
                    recommendations.append({
                        'type': 'zero_pod_scaling',
                        'priority': 'high',
                        'description': f"Detected {idle_data['idle_percentage']:.1f}% idle time - consider zero-pod scaling",
                        'potential_savings': idle_data['idle_percentage'] * 0.01,  # Rough estimate
                        'confidence': idle_data['confidence'],
                        'implementation_effort': 'low'
                    })
            
            # Business hours pattern recommendation
            if 'business_hours_pattern' in cpu_patterns:
                business_data = cpu_patterns['business_hours_pattern']
                if business_data['ratio'] > 2.0:
                    recommendations.append({
                        'type': 'business_hours_scaling',
                        'priority': 'medium',
                        'description': f"Strong business hours pattern detected - implement time-based scaling",
                        'potential_savings': 0.15,  # 15% savings estimate
                        'confidence': business_data['confidence'],
                        'implementation_effort': 'medium'
                    })
        
        # Memory-based recommendations
        if 'memory' in analysis['patterns']:
            memory_patterns = analysis['patterns']['memory']
            
            # Memory leak recommendation
            if 'memory_leak' in memory_patterns:
                leak_data = memory_patterns['memory_leak']
                recommendations.append({
                    'type': 'memory_optimization',
                    'priority': 'high',
                    'description': f"Potential memory leak detected - investigate and fix",
                    'potential_savings': 0.10,  # 10% savings estimate
                    'confidence': leak_data['confidence'],
                    'implementation_effort': 'high'
                })
            
            # Memory pressure recommendation
            if 'memory_pressure' in memory_patterns:
                pressure_data = memory_patterns['memory_pressure']
                recommendations.append({
                    'type': 'memory_scaling',
                    'priority': 'medium',
                    'description': f"Memory pressure detected - consider scaling up memory",
                    'potential_savings': -0.05,  # Cost increase
                    'confidence': pressure_data['confidence'],
                    'implementation_effort': 'medium'
                })
        
        # Trend-based recommendations
        if 'trends' in analysis:
            for resource, trend in analysis['trends'].items():
                if trend['direction'] == 'increasing' and trend['strength'] > 0.5:
                    recommendations.append({
                        'type': 'capacity_planning',
                        'priority': 'medium',
                        'description': f"Strong upward trend in {resource} usage - plan for capacity increase",
                        'potential_savings': 0.0,  # No immediate savings
                        'confidence': trend['confidence'],
                        'implementation_effort': 'high'
                    })
        
        return recommendations
    
    def _calculate_confidence_scores(self, analysis: Dict[str, Any]) -> Dict[str, float]:
        """Calculate confidence scores for analysis components"""
        confidence_scores = {}
        
        # Pattern confidence
        if 'patterns' in analysis:
            for resource, patterns in analysis['patterns'].items():
                if patterns:
                    # Average confidence of all patterns
                    confidences = []
                    for pattern_name, pattern_data in patterns.items():
                        if isinstance(pattern_data, dict) and 'confidence' in pattern_data:
                            confidences.append(pattern_data['confidence'])
                    
                    if confidences:
                        confidence_scores[f'{resource}_patterns'] = np.mean(confidences)
        
        # Trend confidence
        if 'trends' in analysis:
            for resource, trend in analysis['trends'].items():
                if trend and 'confidence' in trend:
                    confidence_scores[f'{resource}_trend'] = trend['confidence']
        
        # Overall confidence
        all_confidences = list(confidence_scores.values())
        if all_confidences:
            confidence_scores['overall'] = np.mean(all_confidences)
        
        return confidence_scores 