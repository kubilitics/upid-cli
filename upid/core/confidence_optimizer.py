"""
Confidence-Based Optimization Engine for UPID
Implements sophisticated optimization with risk assessment, safety boundaries, and simulation
Features:
- Multi-factor confidence scoring
- Risk assessment and safety boundaries
- Rollback plans and simulation
- Business impact correlation
- Optimization recommendations with confidence levels
"""

import os
import subprocess
import json
import yaml
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Set
import logging
import numpy as np
from dataclasses import dataclass
from enum import Enum
import copy

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """Risk levels for optimization operations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class OptimizationType(Enum):
    """Types of optimization operations"""
    SCALE_DOWN = "scale_down"
    SCALE_UP = "scale_up"
    RESOURCE_LIMITS = "resource_limits"
    REPLICA_ADJUSTMENT = "replica_adjustment"
    NODE_DRAIN = "node_drain"
    POD_SCHEDULING = "pod_scheduling"

@dataclass
class SafetyBoundary:
    """Safety boundaries for optimization operations"""
    min_replicas: int = 1
    max_cpu_utilization: float = 80.0
    max_memory_utilization: float = 80.0
    min_available_nodes: int = 1
    max_risk_score: float = 0.7
    business_hours_buffer: float = 0.2  # 20% buffer during business hours

@dataclass
class OptimizationPlan:
    """Optimization plan with confidence and risk assessment"""
    operation_type: OptimizationType
    target_resource: str
    current_value: Any
    proposed_value: Any
    confidence_score: float
    risk_level: RiskLevel
    risk_score: float
    potential_savings: float
    business_impact: Dict[str, Any]
    rollback_plan: Dict[str, Any]
    safety_boundaries: SafetyBoundary
    simulation_results: Dict[str, Any]

class ConfidenceOptimizer:
    """Confidence-based optimization engine with risk assessment"""
    
    def __init__(self):
        """Initialize the confidence optimizer"""
        self.safety_boundaries = SafetyBoundary()
        self.optimization_history = []
        self.risk_models = self._initialize_risk_models()
        
        # Confidence thresholds
        self.high_confidence_threshold = 0.8
        self.medium_confidence_threshold = 0.6
        self.low_confidence_threshold = 0.4
        
        # Risk thresholds
        self.low_risk_threshold = 0.3
        self.medium_risk_threshold = 0.6
        self.high_risk_threshold = 0.8
        
    def _initialize_risk_models(self) -> Dict[str, Any]:
        """Initialize risk assessment models"""
        return {
            'resource_utilization': {
                'high_utilization_risk': 0.8,
                'low_utilization_opportunity': 0.3
            },
            'business_impact': {
                'business_hours_risk': 0.7,
                'critical_service_risk': 0.9
            },
            'stability': {
                'recent_restarts_risk': 0.6,
                'health_check_failures_risk': 0.8
            },
            'dependencies': {
                'dependency_chain_risk': 0.5,
                'service_dependency_risk': 0.7
            }
        }
    
    def generate_optimization_plans(self, cluster_id: str, 
                                  intelligent_metrics: Dict[str, Any],
                                  historical_data: Dict[str, Any]) -> List[OptimizationPlan]:
        """Generate confidence-based optimization plans"""
        try:
            optimization_plans = []
            
            # Analyze current cluster state
            cluster_state = self._analyze_cluster_state(intelligent_metrics)
            
            # Generate different types of optimization plans
            plans = []
            
            # Scale down optimizations
            scale_down_plans = self._generate_scale_down_plans(cluster_state, intelligent_metrics)
            plans.extend(scale_down_plans)
            
            # Resource limit optimizations
            resource_plans = self._generate_resource_optimization_plans(cluster_state, intelligent_metrics)
            plans.extend(resource_plans)
            
            # Replica optimization plans
            replica_plans = self._generate_replica_optimization_plans(cluster_state, intelligent_metrics)
            plans.extend(replica_plans)
            
            # Node optimization plans
            node_plans = self._generate_node_optimization_plans(cluster_state, intelligent_metrics)
            plans.extend(node_plans)
            
            # Assess confidence and risk for each plan
            for plan in plans:
                confidence_score = self._calculate_confidence_score(plan, intelligent_metrics, historical_data)
                risk_score = self._calculate_risk_score(plan, cluster_state, intelligent_metrics)
                risk_level = self._determine_risk_level(risk_score)
                
                # Apply safety boundaries
                if self._check_safety_boundaries(plan, risk_score):
                    optimization_plan = OptimizationPlan(
                        operation_type=plan['type'],
                        target_resource=plan['target'],
                        current_value=plan['current_value'],
                        proposed_value=plan['proposed_value'],
                        confidence_score=confidence_score,
                        risk_level=risk_level,
                        risk_score=risk_score,
                        potential_savings=plan.get('potential_savings', 0),
                        business_impact=self._assess_business_impact(plan, intelligent_metrics),
                        rollback_plan=self._generate_rollback_plan(plan),
                        safety_boundaries=self.safety_boundaries,
                        simulation_results=self._simulate_optimization(plan, cluster_state)
                    )
                    optimization_plans.append(optimization_plan)
            
            # Sort by confidence/risk ratio
            optimization_plans.sort(key=lambda x: x.confidence_score / (x.risk_score + 0.1), reverse=True)
            
            return optimization_plans
            
        except Exception as e:
            logger.error(f"Error generating optimization plans: {e}")
            return []
    
    def _analyze_cluster_state(self, intelligent_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current cluster state for optimization"""
        cluster_state = {
            'pods': [],
            'nodes': [],
            'services': [],
            'resource_utilization': {},
            'business_activity': {},
            'stability_metrics': {}
        }
        
        # Extract pod information
        intelligent_pods = intelligent_metrics.get('intelligent_pods', [])
        for pod in intelligent_pods:
            pod_state = {
                'name': pod.get('name', ''),
                'namespace': pod.get('namespace', ''),
                'status': pod.get('status', ''),
                'activity_analysis': pod.get('activity_analysis', 'unknown'),
                'resource_analysis': pod.get('resource_analysis', {}),
                'idle_patterns': pod.get('idle_patterns', {}),
                'business_context': pod.get('business_context', {}),
                'intelligence_score': pod.get('intelligence_score', 0)
            }
            cluster_state['pods'].append(pod_state)
        
        # Extract business activity
        business_activity = intelligent_metrics.get('business_activity', {})
        cluster_state['business_activity'] = business_activity
        
        # Extract resource correlation
        resource_correlation = intelligent_metrics.get('resource_work_correlation', {})
        cluster_state['resource_utilization'] = resource_correlation
        
        return cluster_state
    
    def _generate_scale_down_plans(self, cluster_state: Dict[str, Any], 
                                 intelligent_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate scale down optimization plans"""
        plans = []
        
        idle_analysis = intelligent_metrics.get('idle_analysis', {})
        idle_pods = idle_analysis.get('idle_pods', [])
        
        for pod in idle_pods:
            if pod.get('confidence', 0) > self.high_confidence_threshold:
                plan = {
                    'type': OptimizationType.SCALE_DOWN,
                    'target': f"{pod.get('namespace', '')}/{pod.get('name', '')}",
                    'current_value': 1,  # Assume 1 replica
                    'proposed_value': 0,  # Scale to 0
                    'potential_savings': self._calculate_pod_savings(pod),
                    'reason': 'high_confidence_idle_detection',
                    'confidence_factors': ['idle_score', 'business_activity', 'resource_usage']
                }
                plans.append(plan)
        
        return plans
    
    def _generate_resource_optimization_plans(self, cluster_state: Dict[str, Any],
                                           intelligent_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate resource optimization plans"""
        plans = []
        
        for pod in cluster_state['pods']:
            resource_analysis = pod.get('resource_analysis', {})
            efficiency = resource_analysis.get('resource_efficiency', 'unknown')
            
            if efficiency == 'underutilized':
                # Propose resource limit reduction
                current_cpu = resource_analysis.get('cpu', 0)
                current_memory = resource_analysis.get('memory', 0)
                
                if current_cpu > 0:
                    proposed_cpu = max(0.1, current_cpu * 0.5)  # Reduce by 50%
                    plan = {
                        'type': OptimizationType.RESOURCE_LIMITS,
                        'target': f"{pod['namespace']}/{pod['name']}",
                        'current_value': {'cpu': current_cpu},
                        'proposed_value': {'cpu': proposed_cpu},
                        'potential_savings': (current_cpu - proposed_cpu) * 0.1,  # Estimate cost
                        'reason': 'underutilized_cpu',
                        'confidence_factors': ['resource_efficiency', 'activity_analysis']
                    }
                    plans.append(plan)
                
                if current_memory > 50:  # More than 50MB
                    proposed_memory = max(50, current_memory * 0.7)  # Reduce by 30%
                    plan = {
                        'type': OptimizationType.RESOURCE_LIMITS,
                        'target': f"{pod['namespace']}/{pod['name']}",
                        'current_value': {'memory': current_memory},
                        'proposed_value': {'memory': proposed_memory},
                        'potential_savings': (current_memory - proposed_memory) * 0.01,  # Estimate cost
                        'reason': 'underutilized_memory',
                        'confidence_factors': ['resource_efficiency', 'activity_analysis']
                    }
                    plans.append(plan)
        
        return plans
    
    def _generate_replica_optimization_plans(self, cluster_state: Dict[str, Any],
                                          intelligent_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate replica optimization plans"""
        plans = []
        
        # Group pods by deployment/service
        deployments = {}
        for pod in cluster_state['pods']:
            name = pod.get('name', '')
            # Extract deployment name from pod name (e.g., "app-12345-abc" -> "app")
            if '-' in name:
                deployment_name = name.rsplit('-', 2)[0]
                if deployment_name not in deployments:
                    deployments[deployment_name] = []
                deployments[deployment_name].append(pod)
        
        # Analyze each deployment
        for deployment_name, pods in deployments.items():
            idle_count = sum(1 for pod in pods if pod.get('activity_analysis') == 'idle')
            total_count = len(pods)
            
            if idle_count > 0 and idle_count / total_count > 0.5:  # More than 50% idle
                plan = {
                    'type': OptimizationType.REPLICA_ADJUSTMENT,
                    'target': deployment_name,
                    'current_value': total_count,
                    'proposed_value': max(1, total_count - idle_count),
                    'potential_savings': idle_count * 0.1,  # Estimate cost per replica
                    'reason': 'deployment_idle_replicas',
                    'confidence_factors': ['idle_ratio', 'deployment_stability']
                }
                plans.append(plan)
        
        return plans
    
    def _generate_node_optimization_plans(self, cluster_state: Dict[str, Any],
                                        intelligent_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate node optimization plans"""
        plans = []
        
        # This would require node-level analysis
        # For now, return empty list as node optimization is complex
        return plans
    
    def _calculate_confidence_score(self, plan: Dict[str, Any], 
                                 intelligent_metrics: Dict[str, Any],
                                 historical_data: Dict[str, Any]) -> float:
        """Calculate confidence score for optimization plan"""
        confidence_factors = plan.get('confidence_factors', [])
        base_confidence = 0.5
        
        # Factor in business activity
        business_activity = intelligent_metrics.get('business_activity', {})
        business_ratio = business_activity.get('business_activity_ratio', 0)
        
        if 'business_activity' in confidence_factors:
            if business_ratio < 0.3:  # Low business activity
                base_confidence += 0.2
            elif business_ratio > 0.7:  # High business activity
                base_confidence -= 0.1
        
        # Factor in resource efficiency
        resource_correlation = intelligent_metrics.get('resource_work_correlation', {})
        efficiency_score = resource_correlation.get('efficiency_score', 0)
        
        if 'resource_efficiency' in confidence_factors:
            if efficiency_score < 50:  # Low efficiency
                base_confidence += 0.2
            elif efficiency_score > 80:  # High efficiency
                base_confidence -= 0.1
        
        # Factor in idle patterns
        idle_analysis = intelligent_metrics.get('idle_analysis', {})
        idle_count = idle_analysis.get('idle_count', 0)
        total_pods = business_activity.get('total_pods', 1)
        
        if 'idle_score' in confidence_factors:
            idle_ratio = idle_count / total_pods if total_pods > 0 else 0
            if idle_ratio > 0.3:  # High idle ratio
                base_confidence += 0.2
        
        # Factor in historical stability
        if historical_data and 'metrics' in historical_data:
            # Check for recent anomalies or instability
            base_confidence += 0.1  # Assume stable if we have historical data
        
        return min(1.0, max(0.0, base_confidence))
    
    def _calculate_risk_score(self, plan: Dict[str, Any], 
                            cluster_state: Dict[str, Any],
                            intelligent_metrics: Dict[str, Any]) -> float:
        """Calculate risk score for optimization plan"""
        risk_score = 0.0
        
        # Business hours risk
        current_hour = datetime.utcnow().hour
        is_business_hours = 9 <= current_hour <= 17
        
        if is_business_hours:
            risk_score += self.risk_models['business_impact']['business_hours_risk']
        
        # Critical service risk
        target = plan.get('target', '')
        if any(critical in target.lower() for critical in ['database', 'redis', 'postgres', 'mysql']):
            risk_score += self.risk_models['business_impact']['critical_service_risk']
        
        # Resource utilization risk
        operation_type = plan.get('type')
        if operation_type == OptimizationType.SCALE_DOWN:
            # Higher risk for scale down operations
            risk_score += 0.3
        
        # Dependency risk
        if 'dependency' in plan.get('reason', ''):
            risk_score += self.risk_models['dependencies']['dependency_chain_risk']
        
        # Stability risk (simplified)
        # In a real implementation, you'd check recent restarts, health check failures, etc.
        risk_score += 0.1  # Base stability risk
        
        return min(1.0, risk_score)
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level based on risk score"""
        if risk_score <= self.low_risk_threshold:
            return RiskLevel.LOW
        elif risk_score <= self.medium_risk_threshold:
            return RiskLevel.MEDIUM
        elif risk_score <= self.high_risk_threshold:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def _check_safety_boundaries(self, plan: Dict[str, Any], risk_score: float) -> bool:
        """Check if plan meets safety boundaries"""
        # Check risk score boundary
        if risk_score > self.safety_boundaries.max_risk_score:
            return False
        
        # Check business hours buffer
        current_hour = datetime.utcnow().hour
        is_business_hours = 9 <= current_hour <= 17
        
        if is_business_hours:
            # Apply stricter boundaries during business hours
            if risk_score > self.safety_boundaries.max_risk_score * (1 - self.safety_boundaries.business_hours_buffer):
                return False
        
        return True
    
    def _assess_business_impact(self, plan: Dict[str, Any], 
                              intelligent_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Assess business impact of optimization plan"""
        business_impact = {
            'potential_cost_savings': plan.get('potential_savings', 0),
            'service_availability_risk': 0.0,
            'performance_impact': 'low',
            'business_hours_impact': 'minimal'
        }
        
        # Assess service availability risk
        operation_type = plan.get('type')
        if operation_type == OptimizationType.SCALE_DOWN:
            business_impact['service_availability_risk'] = 0.3
            business_impact['performance_impact'] = 'medium'
        elif operation_type == OptimizationType.RESOURCE_LIMITS:
            business_impact['service_availability_risk'] = 0.1
            business_impact['performance_impact'] = 'low'
        
        # Assess business hours impact
        current_hour = datetime.utcnow().hour
        is_business_hours = 9 <= current_hour <= 17
        
        if is_business_hours:
            business_impact['business_hours_impact'] = 'moderate'
        else:
            business_impact['business_hours_impact'] = 'minimal'
        
        return business_impact
    
    def _generate_rollback_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate rollback plan for optimization"""
        rollback_plan = {
            'trigger_conditions': [],
            'rollback_actions': [],
            'monitoring_metrics': [],
            'timeout_seconds': 300  # 5 minutes
        }
        
        operation_type = plan.get('type')
        
        if operation_type == OptimizationType.SCALE_DOWN:
            rollback_plan['trigger_conditions'] = [
                'pod_unavailable',
                'service_unreachable',
                'error_rate_increase'
            ]
            rollback_plan['rollback_actions'] = [
                f"kubectl scale deployment {plan['target']} --replicas={plan['current_value']}"
            ]
            rollback_plan['monitoring_metrics'] = [
                'pod_ready_status',
                'service_endpoint_health',
                'error_rate'
            ]
        
        elif operation_type == OptimizationType.RESOURCE_LIMITS:
            rollback_plan['trigger_conditions'] = [
                'pod_oom_killed',
                'cpu_throttling',
                'performance_degradation'
            ]
            rollback_plan['rollback_actions'] = [
                f"kubectl patch deployment {plan['target']} -p='{{\"spec\":{{\"template\":{{\"spec\":{{\"containers\":[{{\"name\":\"main\",\"resources\":{{\"limits\":{{\"cpu\":\"{plan['current_value']['cpu']}\"}}}}}}]}}}}}}'"
            ]
            rollback_plan['monitoring_metrics'] = [
                'container_oom_killed',
                'cpu_usage',
                'memory_usage',
                'response_time'
            ]
        
        return rollback_plan
    
    def _simulate_optimization(self, plan: Dict[str, Any], 
                             cluster_state: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate optimization to predict outcomes"""
        simulation_results = {
            'predicted_resource_usage': {},
            'predicted_cost_savings': plan.get('potential_savings', 0),
            'predicted_risk_factors': [],
            'predicted_performance_impact': 'low',
            'simulation_confidence': 0.7
        }
        
        operation_type = plan.get('type')
        
        if operation_type == OptimizationType.SCALE_DOWN:
            # Simulate scale down impact
            simulation_results['predicted_resource_usage'] = {
                'cpu_reduction': 0.2,  # 20% CPU reduction
                'memory_reduction': 0.3,  # 30% memory reduction
                'network_reduction': 0.1  # 10% network reduction
            }
            simulation_results['predicted_risk_factors'] = [
                'reduced_availability',
                'increased_load_on_remaining_pods'
            ]
            simulation_results['predicted_performance_impact'] = 'medium'
        
        elif operation_type == OptimizationType.RESOURCE_LIMITS:
            # Simulate resource limit changes
            current_value = plan.get('current_value', {})
            proposed_value = plan.get('proposed_value', {})
            
            if 'cpu' in current_value and 'cpu' in proposed_value:
                cpu_reduction = (current_value['cpu'] - proposed_value['cpu']) / current_value['cpu']
                simulation_results['predicted_resource_usage']['cpu_reduction'] = cpu_reduction
            
            if 'memory' in current_value and 'memory' in proposed_value:
                memory_reduction = (current_value['memory'] - proposed_value['memory']) / current_value['memory']
                simulation_results['predicted_resource_usage']['memory_reduction'] = memory_reduction
            
            simulation_results['predicted_risk_factors'] = [
                'potential_oom_killed',
                'cpu_throttling'
            ]
            simulation_results['predicted_performance_impact'] = 'low'
        
        return simulation_results
    
    def _calculate_pod_savings(self, pod: Dict[str, Any]) -> float:
        """Calculate potential savings from pod optimization"""
        resource_analysis = pod.get('resource_analysis', {})
        cpu = resource_analysis.get('cpu', 0)
        memory = resource_analysis.get('memory', 0)
        
        # Estimate cost savings (simplified calculation)
        cpu_cost = cpu * 0.1  # $0.1 per CPU core per hour
        memory_cost = memory * 0.01  # $0.01 per MB per hour
        
        return cpu_cost + memory_cost
    
    def execute_optimization(self, plan: OptimizationPlan, 
                           dry_run: bool = True) -> Dict[str, Any]:
        """Execute optimization plan with safety checks"""
        try:
            execution_result = {
                'success': False,
                'plan': plan,
                'execution_time': datetime.utcnow().isoformat(),
                'dry_run': dry_run,
                'kubectl_commands': [],
                'rollback_commands': [],
                'monitoring_metrics': []
            }
            
            # Pre-execution safety checks
            if not self._pre_execution_safety_check(plan):
                execution_result['error'] = 'Safety check failed'
                return execution_result
            
            # Generate kubectl commands
            kubectl_commands = self._generate_kubectl_commands(plan)
            execution_result['kubectl_commands'] = kubectl_commands
            
            # Generate rollback commands
            rollback_commands = self._generate_rollback_commands(plan)
            execution_result['rollback_commands'] = rollback_commands
            
            if not dry_run:
                # Execute commands
                for command in kubectl_commands:
                    result = subprocess.run(command.split(), capture_output=True, text=True, timeout=30)
                    if result.returncode != 0:
                        execution_result['error'] = f"Command failed: {result.stderr}"
                        return execution_result
                
                execution_result['success'] = True
            else:
                execution_result['success'] = True
                execution_result['message'] = 'Dry run completed successfully'
            
            return execution_result
            
        except Exception as e:
            logger.error(f"Error executing optimization: {e}")
            return {
                'success': False,
                'error': str(e),
                'plan': plan,
                'execution_time': datetime.utcnow().isoformat()
            }
    
    def _pre_execution_safety_check(self, plan: OptimizationPlan) -> bool:
        """Perform pre-execution safety checks"""
        # Check risk level
        if plan.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            logger.warning(f"High risk optimization detected: {plan.risk_level}")
            return False
        
        # Check business hours
        current_hour = datetime.utcnow().hour
        is_business_hours = 9 <= current_hour <= 17
        
        if is_business_hours and plan.risk_score > 0.5:
            logger.warning("High risk operation during business hours")
            return False
        
        # Check safety boundaries
        if plan.risk_score > self.safety_boundaries.max_risk_score:
            logger.warning("Risk score exceeds safety boundaries")
            return False
        
        return True
    
    def _generate_kubectl_commands(self, plan: OptimizationPlan) -> List[str]:
        """Generate kubectl commands for optimization"""
        commands = []
        
        if plan.operation_type == OptimizationType.SCALE_DOWN:
            # Scale deployment to 0
            commands.append(f"kubectl scale deployment {plan.target_resource} --replicas=0")
        
        elif plan.operation_type == OptimizationType.RESOURCE_LIMITS:
            # Update resource limits
            if 'cpu' in plan.proposed_value:
                commands.append(f"kubectl patch deployment {plan.target_resource} -p='{{\"spec\":{{\"template\":{{\"spec\":{{\"containers\":[{{\"name\":\"main\",\"resources\":{{\"limits\":{{\"cpu\":\"{plan.proposed_value['cpu']}\"}}}}}}]}}}}}}'")
            
            if 'memory' in plan.proposed_value:
                commands.append(f"kubectl patch deployment {plan.target_resource} -p='{{\"spec\":{{\"template\":{{\"spec\":{{\"containers\":[{{\"name\":\"main\",\"resources\":{{\"limits\":{{\"memory\":\"{plan.proposed_value['memory']}Mi\"}}}}}}]}}}}}}'")
        
        elif plan.operation_type == OptimizationType.REPLICA_ADJUSTMENT:
            # Adjust replica count
            commands.append(f"kubectl scale deployment {plan.target_resource} --replicas={plan.proposed_value}")
        
        return commands
    
    def _generate_rollback_commands(self, plan: OptimizationPlan) -> List[str]:
        """Generate rollback commands for optimization"""
        commands = []
        
        if plan.operation_type == OptimizationType.SCALE_DOWN:
            # Scale back up
            commands.append(f"kubectl scale deployment {plan.target_resource} --replicas={plan.current_value}")
        
        elif plan.operation_type == OptimizationType.RESOURCE_LIMITS:
            # Restore original resource limits
            if 'cpu' in plan.current_value:
                commands.append(f"kubectl patch deployment {plan.target_resource} -p='{{\"spec\":{{\"template\":{{\"spec\":{{\"containers\":[{{\"name\":\"main\",\"resources\":{{\"limits\":{{\"cpu\":\"{plan.current_value['cpu']}\"}}}}}}]}}}}}}'")
            
            if 'memory' in plan.current_value:
                commands.append(f"kubectl patch deployment {plan.target_resource} -p='{{\"spec\":{{\"template\":{{\"spec\":{{\"containers\":[{{\"name\":\"main\",\"resources\":{{\"limits\":{{\"memory\":\"{plan.current_value['memory']}Mi\"}}}}}}]}}}}}}'")
        
        elif plan.operation_type == OptimizationType.REPLICA_ADJUSTMENT:
            # Restore original replica count
            commands.append(f"kubectl scale deployment {plan.target_resource} --replicas={plan.current_value}")
        
        return commands
    
    def get_optimization_summary(self, plans: List[OptimizationPlan]) -> Dict[str, Any]:
        """Generate optimization summary with confidence and risk analysis"""
        if not plans:
            return {
                'total_plans': 0,
                'high_confidence_plans': 0,
                'low_risk_plans': 0,
                'total_potential_savings': 0,
                'recommended_actions': []
            }
        
        high_confidence_plans = [p for p in plans if p.confidence_score >= self.high_confidence_threshold]
        low_risk_plans = [p for p in plans if p.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]]
        
        total_savings = sum(p.potential_savings for p in plans)
        
        # Generate recommended actions
        recommended_actions = []
        
        # High confidence, low risk plans
        safe_plans = [p for p in plans if p.confidence_score >= self.high_confidence_threshold and p.risk_level == RiskLevel.LOW]
        for plan in safe_plans[:3]:  # Top 3 safe plans
            recommended_actions.append({
                'action': f"Execute {plan.operation_type.value} on {plan.target_resource}",
                'confidence': plan.confidence_score,
                'risk': plan.risk_level.value,
                'savings': plan.potential_savings,
                'reason': 'high_confidence_low_risk'
            })
        
        # High savings plans
        high_savings_plans = sorted(plans, key=lambda x: x.potential_savings, reverse=True)[:3]
        for plan in high_savings_plans:
            if plan not in safe_plans:  # Don't duplicate
                recommended_actions.append({
                    'action': f"Execute {plan.operation_type.value} on {plan.target_resource}",
                    'confidence': plan.confidence_score,
                    'risk': plan.risk_level.value,
                    'savings': plan.potential_savings,
                    'reason': 'high_potential_savings'
                })
        
        return {
            'total_plans': len(plans),
            'high_confidence_plans': len(high_confidence_plans),
            'low_risk_plans': len(low_risk_plans),
            'total_potential_savings': total_savings,
            'recommended_actions': recommended_actions,
            'risk_distribution': {
                'low': len([p for p in plans if p.risk_level == RiskLevel.LOW]),
                'medium': len([p for p in plans if p.risk_level == RiskLevel.MEDIUM]),
                'high': len([p for p in plans if p.risk_level == RiskLevel.HIGH]),
                'critical': len([p for p in plans if p.risk_level == RiskLevel.CRITICAL])
            },
            'confidence_distribution': {
                'high': len([p for p in plans if p.confidence_score >= self.high_confidence_threshold]),
                'medium': len([p for p in plans if self.medium_confidence_threshold <= p.confidence_score < self.high_confidence_threshold]),
                'low': len([p for p in plans if p.confidence_score < self.medium_confidence_threshold])
            }
        } 