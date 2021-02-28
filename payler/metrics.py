"""Expose payler internal metrics in OpenMetrics format.

Define and expose metrics for payler :class:`payler.runtime.Workflow`

The exposed metrics are as follow::

    # HELP payler_workflow_jobs_total Count number of payler-processed jobs.
    # TYPE payler_workflow_jobs_total counter
    payler_workflow_jobs_total{status="success",workflow="BrokerManager"} 1.0
    payler_workflow_jobs_total{status="success",workflow="SpoolManager"} 1.0

Each metric is defined based on the `status` and the `workflow`.

Exposed metrics are available based on the port defined
when calling :func:`run_metric_server`.
"""
from prometheus_client import start_http_server, Counter


def run_metric_server(port: int):
    """Start a prometheus exporter exposing workflow metrics.

    :param port: Listening port for the Prometheus exporter
    """
    start_http_server(port)


METRIC_NAME = "payler_workflow_jobs"
DESCRIPTION = "Count number of payler-processed jobs."
JOB_COUNTER = Counter(
    METRIC_NAME,
    DESCRIPTION,
    labelnames=['workflow', 'status'],
)

__all__ = [
    'run_metric_server',
    'JOB_COUNTER',
]
