"""
UPID CLI - ROI Analyzer
Return on Investment analysis and projections
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import math

logger = logging.getLogger(__name__)


@dataclass
class ROIAnalysis:
    """ROI analysis data structure"""
    initial_investment: float
    total_savings: float
    roi_percentage: float
    payback_period_months: float
    net_present_value: float
    internal_rate_of_return: float
    breakeven_point: datetime
    projected_savings: Dict[str, float]


@dataclass
class ROIForecast:
    """ROI forecast data"""
    period: str
    projected_savings: float
    cumulative_savings: float
    roi_percentage: float
    confidence_level: float


class ROIAnalyzer:
    """
    Return on Investment Analyzer
    
    Provides comprehensive ROI analysis capabilities:
    - ROI calculations and projections
    - Payback period analysis
    - Net Present Value calculations
    - Internal Rate of Return analysis
    - Breakeven point analysis
    - Long-term ROI forecasting
    """
    
    def __init__(self):
        self.discount_rate = 0.10  # 10% discount rate
        self.analysis_history: List[ROIAnalysis] = []
        
        logger.info("🔧 Initializing ROI analyzer")
    
    async def calculate_roi(self, 
                           initial_investment: float,
                           monthly_savings: float,
                           implementation_cost: float = 0.0,
                           maintenance_cost: float = 0.0,
                           time_period_months: int = 12) -> ROIAnalysis:
        """Calculate comprehensive ROI analysis"""
        try:
            logger.info("💰 Calculating ROI analysis...")
            
            # Calculate total investment
            total_investment = initial_investment + implementation_cost
            
            # Calculate total savings over time period
            total_savings = monthly_savings * time_period_months
            
            # Calculate maintenance costs
            total_maintenance = maintenance_cost * time_period_months
            
            # Net savings
            net_savings = total_savings - total_maintenance
            
            # Calculate ROI percentage
            roi_percentage = (net_savings / max(total_investment, 1)) * 100
            
            # Calculate payback period
            payback_period_months = total_investment / max(monthly_savings, 1)
            
            # Calculate Net Present Value
            npv = await self._calculate_npv(total_investment, monthly_savings, maintenance_cost, time_period_months)
            
            # Calculate Internal Rate of Return
            irr = await self._calculate_irr(total_investment, monthly_savings, maintenance_cost, time_period_months)
            
            # Calculate breakeven point
            breakeven_point = datetime.utcnow() + timedelta(days=payback_period_months * 30)
            
            # Calculate projected savings
            projected_savings = await self._calculate_projected_savings(monthly_savings, time_period_months)
            
            # Create ROI analysis
            roi_analysis = ROIAnalysis(
                initial_investment=total_investment,
                total_savings=net_savings,
                roi_percentage=roi_percentage,
                payback_period_months=payback_period_months,
                net_present_value=npv,
                internal_rate_of_return=irr,
                breakeven_point=breakeven_point,
                projected_savings=projected_savings
            )
            
            # Store in history
            self.analysis_history.append(roi_analysis)
            
            logger.info(f"✅ ROI analysis completed: {roi_percentage:.2f}% ROI")
            return roi_analysis
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate ROI: {e}")
            return ROIAnalysis(
                initial_investment=0.0,
                total_savings=0.0,
                roi_percentage=0.0,
                payback_period_months=0.0,
                net_present_value=0.0,
                internal_rate_of_return=0.0,
                breakeven_point=datetime.utcnow(),
                projected_savings={}
            )
    
    async def _calculate_npv(self, 
                            initial_investment: float,
                            monthly_savings: float,
                            monthly_maintenance: float,
                            months: int) -> float:
        """Calculate Net Present Value"""
        try:
            npv = -initial_investment  # Initial investment is negative cash flow
            
            for month in range(1, months + 1):
                # Monthly net cash flow
                monthly_cash_flow = monthly_savings - monthly_maintenance
                
                # Discount factor
                discount_factor = 1 / ((1 + self.discount_rate) ** (month / 12))
                
                # Add discounted cash flow to NPV
                npv += monthly_cash_flow * discount_factor
            
            return npv
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate NPV: {e}")
            return 0.0
    
    async def _calculate_irr(self, 
                            initial_investment: float,
                            monthly_savings: float,
                            monthly_maintenance: float,
                            months: int) -> float:
        """Calculate Internal Rate of Return (simplified)"""
        try:
            # Simplified IRR calculation
            total_cash_flow = (monthly_savings - monthly_maintenance) * months
            irr = (total_cash_flow / max(initial_investment, 1)) - 1
            
            return irr * 100  # Convert to percentage
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate IRR: {e}")
            return 0.0
    
    async def _calculate_projected_savings(self, monthly_savings: float, months: int) -> Dict[str, float]:
        """Calculate projected savings over time"""
        try:
            projected_savings = {}
            
            for month in range(1, months + 1):
                cumulative_savings = monthly_savings * month
                projected_savings[f"month_{month}"] = cumulative_savings
            
            return projected_savings
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate projected savings: {e}")
            return {}
    
    async def generate_roi_forecast(self, 
                                  initial_investment: float,
                                  monthly_savings: float,
                                  forecast_period_months: int = 36) -> List[ROIForecast]:
        """Generate long-term ROI forecast"""
        try:
            logger.info("🔮 Generating ROI forecast...")
            
            forecasts = []
            
            for month in range(1, forecast_period_months + 1):
                # Calculate cumulative savings
                cumulative_savings = monthly_savings * month
                
                # Calculate ROI percentage
                roi_percentage = (cumulative_savings / max(initial_investment, 1)) * 100
                
                # Calculate confidence level (simplified)
                confidence_level = min(95.0, 50.0 + (month * 1.5))  # Increases over time
                
                forecast = ROIForecast(
                    period=f"month_{month}",
                    projected_savings=monthly_savings,
                    cumulative_savings=cumulative_savings,
                    roi_percentage=roi_percentage,
                    confidence_level=confidence_level
                )
                
                forecasts.append(forecast)
            
            logger.info(f"✅ Generated {len(forecasts)} ROI forecasts")
            return forecasts
            
        except Exception as e:
            logger.error(f"❌ Failed to generate ROI forecast: {e}")
            return []
    
    async def compare_roi_scenarios(self, 
                                  scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare multiple ROI scenarios"""
        try:
            logger.info("📊 Comparing ROI scenarios...")
            
            comparison = {
                'scenarios': [],
                'best_scenario': None,
                'summary': {}
            }
            
            best_roi = -float('inf')
            
            for i, scenario in enumerate(scenarios):
                # Calculate ROI for this scenario
                roi_analysis = await self.calculate_roi(
                    initial_investment=scenario.get('initial_investment', 0),
                    monthly_savings=scenario.get('monthly_savings', 0),
                    implementation_cost=scenario.get('implementation_cost', 0),
                    maintenance_cost=scenario.get('maintenance_cost', 0),
                    time_period_months=scenario.get('time_period_months', 12)
                )
                
                scenario_result = {
                    'scenario_name': scenario.get('name', f'Scenario {i+1}'),
                    'roi_percentage': roi_analysis.roi_percentage,
                    'payback_period_months': roi_analysis.payback_period_months,
                    'net_present_value': roi_analysis.net_present_value,
                    'internal_rate_of_return': roi_analysis.internal_rate_of_return,
                    'total_savings': roi_analysis.total_savings
                }
                
                comparison['scenarios'].append(scenario_result)
                
                # Track best scenario
                if roi_analysis.roi_percentage > best_roi:
                    best_roi = roi_analysis.roi_percentage
                    comparison['best_scenario'] = scenario_result
            
            # Generate summary
            if comparison['scenarios']:
                roi_percentages = [s['roi_percentage'] for s in comparison['scenarios']]
                comparison['summary'] = {
                    'average_roi': sum(roi_percentages) / len(roi_percentages),
                    'max_roi': max(roi_percentages),
                    'min_roi': min(roi_percentages),
                    'roi_range': max(roi_percentages) - min(roi_percentages)
                }
            
            logger.info("✅ ROI scenario comparison completed")
            return comparison
            
        except Exception as e:
            logger.error(f"❌ Failed to compare ROI scenarios: {e}")
            return {}
    
    async def calculate_breakeven_analysis(self, 
                                         initial_investment: float,
                                         monthly_savings: float,
                                         monthly_costs: float = 0.0) -> Dict[str, Any]:
        """Calculate breakeven analysis"""
        try:
            logger.info("⚖️ Calculating breakeven analysis...")
            
            # Calculate net monthly savings
            net_monthly_savings = monthly_savings - monthly_costs
            
            # Calculate breakeven point
            if net_monthly_savings > 0:
                breakeven_months = initial_investment / net_monthly_savings
                breakeven_date = datetime.utcnow() + timedelta(days=breakeven_months * 30)
            else:
                breakeven_months = float('inf')
                breakeven_date = None
            
            # Calculate sensitivity analysis
            sensitivity_analysis = await self._calculate_sensitivity_analysis(
                initial_investment, monthly_savings, monthly_costs
            )
            
            analysis = {
                'initial_investment': initial_investment,
                'monthly_savings': monthly_savings,
                'monthly_costs': monthly_costs,
                'net_monthly_savings': net_monthly_savings,
                'breakeven_months': breakeven_months,
                'breakeven_date': breakeven_date.isoformat() if breakeven_date else None,
                'sensitivity_analysis': sensitivity_analysis
            }
            
            logger.info("✅ Breakeven analysis completed")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate breakeven analysis: {e}")
            return {}
    
    async def _calculate_sensitivity_analysis(self, 
                                            initial_investment: float,
                                            monthly_savings: float,
                                            monthly_costs: float) -> Dict[str, Any]:
        """Calculate sensitivity analysis for breakeven"""
        try:
            sensitivity = {}
            
            # Vary monthly savings by ±20%
            for variation in [-0.2, -0.1, 0, 0.1, 0.2]:
                adjusted_savings = monthly_savings * (1 + variation)
                net_monthly_savings = adjusted_savings - monthly_costs
                
                if net_monthly_savings > 0:
                    breakeven_months = initial_investment / net_monthly_savings
                else:
                    breakeven_months = float('inf')
                
                variation_key = f"{variation*100:+.0f}%"
                sensitivity[variation_key] = {
                    'adjusted_savings': adjusted_savings,
                    'breakeven_months': breakeven_months
                }
            
            return sensitivity
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate sensitivity analysis: {e}")
            return {}
    
    async def generate_roi_report(self, 
                                roi_analysis: ROIAnalysis,
                                include_forecast: bool = True,
                                include_comparison: bool = False) -> Dict[str, Any]:
        """Generate comprehensive ROI report"""
        try:
            logger.info("📋 Generating ROI report...")
            
            report = {
                'timestamp': datetime.utcnow().isoformat(),
                'roi_analysis': {
                    'initial_investment': roi_analysis.initial_investment,
                    'total_savings': roi_analysis.total_savings,
                    'roi_percentage': roi_analysis.roi_percentage,
                    'payback_period_months': roi_analysis.payback_period_months,
                    'net_present_value': roi_analysis.net_present_value,
                    'internal_rate_of_return': roi_analysis.internal_rate_of_return,
                    'breakeven_point': roi_analysis.breakeven_point.isoformat(),
                    'projected_savings': roi_analysis.projected_savings
                },
                'recommendations': await self._generate_roi_recommendations(roi_analysis)
            }
            
            # Add forecast if requested
            if include_forecast:
                monthly_savings = roi_analysis.total_savings / 12  # Simplified
                forecast = await self.generate_roi_forecast(
                    roi_analysis.initial_investment, monthly_savings
                )
                report['forecast'] = [f.__dict__ for f in forecast]
            
            # Add comparison if requested
            if include_comparison and self.analysis_history:
                report['historical_comparison'] = await self._compare_with_history(roi_analysis)
            
            logger.info("✅ ROI report generated successfully")
            return report
            
        except Exception as e:
            logger.error(f"❌ Failed to generate ROI report: {e}")
            return {}
    
    async def _generate_roi_recommendations(self, roi_analysis: ROIAnalysis) -> List[Dict[str, Any]]:
        """Generate recommendations based on ROI analysis"""
        try:
            recommendations = []
            
            # ROI recommendations
            if roi_analysis.roi_percentage < 20:
                recommendations.append({
                    'type': 'roi_improvement',
                    'priority': 'high',
                    'description': 'Low ROI detected. Consider optimization strategies to increase savings.',
                    'impact': 'high'
                })
            
            # Payback period recommendations
            if roi_analysis.payback_period_months > 12:
                recommendations.append({
                    'type': 'payback_optimization',
                    'priority': 'medium',
                    'description': 'Long payback period. Consider strategies to accelerate savings.',
                    'impact': 'medium'
                })
            
            # NPV recommendations
            if roi_analysis.net_present_value < 0:
                recommendations.append({
                    'type': 'npv_improvement',
                    'priority': 'high',
                    'description': 'Negative NPV. Review investment strategy and cost structure.',
                    'impact': 'high'
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Failed to generate ROI recommendations: {e}")
            return []
    
    async def _compare_with_history(self, current_analysis: ROIAnalysis) -> Dict[str, Any]:
        """Compare current ROI with historical data"""
        try:
            if len(self.analysis_history) < 2:
                return {}
            
            # Get previous analysis
            previous_analysis = self.analysis_history[-2]  # Second to last
            
            comparison = {
                'roi_change': current_analysis.roi_percentage - previous_analysis.roi_percentage,
                'savings_change': current_analysis.total_savings - previous_analysis.total_savings,
                'payback_change': current_analysis.payback_period_months - previous_analysis.payback_period_months,
                'npv_change': current_analysis.net_present_value - previous_analysis.net_present_value
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"❌ Failed to compare with history: {e}")
            return {} 