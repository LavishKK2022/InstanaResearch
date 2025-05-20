from aioptim.services.instana import IBM
import pytest
from aioptim.utils.node import Node
from aioptim.utils.request import Conn
from unittest.mock import patch


@pytest.fixture
def ibm():
    return IBM(
        "tenant",
        "unit",
        "api",
        "label",
        50
    )


@pytest.fixture
def valid_technologies():
    return ["pythonRuntimePlatform", "springbootApplicationContainer"]


@pytest.fixture
def invalid_technologies():
    return ["PHP", "Rust", "test"]


@pytest.fixture
def endpoints():
    return [
        Node.EndpointNode("test", "pythonRuntimePlatform", 500),
        Node.EndpointNode("test", "springbootApplicationContainer", 500),
        Node.EndpointNode("test", "springbootApplicationContainer", 200),
        Node.EndpointNode("test", "test", 500),
        Node.EndpointNode("test", "springbootApplicationContainer", 200),
    ]


@pytest.fixture
def endpoint_response():
    return {
        "items": [
            {
                "endpoint": {
                    "id": "example",
                    "label": "cities",
                    "type": "HTTP",
                    "serviceId": "example",
                    "technologies": ["mySqlDatabase"],
                    "syntheticType": "NON_SYNTHETIC",
                    "synthetic": False,
                    "entityType": "ENDPOINT",
                },
                "metrics": {"latency.mean": [[1744523350000, 180.625]]},
            },
            {
                "endpoint": {
                    "id": "example",
                    "label": "robot-shop",
                    "type": "HTTP",
                    "serviceId": "example",
                    "technologies": ["golangRuntimePlatform"],
                    "syntheticType": "NON_SYNTHETIC",
                    "synthetic": False,
                    "entityType": "ENDPOINT",
                },
                "metrics": {"latency.mean": [[1744523350000, 124]]},
            },
        ],
        "page": 1,
        "pageSize": 20,
        "totalHits": 34,
        "adjustedTimeframe": {"windowSize": 120000, "to": 1744523350000},
    }


def test_get_endpoints(ibm, endpoint_response):
    with patch.object(Conn, "post_req", return_value=endpoint_response):
        assert ibm.get_endpoints() == [
            Node.EndpointNode("cities", "mySqlDatabase", 180.625),
            Node.EndpointNode("robot-shop", "golangRuntimePlatform", 124)
        ]


def test_get_endpoints_empty(ibm):
    with patch.object(Conn, "post_req", return_value=[]):
        assert ibm.get_endpoints() is None


def test_filter_on_empty_endpointds(
        ibm,
        valid_technologies,
        invalid_technologies
):
    assert ibm.filter_endpoints([], 500, valid_technologies) is None
    assert ibm.filter_endpoints([], 0, valid_technologies) is None
    assert ibm.filter_endpoints([], 500, invalid_technologies) is None
    assert ibm.filter_endpoints([], 0, invalid_technologies) is None


def test_filter_on_thershold(
        ibm,
        endpoints,
        valid_technologies,
        invalid_technologies
):
    all_technologies = valid_technologies + invalid_technologies
    assert len(ibm.filter_endpoints(endpoints, 0, all_technologies)) == 5
    assert len(ibm.filter_endpoints(endpoints, 500, all_technologies)) == 3
    assert len(ibm.filter_endpoints(endpoints, -1, all_technologies)) == 5
    assert len(ibm.filter_endpoints(endpoints, 1000, all_technologies)) == 0


def test_filter_on_technology(
        ibm,
        endpoints,
        valid_technologies,
        invalid_technologies
):
    invalid_technologies.remove("test")
    assert len(ibm.filter_endpoints(endpoints, 100, valid_technologies)) == 4
    assert len(ibm.filter_endpoints(endpoints, 100, invalid_technologies)) == 0
    assert len(ibm.filter_endpoints(
        endpoints, 100, valid_technologies[0])) == 1
    assert len(ibm.filter_endpoints(
        endpoints, 100, valid_technologies[1])) == 3