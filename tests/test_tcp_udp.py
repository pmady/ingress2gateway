"""Tests for TCP/UDP route support."""

from src.ingress2gateway.tcp_udp import (
    create_tcp_listener,
    create_tcp_route,
    create_udp_listener,
    create_udp_route,
    detect_tcp_udp_services,
    is_tcp_backend,
    is_udp_backend,
)


def test_is_tcp_backend_by_annotation():
    """Test TCP detection via annotation."""
    ingress = {"metadata": {"annotations": {"nginx.ingress.kubernetes.io/backend-protocol": "TCP"}}}
    assert is_tcp_backend(ingress, "my-service") is True


def test_is_tcp_backend_by_name():
    """Test TCP detection via service name."""
    ingress = {"metadata": {}}
    assert is_tcp_backend(ingress, "mysql-service") is True
    assert is_tcp_backend(ingress, "redis-cache") is True
    assert is_tcp_backend(ingress, "web-service") is False


def test_is_udp_backend_by_annotation():
    """Test UDP detection via annotation."""
    ingress = {"metadata": {"annotations": {"nginx.ingress.kubernetes.io/backend-protocol": "UDP"}}}
    assert is_udp_backend(ingress, "my-service") is True


def test_is_udp_backend_by_name():
    """Test UDP detection via service name."""
    ingress = {"metadata": {}}
    assert is_udp_backend(ingress, "dns-service") is True
    assert is_udp_backend(ingress, "syslog-collector") is True
    assert is_udp_backend(ingress, "web-service") is False


def test_create_tcp_route():
    """Test TCPRoute creation."""
    route = create_tcp_route(
        name="mysql-route",
        namespace="default",
        gateway_name="my-gateway",
        service_name="mysql",
        port=3306,
    )

    assert route["kind"] == "TCPRoute"
    assert route["apiVersion"] == "gateway.networking.k8s.io/v1alpha2"
    assert route["metadata"]["name"] == "mysql-route"
    assert route["spec"]["rules"][0]["backendRefs"][0]["port"] == 3306


def test_create_udp_route():
    """Test UDPRoute creation."""
    route = create_udp_route(
        name="dns-route",
        namespace="default",
        gateway_name="my-gateway",
        service_name="dns",
        port=53,
    )

    assert route["kind"] == "UDPRoute"
    assert route["apiVersion"] == "gateway.networking.k8s.io/v1alpha2"
    assert route["spec"]["rules"][0]["backendRefs"][0]["port"] == 53


def test_create_tcp_listener():
    """Test TCP listener creation."""
    listener = create_tcp_listener(hostname=None, port=3306)

    assert listener["name"] == "tcp-3306"
    assert listener["protocol"] == "TCP"
    assert listener["port"] == 3306


def test_create_udp_listener():
    """Test UDP listener creation."""
    listener = create_udp_listener(port=53)

    assert listener["name"] == "udp-53"
    assert listener["protocol"] == "UDP"
    assert listener["port"] == 53


def test_detect_tcp_udp_services():
    """Test detection of TCP/UDP services returns expected structure."""
    ingress = {"metadata": {"annotations": {}}}

    result = detect_tcp_udp_services(ingress)
    assert "tcp" in result
    assert "udp" in result
    assert isinstance(result["tcp"], list)
    assert isinstance(result["udp"], list)
