from pydantic import BaseModel
from typing import Optional

class ReportGenerationRequest(BaseModel):
    report_type: Optional[str] = None
    cluster_name: Optional[str] = None
    namespace: Optional[str] = None
    time_range: Optional[str] = None
    include_charts: Optional[bool] = None
    include_recommendations: Optional[bool] = None
    format: Optional[str] = None

class BusinessCorrelationRequest(BaseModel):
    cluster_name: Optional[str] = None
    namespace: Optional[str] = None
    time_range: Optional[str] = None

# Add other request models as needed for the endpoints. 