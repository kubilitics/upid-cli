"""
Executive Dashboard Engine for UPID
Aggregates optimization trends, KPIs, cost/ROI, risk, and recommendations
Supports time-series and snapshot reporting for executive summaries
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import numpy as np

@dataclass
class ExecutiveSummary:
    timestamp: str
    cluster_id: str
    total_optimizations: int
    total_savings: float
    roi: float
    risk_score: float
    business_impact: str
    kpi_summary: Dict[str, Any]
    recommendations: List[str]
    trend_analysis: Dict[str, Any]

class ExecutiveDashboardEngine:
    """Aggregates and summarizes executive-level analytics for UPID"""
    def __init__(self):
        pass

    def generate_dashboard(self, cluster_id: str, 
                           optimization_history: List[Dict[str, Any]],
                           business_reports: List[Dict[str, Any]],
                           kpi_history: List[Dict[str, Any]]) -> ExecutiveSummary:
        """Generate an executive dashboard summary"""
        now = datetime.utcnow().isoformat()
        total_optimizations = len(optimization_history)
        total_savings = sum(item.get('potential_savings', 0) for item in optimization_history)
        roi = np.mean([report.get('roi_analysis', {}).get('current_roi', 0) for report in business_reports]) if business_reports else 0
        risk_score = np.mean([item.get('risk_score', 0) for item in optimization_history]) if optimization_history else 0
        business_impact = self._aggregate_business_impact(business_reports)
        kpi_summary = self._aggregate_kpis(kpi_history)
        recommendations = self._aggregate_recommendations(optimization_history, business_reports)
        trend_analysis = self._analyze_trends(optimization_history, kpi_history)
        return ExecutiveSummary(
            timestamp=now,
            cluster_id=cluster_id,
            total_optimizations=total_optimizations,
            total_savings=total_savings,
            roi=roi,
            risk_score=risk_score,
            business_impact=business_impact,
            kpi_summary=kpi_summary,
            recommendations=recommendations,
            trend_analysis=trend_analysis
        )

    def _aggregate_business_impact(self, business_reports: List[Dict[str, Any]]) -> str:
        if not business_reports:
            return "neutral"
        impacts = [r.get('executive_summary', {}).get('optimization_potential', 0) for r in business_reports]
        if np.mean(impacts) > 0:
            return "positive"
        elif np.mean(impacts) < 0:
            return "negative"
        return "neutral"

    def _aggregate_kpis(self, kpi_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not kpi_history:
            return {}
        summary = {}
        for k in ['resource_efficiency', 'availability_score', 'performance_score', 'business_activity_score']:
            values = [kpi.get(k, 0) for kpi in kpi_history]
            summary[k] = float(np.mean(values)) if values else 0
        return summary

    def _aggregate_recommendations(self, optimization_history, business_reports) -> List[str]:
        recs = []
        for plan in optimization_history:
            if plan.get('confidence_score', 0) > 0.8 and plan.get('risk_level', 'high') == 'low':
                recs.append(f"Execute {plan.get('operation_type', 'unknown')} on {plan.get('target_resource', 'N/A')}")
        for report in business_reports:
            for rec in report.get('recommendations', []):
                recs.append(rec.get('action', ''))
        return list(set(recs))[:5]

    def _analyze_trends(self, optimization_history, kpi_history) -> Dict[str, Any]:
        # Simple trend: compare first and last values
        trends = {}
        if kpi_history and len(kpi_history) > 1:
            for k in ['resource_efficiency', 'availability_score', 'performance_score', 'business_activity_score']:
                first = kpi_history[0].get(k, 0)
                last = kpi_history[-1].get(k, 0)
                trends[k] = {'start': first, 'end': last, 'change': last - first}
        if optimization_history and len(optimization_history) > 1:
            first = optimization_history[0].get('potential_savings', 0)
            last = optimization_history[-1].get('potential_savings', 0)
            trends['potential_savings'] = {'start': first, 'end': last, 'change': last - first}
        return trends

    def export_dashboard(self, summary: ExecutiveSummary, format: str = 'json') -> str:
        """Export the executive dashboard summary in the requested format"""
        data = summary.__dict__
        if format == 'json':
            return json.dumps(data, indent=2)
        elif format == 'yaml':
            import yaml
            return yaml.dump(data, default_flow_style=False)
        elif format == 'markdown':
            return self._to_markdown(data)
        elif format == 'html':
            return self._to_html(data)
        else:
            return str(data)

    def _to_markdown(self, data: Dict[str, Any]) -> str:
        md = f"# Executive Dashboard\n\n"
        md += f"**Cluster:** {data['cluster_id']}\n\n"
        md += f"**Timestamp:** {data['timestamp']}\n\n"
        md += f"**Total Optimizations:** {data['total_optimizations']}\n\n"
        md += f"**Total Savings:** ${data['total_savings']:.2f}\n\n"
        md += f"**ROI:** {data['roi']:.1f}%\n\n"
        md += f"**Risk Score:** {data['risk_score']:.2f}\n\n"
        md += f"**Business Impact:** {data['business_impact']}\n\n"
        md += f"## KPI Summary\n"
        for k, v in data['kpi_summary'].items():
            md += f"- {k.replace('_', ' ').title()}: {v:.1f}\n"
        md += f"\n## Recommendations\n"
        for rec in data['recommendations']:
            md += f"- {rec}\n"
        md += f"\n## Trend Analysis\n"
        for k, v in data['trend_analysis'].items():
            md += f"- {k.replace('_', ' ').title()}: Start={v['start']}, End={v['end']}, Change={v['change']:.2f}\n"
        return md

    def _to_html(self, data: Dict[str, Any]) -> str:
        html = f"<h1>Executive Dashboard</h1>"
        html += f"<b>Cluster:</b> {data['cluster_id']}<br>"
        html += f"<b>Timestamp:</b> {data['timestamp']}<br>"
        html += f"<b>Total Optimizations:</b> {data['total_optimizations']}<br>"
        html += f"<b>Total Savings:</b> ${data['total_savings']:.2f}<br>"
        html += f"<b>ROI:</b> {data['roi']:.1f}%<br>"
        html += f"<b>Risk Score:</b> {data['risk_score']:.2f}<br>"
        html += f"<b>Business Impact:</b> {data['business_impact']}<br>"
        html += f"<h2>KPI Summary</h2><ul>"
        for k, v in data['kpi_summary'].items():
            html += f"<li>{k.replace('_', ' ').title()}: {v:.1f}</li>"
        html += "</ul><h2>Recommendations</h2><ul>"
        for rec in data['recommendations']:
            html += f"<li>{rec}</li>"
        html += "</ul><h2>Trend Analysis</h2><ul>"
        for k, v in data['trend_analysis'].items():
            html += f"<li>{k.replace('_', ' ').title()}: Start={v['start']}, End={v['end']}, Change={v['change']:.2f}</li>"
        html += "</ul>"
        return html 