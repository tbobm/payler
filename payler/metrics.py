"""Expose payler internal metrics"""
from prometheus_client import start_http_server, Counter


def run_metric_server(port: int):
    """Start a prometheus exporter."""
    start_http_server(port)


METRIC_NAME = "payler_workflow_jobs"
DESCRIPTION = "Count number of payler-processed jobs."
JOB_COUNTER = Counter(
    METRIC_NAME,
    DESCRIPTION,
    labelnames=['workflow'],
)

__all__ = [
    'run_metric_server',
    'JOB_COUNTER',
]
