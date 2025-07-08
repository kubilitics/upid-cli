"""
Advanced Intelligence Engine for UPID
Implements sophisticated analytics beyond basic pattern detection
Features:
- 90-day historical analysis with compression
- Business calendar intelligence
- Multi-dimensional pattern analysis
- Predictive analytics
- Efficiency analysis
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import logging
from collections import defaultdict
import json
from scipy import stats
from scipy.signal import find_peaks
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class AdvancedIntelligenceEngine:
    """Advanced intelligence engine with sophisticated analytics"""
    
    def __init__(self):
        """Initialize the advanced intelligence engine"""
        self.analysis_periods = [7, 30, 90]  # days
        self.business_hours = {
            'start': 9,
            'end': 17,
            'timezone': 'UTC'
        }
        
        # Pattern detection thresholds
        self.anomaly_threshold = 3.0  # standard deviations
        self.trend_confidence_threshold = 0.8
        self.seasonal_confidence_threshold = 0.7
        
    def analyze_advanced_patterns(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform advanced pattern analysis with business intelligence"""
        try:
            analysis = {
                'cluster_id': historical_data.get('cluster_id', 'unknown'),
                'analysis_period': historical_data.get('period_days', 90),
                'generated_at': datetime.utcnow().isoformat(),
                'advanced_patterns': {},
                'business_intelligence': {},
                'predictive_insights': {},
                'efficiency_analysis': {},
                'confidence_metrics': {},
                'recommendations': []
            }
            
            # Analyze different time periods
            for period in self.analysis_periods:
                period_data = self._get_period_data(historical_data, period)
                if period_data:
                    analysis['advanced_patterns'][f'{period}_day'] = self._analyze_period_patterns(period_data, period)
            
            # Business intelligence analysis
            analysis['business_intelligence'] = self._analyze_business_intelligence(historical_data)
            
            # Predictive analytics
            analysis['predictive_insights'] = self._generate_predictive_insights(historical_data)
            
            # Efficiency analysis
            analysis['efficiency_analysis'] = self._analyze_efficiency_patterns(historical_data)
            
            # Calculate confidence metrics
            analysis['confidence_metrics'] = self._calculate_advanced_confidence(analysis)
            
            # Generate recommendations
            analysis['recommendations'] = self._generate_advanced_recommendations(analysis)
            
            logger.info(f"Completed advanced pattern analysis for cluster {analysis['cluster_id']}")
            
        except Exception as e:
            logger.error(f"Error in advanced pattern analysis: {e}")
            analysis['error'] = str(e)
        
        return analysis
    
    def _get_period_data(self, historical_data: Dict[str, Any], period_days: int) -> Optional[Dict[str, Any]]:
        """Get data for specific time period"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=period_days)
            
            # Filter data for the period
            period_metrics = {}
            
            for metric_type, data in historical_data.get('metrics', {}).items():
                period_data = []
                for point in data:
                    timestamp = datetime.fromisoformat(point['timestamp'])
                    if start_date <= timestamp <= end_date:
                        period_data.append(point)
                
                if period_data:
                    period_metrics[metric_type] = period_data
            
            if period_metrics:
                return {
                    'period_days': period_days,
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'metrics': period_metrics
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting period data: {e}")
            return None
    
    def _analyze_period_patterns(self, period_data: Dict[str, Any], period_days: int) -> Dict[str, Any]:
        """Analyze patterns for specific time period"""
        patterns = {
            'temporal_patterns': {},
            'seasonal_patterns': {},
            'trend_analysis': {},
            'anomaly_detection': {},
            'volatility_analysis': {}
        }
        
        try:
            for metric_type, data in period_data.get('metrics', {}).items():
                if not data:
                    continue
                
                values = [point['value'] for point in data]
                timestamps = [point['timestamp'] for point in data]
                
                # Temporal patterns
                patterns['temporal_patterns'][metric_type] = self._analyze_temporal_patterns(values, timestamps)
                
                # Seasonal patterns
                patterns['seasonal_patterns'][metric_type] = self._analyze_seasonal_patterns(values, timestamps, period_days)
                
                # Trend analysis
                patterns['trend_analysis'][metric_type] = self._analyze_advanced_trends(values, timestamps)
                
                # Anomaly detection
                patterns['anomaly_detection'][metric_type] = self._detect_advanced_anomalies(values, timestamps)
                
                # Volatility analysis
                patterns['volatility_analysis'][metric_type] = self._analyze_volatility(values, timestamps)
        
        except Exception as e:
            logger.error(f"Error analyzing period patterns: {e}")
        
        return patterns
    
    def _analyze_temporal_patterns(self, values: List[float], timestamps: List[str]) -> Dict[str, Any]:
        """Analyze temporal patterns in data"""
        if len(values) < 24:  # Need at least 24 data points
            return {}
        
        try:
            # Convert to pandas for easier analysis
            df = pd.DataFrame({
                'value': values,
                'timestamp': pd.to_datetime(timestamps)
            })
            
            # Hourly patterns
            df['hour'] = df['timestamp'].dt.hour
            hourly_patterns = df.groupby('hour')['value'].agg(['mean', 'std', 'count']).to_dict()
            
            # Daily patterns
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            daily_patterns = df.groupby('day_of_week')['value'].agg(['mean', 'std', 'count']).to_dict()
            
            # Peak detection
            peaks, _ = find_peaks(values, height=np.mean(values) + np.std(values))
            peak_times = [timestamps[i] for i in peaks] if len(peaks) > 0 else []
            
            return {
                'hourly_patterns': hourly_patterns,
                'daily_patterns': daily_patterns,
                'peak_times': peak_times,
                'peak_count': len(peaks),
                'data_points': len(values)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing temporal patterns: {e}")
            return {}
    
    def _analyze_seasonal_patterns(self, values: List[float], timestamps: List[str], period_days: int) -> Dict[str, Any]:
        """Analyze seasonal patterns in data"""
        if len(values) < 7:  # Need at least a week of data
            return {}
        
        try:
            df = pd.DataFrame({
                'value': values,
                'timestamp': pd.to_datetime(timestamps)
            })
            
            # Weekly seasonality
            df['week'] = df['timestamp'].dt.isocalendar().week
            weekly_patterns = df.groupby('week')['value'].agg(['mean', 'std', 'count']).to_dict()
            
            # Monthly seasonality (if we have enough data)
            monthly_patterns = {}
            if period_days >= 30:
                df['month'] = df['timestamp'].dt.month
                monthly_patterns = df.groupby('month')['value'].agg(['mean', 'std', 'count']).to_dict()
            
            # Business hours vs non-business hours
            df['hour'] = df['timestamp'].dt.hour
            business_hours = df[(df['hour'] >= self.business_hours['start']) & (df['hour'] <= self.business_hours['end'])]
            non_business_hours = df[(df['hour'] < self.business_hours['start']) | (df['hour'] > self.business_hours['end'])]
            
            business_avg = business_hours['value'].mean() if not business_hours.empty else 0
            non_business_avg = non_business_hours['value'].mean() if not non_business_hours.empty else 0
            
            return {
                'weekly_patterns': weekly_patterns,
                'monthly_patterns': monthly_patterns,
                'business_hours_avg': business_avg,
                'non_business_hours_avg': non_business_avg,
                'business_hours_ratio': business_avg / (business_avg + non_business_avg) if (business_avg + non_business_avg) > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing seasonal patterns: {e}")
            return {}
    
    def _analyze_advanced_trends(self, values: List[float], timestamps: List[str]) -> Dict[str, Any]:
        """Analyze advanced trends in data"""
        if len(values) < 10:
            return {}
        
        try:
            # Linear trend
            x = np.arange(len(values))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
            
            # Polynomial trend (quadratic)
            poly_coeffs = np.polyfit(x, values, 2)
            poly_trend = np.poly1d(poly_coeffs)
            
            # Moving averages
            window_sizes = [3, 7, 14]
            moving_averages = {}
            
            for window in window_sizes:
                if len(values) >= window:
                    ma = pd.Series(values).rolling(window=window).mean().tolist()
                    moving_averages[f'ma_{window}'] = ma
            
            # Trend strength
            trend_strength = abs(r_value)
            trend_direction = 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable'
            
            # Confidence in trend
            trend_confidence = min(100, max(0, r_value**2 * 100))
            
            return {
                'linear_slope': slope,
                'linear_intercept': intercept,
                'r_squared': r_value**2,
                'p_value': p_value,
                'trend_direction': trend_direction,
                'trend_strength': trend_strength,
                'trend_confidence': trend_confidence,
                'polynomial_coeffs': poly_coeffs.tolist(),
                'moving_averages': moving_averages,
                'data_points': len(values)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing advanced trends: {e}")
            return {}
    
    def _detect_advanced_anomalies(self, values: List[float], timestamps: List[str]) -> Dict[str, Any]:
        """Detect advanced anomalies in data"""
        if len(values) < 10:
            return {}
        
        try:
            anomalies = []
            
            # Statistical anomalies (Z-score)
            mean = np.mean(values)
            std = np.std(values)
            
            for i, value in enumerate(values):
                z_score = abs(value - mean) / std if std > 0 else 0
                
                if z_score > self.anomaly_threshold:
                    anomalies.append({
                        'timestamp': timestamps[i],
                        'value': value,
                        'z_score': z_score,
                        'severity': 'high' if z_score > 4 else 'medium',
                        'type': 'statistical_outlier'
                    })
            
            # Change point detection
            change_points = self._detect_change_points(values, timestamps)
            anomalies.extend(change_points)
            
            # Seasonal anomalies
            seasonal_anomalies = self._detect_seasonal_anomalies(values, timestamps)
            anomalies.extend(seasonal_anomalies)
            
            return {
                'anomalies': anomalies,
                'anomaly_count': len(anomalies),
                'high_severity_count': len([a for a in anomalies if a.get('severity') == 'high']),
                'anomaly_rate': len(anomalies) / len(values) if values else 0
            }
            
        except Exception as e:
            logger.error(f"Error detecting advanced anomalies: {e}")
            return {}
    
    def _detect_change_points(self, values: List[float], timestamps: List[str]) -> List[Dict[str, Any]]:
        """Detect change points in time series"""
        change_points = []
        
        try:
            if len(values) < 20:
                return change_points
            
            # Simple change point detection using rolling statistics
            window_size = min(7, len(values) // 3)
            
            for i in range(window_size, len(values) - window_size):
                before_window = values[i-window_size:i]
                after_window = values[i:i+window_size]
                
                before_mean = np.mean(before_window)
                after_mean = np.mean(after_window)
                
                # Detect significant change
                change_magnitude = abs(after_mean - before_mean) / before_mean if before_mean > 0 else 0
                
                if change_magnitude > 0.5:  # 50% change threshold
                    change_points.append({
                        'timestamp': timestamps[i],
                        'value': values[i],
                        'change_magnitude': change_magnitude,
                        'before_mean': before_mean,
                        'after_mean': after_mean,
                        'type': 'change_point'
                    })
            
        except Exception as e:
            logger.error(f"Error detecting change points: {e}")
        
        return change_points
    
    def _detect_seasonal_anomalies(self, values: List[float], timestamps: List[str]) -> List[Dict[str, Any]]:
        """Detect seasonal anomalies"""
        seasonal_anomalies = []
        
        try:
            if len(values) < 24:  # Need at least a day of hourly data
                return seasonal_anomalies
            
            df = pd.DataFrame({
                'value': values,
                'timestamp': pd.to_datetime(timestamps)
            })
            
            # Hourly seasonal decomposition
            df['hour'] = df['timestamp'].dt.hour
            hourly_stats = df.groupby('hour')['value'].agg(['mean', 'std']).to_dict()
            
            for i, (value, timestamp) in enumerate(zip(values, timestamps)):
                hour = pd.to_datetime(timestamp).hour
                
                if hour in hourly_stats:
                    expected_mean = hourly_stats[hour]['mean']
                    expected_std = hourly_stats[hour]['std']
                    
                    if expected_std > 0:
                        z_score = abs(value - expected_mean) / expected_std
                        
                        if z_score > self.anomaly_threshold:
                            seasonal_anomalies.append({
                                'timestamp': timestamp,
                                'value': value,
                                'expected_value': expected_mean,
                                'z_score': z_score,
                                'hour': hour,
                                'type': 'seasonal_anomaly'
                            })
            
        except Exception as e:
            logger.error(f"Error detecting seasonal anomalies: {e}")
        
        return seasonal_anomalies
    
    def _analyze_volatility(self, values: List[float], timestamps: List[str]) -> Dict[str, Any]:
        """Analyze volatility patterns"""
        if len(values) < 10:
            return {}
        
        try:
            # Calculate volatility using standard deviation
            volatility = np.std(values)
            mean_value = np.mean(values)
            
            # Calculate coefficient of variation
            cv = volatility / mean_value if mean_value > 0 else 0
            
            # Volatility classification
            if cv < 0.1:
                volatility_level = 'low'
            elif cv < 0.3:
                volatility_level = 'medium'
            else:
                volatility_level = 'high'
            
            return {
                'volatility': volatility,
                'coefficient_of_variation': cv,
                'volatility_level': volatility_level,
                'volatility_confidence': min(100, max(0, (1 - cv) * 100))
            }
            
        except Exception as e:
            logger.error(f"Error analyzing volatility: {e}")
            return {}
    
    def _analyze_business_intelligence(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze business intelligence patterns"""
        try:
            business_intelligence = {
                'business_hours_analysis': {},
                'workload_patterns': {},
                'resource_efficiency': {},
                'cost_optimization': {},
                'capacity_planning': {}
            }
            
            # Analyze business hours patterns
            for metric_type, data in historical_data.get('metrics', {}).items():
                if data:
                    values = [point['value'] for point in data]
                    timestamps = [point['timestamp'] for point in data]
                    
                    business_intelligence['business_hours_analysis'][metric_type] = self._analyze_business_hours_pattern(values, timestamps)
                    business_intelligence['workload_patterns'][metric_type] = self._analyze_workload_patterns(values, timestamps)
                    business_intelligence['resource_efficiency'][metric_type] = self._analyze_resource_efficiency(values, timestamps)
            
            # Cost optimization analysis
            business_intelligence['cost_optimization'] = self._analyze_cost_optimization(historical_data)
            
            # Capacity planning insights
            business_intelligence['capacity_planning'] = self._analyze_capacity_planning(historical_data)
            
            return business_intelligence
            
        except Exception as e:
            logger.error(f"Error analyzing business intelligence: {e}")
            return {}
    
    def _analyze_business_hours_pattern(self, values: List[float], timestamps: List[str]) -> Dict[str, Any]:
        """Analyze business hours vs non-business hours patterns"""
        if len(values) < 24:
            return {}
        
        try:
            df = pd.DataFrame({
                'value': values,
                'timestamp': pd.to_datetime(timestamps)
            })
            
            df['hour'] = df['timestamp'].dt.hour
            df['is_business_hours'] = (df['hour'] >= self.business_hours['start']) & (df['hour'] <= self.business_hours['end'])
            
            business_hours_data = df[df['is_business_hours']]['value']
            non_business_hours_data = df[~df['is_business_hours']]['value']
            
            business_avg = business_hours_data.mean() if not business_hours_data.empty else 0
            non_business_avg = non_business_hours_data.mean() if not non_business_hours_data.empty else 0
            
            business_std = business_hours_data.std() if not business_hours_data.empty else 0
            non_business_std = non_business_hours_data.std() if not non_business_hours_data.empty else 0
            
            # Calculate business hours utilization ratio
            total_avg = (business_avg + non_business_avg) / 2 if (business_avg + non_business_avg) > 0 else 0
            business_utilization_ratio = business_avg / total_avg if total_avg > 0 else 0
            
            return {
                'business_hours_avg': business_avg,
                'non_business_hours_avg': non_business_avg,
                'business_hours_std': business_std,
                'non_business_hours_std': non_business_std,
                'business_utilization_ratio': business_utilization_ratio,
                'business_hours_efficiency': min(100, business_utilization_ratio * 100),
                'has_business_pattern': business_utilization_ratio > 1.2  # 20% higher during business hours
            }
            
        except Exception as e:
            logger.error(f"Error analyzing business hours pattern: {e}")
            return {}
    
    def _analyze_workload_patterns(self, values: List[float], timestamps: List[str]) -> Dict[str, Any]:
        """Analyze workload patterns"""
        if len(values) < 10:
            return {}
        
        try:
            # Calculate workload characteristics
            mean_workload = np.mean(values)
            max_workload = np.max(values)
            min_workload = np.min(values)
            workload_range = max_workload - min_workload
            
            # Workload stability
            workload_stability = 1 - (np.std(values) / mean_workload) if mean_workload > 0 else 0
            
            # Peak detection
            peaks, _ = find_peaks(values, height=mean_workload + np.std(values))
            peak_count = len(peaks)
            
            # Workload classification
            if workload_stability > 0.8:
                workload_type = 'stable'
            elif peak_count > len(values) * 0.1:
                workload_type = 'spiky'
            else:
                workload_type = 'variable'
            
            return {
                'mean_workload': mean_workload,
                'max_workload': max_workload,
                'min_workload': min_workload,
                'workload_range': workload_range,
                'workload_stability': workload_stability,
                'peak_count': peak_count,
                'workload_type': workload_type,
                'utilization_efficiency': min(100, (mean_workload / max_workload) * 100) if max_workload > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing workload patterns: {e}")
            return {}
    
    def _analyze_resource_efficiency(self, values: List[float], timestamps: List[str]) -> Dict[str, Any]:
        """Analyze resource efficiency patterns"""
        if len(values) < 10:
            return {}
        
        try:
            mean_value = np.mean(values)
            std_value = np.std(values)
            
            # Efficiency metrics
            efficiency_score = min(100, max(0, (1 - std_value / mean_value) * 100)) if mean_value > 0 else 0
            
            # Resource utilization classification
            if mean_value < 20:
                utilization_level = 'underutilized'
            elif mean_value > 80:
                utilization_level = 'overutilized'
            else:
                utilization_level = 'optimal'
            
            # Efficiency trends
            if len(values) >= 20:
                recent_values = values[-10:]
                historical_values = values[:-10]
                
                recent_mean = np.mean(recent_values)
                historical_mean = np.mean(historical_values)
                
                efficiency_trend = 'improving' if recent_mean > historical_mean else 'declining' if recent_mean < historical_mean else 'stable'
            else:
                efficiency_trend = 'insufficient_data'
            
            return {
                'efficiency_score': efficiency_score,
                'utilization_level': utilization_level,
                'efficiency_trend': efficiency_trend,
                'mean_utilization': mean_value,
                'utilization_std': std_value,
                'efficiency_confidence': min(100, max(0, 100 - std_value))
            }
            
        except Exception as e:
            logger.error(f"Error analyzing resource efficiency: {e}")
            return {}
    
    def _analyze_cost_optimization(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze cost optimization opportunities"""
        try:
            cost_analysis = {
                'potential_savings': {},
                'optimization_opportunities': [],
                'cost_efficiency_score': 0,
                'recommended_actions': []
            }
            
            total_potential_savings = 0
            
            for metric_type, data in historical_data.get('metrics', {}).items():
                if not data:
                    continue
                
                values = [point['value'] for point in data]
                mean_value = np.mean(values)
                
                # Calculate potential savings based on underutilization
                if mean_value < 30:  # Underutilized
                    potential_savings = (30 - mean_value) / 30 * 100  # Percentage savings
                    cost_analysis['potential_savings'][metric_type] = {
                        'current_utilization': mean_value,
                        'potential_savings_percent': potential_savings,
                        'optimization_type': 'underutilization'
                    }
                    total_potential_savings += potential_savings
                
                elif mean_value > 80:  # Overutilized
                    cost_analysis['potential_savings'][metric_type] = {
                        'current_utilization': mean_value,
                        'potential_savings_percent': 0,
                        'optimization_type': 'overutilization',
                        'recommendation': 'scale_up_needed'
                    }
            
            cost_analysis['cost_efficiency_score'] = min(100, max(0, 100 - total_potential_savings))
            
            # Generate optimization opportunities
            for metric_type, savings in cost_analysis['potential_savings'].items():
                if savings.get('potential_savings_percent', 0) > 20:
                    cost_analysis['optimization_opportunities'].append({
                        'metric_type': metric_type,
                        'savings_percent': savings['potential_savings_percent'],
                        'action': 'scale_down' if savings['optimization_type'] == 'underutilization' else 'scale_up'
                    })
            
            return cost_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing cost optimization: {e}")
            return {}
    
    def _analyze_capacity_planning(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze capacity planning insights"""
        try:
            capacity_analysis = {
                'current_capacity': {},
                'capacity_trends': {},
                'capacity_recommendations': [],
                'scaling_insights': {}
            }
            
            for metric_type, data in historical_data.get('metrics', {}).items():
                if not data or len(data) < 10:
                    continue
                
                values = [point['value'] for point in data]
                timestamps = [point['timestamp'] for point in data]
                
                # Current capacity analysis
                current_avg = np.mean(values[-10:])  # Last 10 data points
                historical_avg = np.mean(values)
                
                capacity_analysis['current_capacity'][metric_type] = {
                    'current_utilization': current_avg,
                    'historical_avg': historical_avg,
                    'capacity_status': 'adequate' if current_avg < 70 else 'near_limit' if current_avg < 85 else 'critical'
                }
                
                # Capacity trends
                if len(values) >= 20:
                    recent_trend = np.polyfit(range(len(values[-10:])), values[-10:], 1)[0]
                    capacity_analysis['capacity_trends'][metric_type] = {
                        'trend_direction': 'increasing' if recent_trend > 0 else 'decreasing' if recent_trend < 0 else 'stable',
                        'trend_magnitude': abs(recent_trend),
                        'projected_utilization': min(100, current_avg + recent_trend * 7)  # 7 days projection
                    }
                
                # Scaling insights
                if current_avg > 80:
                    capacity_analysis['scaling_insights'][metric_type] = {
                        'scaling_needed': True,
                        'urgency': 'high' if current_avg > 90 else 'medium',
                        'recommended_action': 'scale_up_immediately' if current_avg > 90 else 'scale_up_soon'
                    }
                elif current_avg < 30:
                    capacity_analysis['scaling_insights'][metric_type] = {
                        'scaling_needed': True,
                        'urgency': 'low',
                        'recommended_action': 'scale_down'
                    }
            
            return capacity_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing capacity planning: {e}")
            return {}
    
    def _generate_predictive_insights(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate predictive insights using historical data"""
        try:
            predictive_insights = {
                'trend_predictions': {},
                'anomaly_predictions': {},
                'capacity_forecasts': {},
                'optimization_predictions': {},
                'confidence_scores': {}
            }
            
            for metric_type, data in historical_data.get('metrics', {}).items():
                if not data or len(data) < 20:
                    continue
                
                values = [point['value'] for point in data]
                timestamps = [point['timestamp'] for point in data]
                
                # Trend predictions
                trend_prediction = self._predict_trend(values, timestamps)
                predictive_insights['trend_predictions'][metric_type] = trend_prediction
                
                # Anomaly predictions
                anomaly_prediction = self._predict_anomalies(values, timestamps)
                predictive_insights['anomaly_predictions'][metric_type] = anomaly_prediction
                
                # Capacity forecasts
                capacity_forecast = self._forecast_capacity(values, timestamps)
                predictive_insights['capacity_forecasts'][metric_type] = capacity_forecast
                
                # Optimization predictions
                optimization_prediction = self._predict_optimization_opportunities(values, timestamps)
                predictive_insights['optimization_predictions'][metric_type] = optimization_prediction
            
            # Calculate overall confidence scores
            predictive_insights['confidence_scores'] = self._calculate_predictive_confidence(predictive_insights)
            
            return predictive_insights
            
        except Exception as e:
            logger.error(f"Error generating predictive insights: {e}")
            return {}
    
    def _predict_trend(self, values: List[float], timestamps: List[str]) -> Dict[str, Any]:
        """Predict future trends based on historical data"""
        try:
            if len(values) < 10:
                return {'prediction': 'insufficient_data'}
            
            # Linear regression for trend prediction
            x = np.arange(len(values))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
            
            # Predict next 7 days
            future_days = 7
            future_x = np.arange(len(values), len(values) + future_days)
            future_values = slope * future_x + intercept
            
            # Calculate prediction confidence
            confidence = min(100, max(0, r_value**2 * 100))
            
            return {
                'prediction_type': 'linear_trend',
                'slope': slope,
                'intercept': intercept,
                'r_squared': r_value**2,
                'confidence': confidence,
                'predicted_values': future_values.tolist(),
                'trend_direction': 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable',
                'prediction_horizon_days': future_days
            }
            
        except Exception as e:
            logger.error(f"Error predicting trend: {e}")
            return {'prediction': 'error'}
    
    def _predict_anomalies(self, values: List[float], timestamps: List[str]) -> Dict[str, Any]:
        """Predict potential anomalies"""
        try:
            if len(values) < 20:
                return {'prediction': 'insufficient_data'}
            
            # Calculate anomaly probability based on historical patterns
            mean_value = np.mean(values)
            std_value = np.std(values)
            
            # Calculate how many standard deviations the recent values are from mean
            recent_values = values[-5:]  # Last 5 values
            recent_avg = np.mean(recent_values)
            
            z_score = abs(recent_avg - mean_value) / std_value if std_value > 0 else 0
            
            # Predict anomaly probability
            anomaly_probability = min(100, max(0, z_score * 20))  # Scale z-score to probability
            
            return {
                'anomaly_probability': anomaly_probability,
                'risk_level': 'high' if anomaly_probability > 70 else 'medium' if anomaly_probability > 30 else 'low',
                'confidence': min(100, max(0, 100 - z_score * 10)),
                'prediction_horizon_hours': 24
            }
            
        except Exception as e:
            logger.error(f"Error predicting anomalies: {e}")
            return {'prediction': 'error'}
    
    def _forecast_capacity(self, values: List[float], timestamps: List[str]) -> Dict[str, Any]:
        """Forecast capacity requirements"""
        try:
            if len(values) < 20:
                return {'forecast': 'insufficient_data'}
            
            # Simple capacity forecasting
            recent_avg = np.mean(values[-10:])
            historical_avg = np.mean(values)
            
            # Project capacity needs
            growth_rate = (recent_avg - historical_avg) / historical_avg if historical_avg > 0 else 0
            
            # Forecast for next 30 days
            forecast_days = 30
            projected_capacity = recent_avg * (1 + growth_rate * forecast_days / 30)
            
            return {
                'current_capacity_utilization': recent_avg,
                'projected_capacity_utilization': projected_capacity,
                'growth_rate': growth_rate,
                'forecast_horizon_days': forecast_days,
                'capacity_status': 'adequate' if projected_capacity < 70 else 'near_limit' if projected_capacity < 85 else 'critical',
                'confidence': min(100, max(0, 100 - abs(growth_rate) * 100))
            }
            
        except Exception as e:
            logger.error(f"Error forecasting capacity: {e}")
            return {'forecast': 'error'}
    
    def _predict_optimization_opportunities(self, values: List[float], timestamps: List[str]) -> Dict[str, Any]:
        """Predict optimization opportunities"""
        try:
            if len(values) < 10:
                return {'prediction': 'insufficient_data'}
            
            mean_value = np.mean(values)
            recent_avg = np.mean(values[-5:])
            
            # Predict optimization opportunities
            if recent_avg < 30:
                optimization_type = 'underutilization'
                opportunity_score = (30 - recent_avg) / 30 * 100
            elif recent_avg > 80:
                optimization_type = 'overutilization'
                opportunity_score = (recent_avg - 80) / 20 * 100
            else:
                optimization_type = 'optimal'
                opportunity_score = 0
            
            return {
                'optimization_type': optimization_type,
                'opportunity_score': opportunity_score,
                'current_utilization': recent_avg,
                'recommended_action': 'scale_down' if optimization_type == 'underutilization' else 'scale_up' if optimization_type == 'overutilization' else 'maintain',
                'confidence': min(100, max(0, 100 - abs(recent_avg - mean_value)))
            }
            
        except Exception as e:
            logger.error(f"Error predicting optimization opportunities: {e}")
            return {'prediction': 'error'}
    
    def _calculate_predictive_confidence(self, predictive_insights: Dict[str, Any]) -> Dict[str, float]:
        """Calculate confidence scores for predictive insights"""
        try:
            confidence_scores = {
                'trend_confidence': 0,
                'anomaly_confidence': 0,
                'capacity_confidence': 0,
                'optimization_confidence': 0,
                'overall_confidence': 0
            }
            
            # Calculate confidence for each prediction type
            trend_confidences = []
            anomaly_confidences = []
            capacity_confidences = []
            optimization_confidences = []
            
            for metric_type, prediction in predictive_insights.get('trend_predictions', {}).items():
                if 'confidence' in prediction:
                    trend_confidences.append(prediction['confidence'])
            
            for metric_type, prediction in predictive_insights.get('anomaly_predictions', {}).items():
                if 'confidence' in prediction:
                    anomaly_confidences.append(prediction['confidence'])
            
            for metric_type, forecast in predictive_insights.get('capacity_forecasts', {}).items():
                if 'confidence' in forecast:
                    capacity_confidences.append(forecast['confidence'])
            
            for metric_type, prediction in predictive_insights.get('optimization_predictions', {}).items():
                if 'confidence' in prediction:
                    optimization_confidences.append(prediction['confidence'])
            
            # Calculate average confidences
            confidence_scores['trend_confidence'] = np.mean(trend_confidences) if trend_confidences else 0
            confidence_scores['anomaly_confidence'] = np.mean(anomaly_confidences) if anomaly_confidences else 0
            confidence_scores['capacity_confidence'] = np.mean(capacity_confidences) if capacity_confidences else 0
            confidence_scores['optimization_confidence'] = np.mean(optimization_confidences) if optimization_confidences else 0
            
            # Calculate overall confidence
            overall_confidences = [confidence_scores['trend_confidence'], confidence_scores['anomaly_confidence'], 
                                 confidence_scores['capacity_confidence'], confidence_scores['optimization_confidence']]
            confidence_scores['overall_confidence'] = np.mean(overall_confidences) if overall_confidences else 0
            
            return confidence_scores
            
        except Exception as e:
            logger.error(f"Error calculating predictive confidence: {e}")
            return {}
    
    def _analyze_efficiency_patterns(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze efficiency patterns across the cluster"""
        try:
            efficiency_analysis = {
                'overall_efficiency': {},
                'resource_efficiency': {},
                'workload_efficiency': {},
                'cost_efficiency': {},
                'efficiency_recommendations': []
            }
            
            # Calculate overall efficiency metrics
            total_metrics = 0
            total_efficiency = 0
            
            for metric_type, data in historical_data.get('metrics', {}).items():
                if not data:
                    continue
                
                values = [point['value'] for point in data]
                mean_value = np.mean(values)
                std_value = np.std(values)
                
                # Calculate efficiency score for this metric
                efficiency_score = min(100, max(0, (1 - std_value / mean_value) * 100)) if mean_value > 0 else 0
                
                efficiency_analysis['resource_efficiency'][metric_type] = {
                    'efficiency_score': efficiency_score,
                    'mean_utilization': mean_value,
                    'utilization_std': std_value,
                    'efficiency_level': 'high' if efficiency_score > 80 else 'medium' if efficiency_score > 60 else 'low'
                }
                
                total_metrics += 1
                total_efficiency += efficiency_score
            
            # Overall efficiency
            if total_metrics > 0:
                overall_efficiency = total_efficiency / total_metrics
                efficiency_analysis['overall_efficiency'] = {
                    'score': overall_efficiency,
                    'level': 'high' if overall_efficiency > 80 else 'medium' if overall_efficiency > 60 else 'low',
                    'metric_count': total_metrics
                }
            
            # Generate efficiency recommendations
            efficiency_analysis['efficiency_recommendations'] = self._generate_efficiency_recommendations(efficiency_analysis)
            
            return efficiency_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing efficiency patterns: {e}")
            return {}
    
    def _generate_efficiency_recommendations(self, efficiency_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate efficiency improvement recommendations"""
        recommendations = []
        
        try:
            overall_efficiency = efficiency_analysis.get('overall_efficiency', {}).get('score', 0)
            
            if overall_efficiency < 60:
                recommendations.append({
                    'type': 'efficiency_improvement',
                    'priority': 'high',
                    'description': 'Overall cluster efficiency is low. Consider resource optimization.',
                    'action': 'review_resource_allocation'
                })
            
            # Check individual resource efficiency
            for metric_type, efficiency in efficiency_analysis.get('resource_efficiency', {}).items():
                efficiency_score = efficiency.get('efficiency_score', 0)
                
                if efficiency_score < 50:
                    recommendations.append({
                        'type': 'resource_optimization',
                        'priority': 'high',
                        'resource': metric_type,
                        'description': f'{metric_type} efficiency is very low ({efficiency_score:.1f}%)',
                        'action': 'optimize_resource_usage',
                        'current_score': efficiency_score
                    })
                elif efficiency_score < 70:
                    recommendations.append({
                        'type': 'resource_optimization',
                        'priority': 'medium',
                        'resource': metric_type,
                        'description': f'{metric_type} efficiency can be improved ({efficiency_score:.1f}%)',
                        'action': 'review_resource_usage',
                        'current_score': efficiency_score
                    })
            
        except Exception as e:
            logger.error(f"Error generating efficiency recommendations: {e}")
        
        return recommendations
    
    def _calculate_advanced_confidence(self, analysis: Dict[str, Any]) -> Dict[str, float]:
        """Calculate advanced confidence metrics for the analysis"""
        try:
            confidence_metrics = {
                'pattern_confidence': 0,
                'trend_confidence': 0,
                'anomaly_confidence': 0,
                'business_confidence': 0,
                'overall_confidence': 0
            }
            
            # Calculate confidence for different analysis components
            pattern_confidences = []
            trend_confidences = []
            anomaly_confidences = []
            business_confidences = []
            
            # Pattern confidence
            for period, patterns in analysis.get('advanced_patterns', {}).items():
                for metric_type, pattern_data in patterns.get('temporal_patterns', {}).items():
                    if 'data_points' in pattern_data:
                        confidence = min(100, pattern_data['data_points'] / 100)  # More data = higher confidence
                        pattern_confidences.append(confidence)
            
            # Trend confidence
            for period, patterns in analysis.get('advanced_patterns', {}).items():
                for metric_type, trend_data in patterns.get('trend_analysis', {}).items():
                    if 'trend_confidence' in trend_data:
                        trend_confidences.append(trend_data['trend_confidence'])
            
            # Anomaly confidence
            for period, patterns in analysis.get('advanced_patterns', {}).items():
                for metric_type, anomaly_data in patterns.get('anomaly_detection', {}).items():
                    if 'anomaly_count' in anomaly_data and 'data_points' in patterns.get('temporal_patterns', {}).get(metric_type, {}):
                        data_points = patterns['temporal_patterns'][metric_type]['data_points']
                        anomaly_rate = anomaly_data['anomaly_count'] / data_points if data_points > 0 else 0
                        confidence = max(0, 100 - anomaly_rate * 100)  # Lower anomaly rate = higher confidence
                        anomaly_confidences.append(confidence)
            
            # Business confidence
            business_intelligence = analysis.get('business_intelligence', {})
            for metric_type, business_data in business_intelligence.get('business_hours_analysis', {}).items():
                if 'business_hours_efficiency' in business_data:
                    business_confidences.append(business_data['business_hours_efficiency'])
            
            # Calculate average confidences
            confidence_metrics['pattern_confidence'] = np.mean(pattern_confidences) if pattern_confidences else 0
            confidence_metrics['trend_confidence'] = np.mean(trend_confidences) if trend_confidences else 0
            confidence_metrics['anomaly_confidence'] = np.mean(anomaly_confidences) if anomaly_confidences else 0
            confidence_metrics['business_confidence'] = np.mean(business_confidences) if business_confidences else 0
            
            # Overall confidence
            overall_confidences = [confidence_metrics['pattern_confidence'], confidence_metrics['trend_confidence'],
                                 confidence_metrics['anomaly_confidence'], confidence_metrics['business_confidence']]
            confidence_metrics['overall_confidence'] = np.mean(overall_confidences) if overall_confidences else 0
            
            return confidence_metrics
            
        except Exception as e:
            logger.error(f"Error calculating advanced confidence: {e}")
            return {}
    
    def _generate_advanced_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate advanced recommendations based on analysis"""
        recommendations = []
        
        try:
            # Efficiency recommendations
            efficiency_analysis = analysis.get('efficiency_analysis', {})
            for recommendation in efficiency_analysis.get('efficiency_recommendations', []):
                recommendations.append(recommendation)
            
            # Business intelligence recommendations
            business_intelligence = analysis.get('business_intelligence', {})
            for metric_type, business_data in business_intelligence.get('business_hours_analysis', {}).items():
                if not business_data.get('has_business_pattern', False):
                    recommendations.append({
                        'type': 'business_pattern_optimization',
                        'priority': 'medium',
                        'resource': metric_type,
                        'description': f'No clear business hours pattern detected for {metric_type}',
                        'action': 'review_business_hours_utilization'
                    })
            
            # Predictive insights recommendations
            predictive_insights = analysis.get('predictive_insights', {})
            for metric_type, prediction in predictive_insights.get('trend_predictions', {}).items():
                if prediction.get('trend_direction') == 'increasing' and prediction.get('confidence', 0) > 70:
                    recommendations.append({
                        'type': 'capacity_planning',
                        'priority': 'high',
                        'resource': metric_type,
                        'description': f'Increasing trend detected for {metric_type} with high confidence',
                        'action': 'plan_capacity_increase',
                        'confidence': prediction.get('confidence', 0)
                    })
            
            # Anomaly recommendations
            for metric_type, anomaly_data in predictive_insights.get('anomaly_predictions', {}).items():
                if anomaly_data.get('anomaly_probability', 0) > 50:
                    recommendations.append({
                        'type': 'anomaly_monitoring',
                        'priority': 'high',
                        'resource': metric_type,
                        'description': f'High anomaly probability detected for {metric_type}',
                        'action': 'monitor_closely',
                        'probability': anomaly_data.get('anomaly_probability', 0)
                    })
            
            # Cost optimization recommendations
            cost_analysis = business_intelligence.get('cost_optimization', {})
            for metric_type, savings in cost_analysis.get('potential_savings', {}).items():
                if savings.get('potential_savings_percent', 0) > 30:
                    recommendations.append({
                        'type': 'cost_optimization',
                        'priority': 'high',
                        'resource': metric_type,
                        'description': f'High potential savings ({savings["potential_savings_percent"]:.1f}%) for {metric_type}',
                        'action': 'implement_optimization',
                        'savings_percent': savings.get('potential_savings_percent', 0)
                    })
            
        except Exception as e:
            logger.error(f"Error generating advanced recommendations: {e}")
        
        return recommendations 