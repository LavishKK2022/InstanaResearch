"""
Middleware to collect data from the Instana backend and convert to endpoints.
Performs filter operation to extract endpoints that surpass the threshold
and are part of the supported technology.

[3] https://stackoverflow.com/a/61938635
    Stack Overflow: MisterMiyagi
    "Proper way to create class variable in Data Class"

"""

import time
from dataclasses import dataclass, field
from typing import ClassVar
from aioptim.utils.node import Node
from aioptim.utils.request import Conn


@dataclass
class IBM(Conn):
    """
    Collects the endpoint data using the '/metrics/endpoint'
    and converts the collected data into a list of concrete endpoints.
    """
    tenant: str
    unit: str
    api: str
    label: str
    delay: int
    url: str = field(init=False)
    BASE: ClassVar[str] = ".instana.io/api/application-monitoring"  # [3]

    def __post_init__(self):
        """ URL to the metrics enpdoint """
        self.url = "https://" + self.unit + "-" + self.tenant + IBM.BASE

    def get_endpoints(self):
        """
        Retrieve endpoints and their latency values from the Instana backend.

        Returns:
            List of endpoints, encapsulated into an endpoint node.
        """
        data = super().post_req(
            endpoint="/metrics/endpoints",
            data={
                "applicationBoundaryScope": "ALL",
                "excludeSynthetic": True,
                "entityType": "HTTP",
                "metrics": [
                    {
                        "aggregation": "MEAN",
                        "metric": "latency"
                    }
                ],
                "order": {
                    "by": "latency.mean",
                    "direction": "DESC"
                },
                "timeFrame": {
                    "to": int(time.time() * 1000),
                    "windowSize": self.delay * 60000
                }
            },
            params={"fillTimeSeries": "true"},
            headers={
                "Content-Type": "application/json",
                "authorization": self.api
            }
        )
        if data and data.get("items"):
            return [
                Node.EndpointNode(
                    label=item["endpoint"]["label"],
                    technology=item["endpoint"]["technologies"][0],
                    latency=item["metrics"]["latency.mean"][0][1]
                )
                for item in data["items"]
                if len(item["endpoint"]["technologies"]) == 1
            ]

    def filter_endpoints(self, endpoints, threshold, technology):
        """
        Filters out endpoint nodes based on their supported technology
        and the user provided threshold metrics.

        Args:
            endpoints: List of endpoints to filter from
            threshold: The threshold to compare the endpoints against
            technology: List of supported technologies to check against

        Returns:
            List of endpoints that exceed the threshold and are part of the 
            supported technologies.
        """
        if endpoints:
            return list(filter(
                lambda e: e.latency >= threshold and e.technology in technology,
                endpoints
            )
            )
