"""Tests for AWS ALB and GCE annotation support."""

from src.ingress2gateway.alb_gce import (
    get_alb_annotation_docs,
    get_gce_annotation_docs,
    parse_alb_annotations,
    parse_cloud_annotations,
    parse_gce_annotations,
)


def test_parse_alb_ssl_redirect():
    """Test parsing ALB SSL redirect annotation."""
    annotations = {"alb.ingress.kubernetes.io/ssl-redirect": "443"}

    result = parse_alb_annotations(annotations)

    assert len(result["filters"]) == 1
    assert result["filters"][0]["type"] == "RequestRedirect"
    assert result["filters"][0]["requestRedirect"]["scheme"] == "https"


def test_parse_alb_certificate_arn():
    """Test parsing ALB certificate ARN annotation."""
    annotations = {
        "alb.ingress.kubernetes.io/certificate-arn": "arn:aws:acm:us-east-1:123:cert/abc"
    }

    result = parse_alb_annotations(annotations)

    assert "certificateArn" in result["gateway_config"]
    assert len(result["warnings"]) > 0


def test_parse_alb_backend_protocol_grpc():
    """Test parsing ALB gRPC backend protocol."""
    annotations = {"alb.ingress.kubernetes.io/backend-protocol": "GRPC"}

    result = parse_alb_annotations(annotations)

    assert result["gateway_config"].get("useGrpcRoute") is True


def test_parse_alb_scheme():
    """Test parsing ALB scheme annotation."""
    annotations = {"alb.ingress.kubernetes.io/scheme": "internal"}

    result = parse_alb_annotations(annotations)

    assert result["gateway_config"]["scheme"] == "internal"
    assert any("internal" in w.lower() for w in result["warnings"])


def test_parse_gce_ingress_class():
    """Test parsing GCE ingress class."""
    annotations = {"kubernetes.io/ingress.class": "gce"}

    result = parse_gce_annotations(annotations)

    assert result["gateway_config"]["gatewayClassName"] == "gke-l7-global-external-managed"


def test_parse_gce_internal_class():
    """Test parsing GCE internal ingress class."""
    annotations = {"kubernetes.io/ingress.class": "gce-internal"}

    result = parse_gce_annotations(annotations)

    assert result["gateway_config"]["gatewayClassName"] == "gke-l7-rilb"


def test_parse_gce_static_ip():
    """Test parsing GCE static IP annotation."""
    annotations = {"kubernetes.io/ingress.global-static-ip-name": "my-static-ip"}

    result = parse_gce_annotations(annotations)

    assert result["gateway_config"]["addresses"][0]["value"] == "my-static-ip"


def test_parse_gce_managed_certificates():
    """Test parsing GCE managed certificates."""
    annotations = {"networking.gke.io/managed-certificates": "cert1,cert2"}

    result = parse_gce_annotations(annotations)

    assert result["gateway_config"]["managedCertificates"] == ["cert1", "cert2"]


def test_parse_cloud_annotations_combined():
    """Test parsing both ALB and GCE annotations."""
    annotations = {
        "alb.ingress.kubernetes.io/ssl-redirect": "443",
        "kubernetes.io/ingress.global-static-ip-name": "my-ip",
    }

    result = parse_cloud_annotations(annotations)

    assert len(result["filters"]) == 1
    assert "addresses" in result["gateway_config"]


def test_get_alb_annotation_docs():
    """Test getting ALB annotation documentation."""
    docs = get_alb_annotation_docs()

    assert len(docs) > 0
    assert all("annotation" in d for d in docs)
    assert all("description" in d for d in docs)


def test_get_gce_annotation_docs():
    """Test getting GCE annotation documentation."""
    docs = get_gce_annotation_docs()

    assert len(docs) > 0
    assert all("annotation" in d for d in docs)
