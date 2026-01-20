from typing import Optional
from agoutix.agouti import Agouti
from os import environ


def read_env_variables(name: str, default: Optional[str] = None) -> str:
    """Read environment variable or raise error if not set."""
    value = environ.get(name, default)
    if value is None:
        raise ValueError(f"Environment variable {name} not set")
    return value


def read_env_int(name: str, default: Optional[int] = None) -> int:
    """Read environment variable as integer or raise error if not set."""
    string_value = read_env_variables(name, None if default is None else str(default))
    try:
        return int(string_value)
    except ValueError:
        raise ValueError(f"Environment variable {name} is not a valid integer")


AGOUTI_EMAIL = read_env_variables("AGOUTI_EMAIL")
AGOUTI_PASSWORD = read_env_variables("AGOUTI_PASSWORD")
AGOUTI_PROJECT_ID = read_env_variables("AGOUTI_PROJECT_ID")
AGOUTI_PROJECT_ID_N_OBSERVATIONS = read_env_int("AGOUTI_PROJECT_ID_N_OBSERVATIONS")
AGOUTI_PROJECT_ID_N_DEPLOYMENTS = read_env_int("AGOUTI_PROJECT_ID_N_DEPLOYMENTS")
AGOUTI_ASSET_ID = read_env_variables("AGOUTI_ASSET_ID")
AGOUTI_ASSET_FILENAME = read_env_variables("AGOUTI_ASSET_FILENAME")


def test_login() -> None:
    agouti = Agouti(AGOUTI_EMAIL, AGOUTI_PASSWORD)
    assert agouti.token is not None
    assert agouti.user_id is not None


def test_invalid_login() -> None:
    try:
        Agouti("invalid_email", "invalid_password")
    except Exception as e:
        assert str(e).startswith("Login failed")
    else:
        assert False, "Expected exception for invalid login"


def test_list_projects() -> None:
    agouti = Agouti(AGOUTI_EMAIL, AGOUTI_PASSWORD)
    projects = agouti.list_projects()
    assert len(projects) > 0


def test_list_project_deployments() -> None:
    agouti = Agouti(AGOUTI_EMAIL, AGOUTI_PASSWORD)
    deployments = agouti.list_project_deployments(AGOUTI_PROJECT_ID)
    assert len(deployments) == AGOUTI_PROJECT_ID_N_DEPLOYMENTS


def test_list_project_observations() -> None:
    agouti = Agouti(AGOUTI_EMAIL, AGOUTI_PASSWORD)
    observations = agouti.list_project_observations(AGOUTI_PROJECT_ID)
    assert len(observations) == AGOUTI_PROJECT_ID_N_OBSERVATIONS


def test_list_deployment_calibrations() -> None:
    agouti = Agouti(AGOUTI_EMAIL, AGOUTI_PASSWORD)
    deployments = agouti.list_project_deployments(AGOUTI_PROJECT_ID)
    assert len(deployments) > 0
    deployment_id = deployments[0].id
    calibrations = agouti.list_deployment_calibrations(deployment_id)
    assert len(calibrations) >= 0  # Calibrations may be zero


def test_get_asset() -> None:
    agouti = Agouti(AGOUTI_EMAIL, AGOUTI_PASSWORD)
    asset = agouti.get_asset(AGOUTI_ASSET_ID)
    assert asset.id == AGOUTI_ASSET_ID
    assert asset.attributes.filename == AGOUTI_ASSET_FILENAME


def test_get_asset_file() -> None:
    agouti = Agouti(AGOUTI_EMAIL, AGOUTI_PASSWORD)
    content, filename = agouti.get_asset_file(AGOUTI_ASSET_ID)
    assert len(content) > 0
    assert filename == AGOUTI_ASSET_FILENAME
