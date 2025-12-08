"""Tests for ReferenceGrant generation."""

from src.ingress2gateway.reference_grant import (
    check_reference_grant_needed,
    create_reference_grant,
    detect_cross_namespace_refs,
    generate_reference_grants,
)


def test_check_reference_grant_needed():
    """Test checking if ReferenceGrant is needed."""
    assert check_reference_grant_needed("default", "other") is True
    assert check_reference_grant_needed("default", "default") is False
    assert check_reference_grant_needed("default", None) is False


def test_detect_cross_namespace_refs_same_namespace():
    """Test no refs detected when same namespace."""
    gateway = {
        "metadata": {"name": "gw", "namespace": "default"},
        "spec": {"listeners": []},
    }
    httproutes = [
        {
            "metadata": {"name": "route", "namespace": "default"},
            "spec": {
                "parentRefs": [{"name": "gw"}],
                "rules": [{"backendRefs": [{"name": "svc", "port": 80}]}],
            },
        }
    ]

    refs = detect_cross_namespace_refs(gateway, httproutes)
    assert len(refs) == 0


def test_detect_cross_namespace_refs_different_namespace():
    """Test refs detected when different namespace."""
    gateway = {
        "metadata": {"name": "gw", "namespace": "gateway-ns"},
        "spec": {"listeners": []},
    }
    httproutes = [
        {
            "metadata": {"name": "route", "namespace": "app-ns"},
            "spec": {
                "parentRefs": [{"name": "gw", "namespace": "gateway-ns"}],
                "rules": [{"backendRefs": [{"name": "svc", "port": 80, "namespace": "svc-ns"}]}],
            },
        }
    ]

    refs = detect_cross_namespace_refs(gateway, httproutes)
    assert len(refs) == 2  # Gateway ref + Service ref


def test_create_reference_grant():
    """Test ReferenceGrant creation."""
    grant = create_reference_grant(
        from_namespace="app-ns",
        from_kinds=["HTTPRoute"],
        to_namespace="svc-ns",
        to_kind="Service",
    )

    assert grant["kind"] == "ReferenceGrant"
    assert grant["metadata"]["namespace"] == "svc-ns"
    assert grant["spec"]["from"][0]["namespace"] == "app-ns"
    assert grant["spec"]["to"][0]["kind"] == "Service"


def test_generate_reference_grants():
    """Test generating all required ReferenceGrants."""
    gateway = {
        "metadata": {"name": "gw", "namespace": "gateway-ns"},
        "spec": {"listeners": []},
    }
    httproutes = [
        {
            "metadata": {"name": "route", "namespace": "app-ns"},
            "kind": "HTTPRoute",
            "spec": {
                "parentRefs": [{"name": "gw", "namespace": "gateway-ns"}],
                "rules": [{"backendRefs": [{"name": "svc", "port": 80}]}],
            },
        }
    ]

    grants = generate_reference_grants(gateway, httproutes)
    assert len(grants) == 1
    assert grants[0]["metadata"]["namespace"] == "gateway-ns"
