from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict


@dataclass
class EmailStats:
    total_sent: int
    successful_deliveries: int
    failed_deliveries: int
    total_recipients: int
    unique_recipients: int
    average_delivery_time: float


@dataclass
class EmailDeliveryReport:
    user_email: str
    period_start: datetime
    period_end: datetime
    stats: EmailStats
    most_common_recipients: List[Dict[str, int]]


@dataclass
class ReportParams:
    user_id: int
    filter_type: str
