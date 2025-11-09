"""Global pytest fixtures and utilities."""
import socket
import pytest


def _can_reach(host: str, port: int, timeout: float = 2.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def skip_if_offline():
    """Skip external tests if basic network connectivity appears unavailable.

    We test reachability to a stable public endpoint (googleapis.com:443).
    Tests marked with @pytest.mark.external should call this fixture first.
    """
    reachable = _can_reach("googleapis.com", 443)
    if not reachable:
        pytest.skip("Network unreachable: skipping external API tests")
