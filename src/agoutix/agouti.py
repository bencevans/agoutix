from furl.furl import furl
import time
from typing import Generic, List, Literal, Optional, Type, TypeVar
from requests import request
from requests.exceptions import RequestException
from pydantic import BaseModel, Field
from rich import print


# ============================================================================
# Response Models
# ============================================================================


class ErrorResponse(BaseModel):
    """Response model for Agouti error responses."""

    class AgoutiError(BaseModel):
        status: str
        detail: str

    errors: List[AgoutiError]


class SucessfulLoginResponse(BaseModel):
    """Response model for Agouti login."""

    message: str
    success: bool
    token: str
    userId: str


# ============================================================================
# Data Models
# ============================================================================


class Project(BaseModel):
    class Attributes(BaseModel):
        name: str

    type: Literal["projects"]
    id: str
    attributes: Attributes


class Observation(BaseModel):
    class Attributes(BaseModel):
        observation_id: Optional[str] = Field(alias="observation-id", default=None)
        sampling_point: str = Field(alias="sampling-point")
        samplingpoint_id: str = Field(alias="samplingpoint-id")
        observation_type: Literal[
            "Empty",
            "DeploymentCalibration",
            "SetupPickup",
            "Unclassified",
            "Species",
            "Vehicle",
            "Undefined"
        ] = Field(alias="observation-type")
        sequence_id: str = Field(alias="sequence-id")
        scientific_name: Optional[str] = Field(alias="scientific-name", default=None)
        deployment_id: str = Field(alias="deployment-id")
        created_by_first_name: Optional[str] = Field(alias="created-by-first-name")
        created_by_last_name : Optional[str] = Field(alias="created-by-last-name")
        modified_by_first_name: Optional[str] = Field(alias="modified-by-first-name")
        modified_by_last_name : Optional[str] = Field(alias="modified-by-last-name")


    type: Literal["cachedobservations"]
    id: str
    attributes: Attributes


class Deployment(BaseModel):
    class Attributes(BaseModel):
        created_at: str = Field(alias="created-at")
        created_by: str = Field(alias="created-by")
        location: str
        notes: Optional[str] = None
        percent_inspected: Optional[float] = Field(
            alias="percent-inspected", default=None
        )
        project: str

    type: Literal["deployments"]
    id: str
    attributes: Attributes


class DeploymentCalibration(BaseModel):
    class Attributes(BaseModel):
        deployment: str
        observation: str
        asset: str
        label: Literal["top", "bottom"]
        x: str
        y: str
        height: str
        distance: Optional[str] = None

    type: Literal["deploymentcalibrations"]
    id: str
    attributes: Attributes


class ObservationPosition(BaseModel):
    class Attributes(BaseModel):
        asset: str
        label: Literal["front-leg"]
        observation: str
        x: str
        y: str

    type: Literal["observationpositions"]
    id: str
    attributes: Attributes


class Asset(BaseModel):
    class Attributes(BaseModel):
        sequence: str
        type: Literal["image", "video"]
        filename: str
        original_filename: str = Field(alias="original-filename")
        destination: str
        directory: str
        order: int
        created_at: str = Field(alias="created-at")
        is_favorite: Optional[bool] = Field(alias="is-favorite", default=None)
        deployment: str
        width: int
        height: int
        camera_make: str = Field(alias="camera-make")
        camera_model: str = Field(alias="camera-model")
        mime_type: str = Field(alias="mime-type")
        camera_serial_number: Optional[str] = Field(
            alias="camera-serial-number", default=None
        )
        is_time_lapse: Optional[bool] = Field(alias="is-time-lapse", default=None)

    type: Literal["assets"]
    id: str
    attributes: Attributes


class AssetReference(BaseModel):
    type: Literal["assets"]
    id: str
    sequence: str


class Sequence(BaseModel):
    class Attributes(BaseModel):
        deployment: str
        order: int

    type: Literal["sequences"]
    id: str
    attributes: Attributes


# ============================================================================
# API Response Models
# ============================================================================

DataType = TypeVar("DataType", bound=BaseModel)


class ApiResponse(BaseModel, Generic[DataType]):
    """Generic API response model for JSON:API format responses."""

    class JsonApiDetails(BaseModel):
        version: str

    class Meta(BaseModel):
        count: int
        current_page: int = Field(alias="current-page")
        first_page: int = Field(alias="first-page")
        last_page: int = Field(alias="last-page")
        pages_total: int = Field(alias="pages-total")

    class Links(BaseModel):
        self: str
        first: str
        last: str
        prev: Optional[str] = None
        next: Optional[str] = None

    meta: Optional[Meta] = None
    links: Optional[Links] = None
    data: DataType | List[DataType]
    jsonapi: JsonApiDetails
    relationships: Optional[dict] = None
    links: Optional[dict] = None
    included: Optional[list] = None


# Type aliases for specific responses
class ProjectsResponse(ApiResponse[Project]):
    pass


class ObservationsResponse(ApiResponse[Observation]):
    pass


class DeploymentsResponse(ApiResponse[Deployment]):
    pass


class DeploymentCalibrationsResponse(ApiResponse[DeploymentCalibration]):
    pass


class ObservationPositionsResponse(ApiResponse[ObservationPosition]):
    pass


class AssetsResponse(ApiResponse[Asset]):
    pass


class SequenceResponse(ApiResponse[Sequence]):
    pass


class AssetReferenceResponse(ApiResponse[AssetReference]):
    pass


# ============================================================================
# Agouti API Client
# ============================================================================


class Agouti:
    email: str
    password: str
    token: str
    user_id: str

    def __init__(self, email: str, password: str, verbose: bool = False) -> None:
        self.email = email
        self.password = password
        self.verbose = verbose
        self.login()

    def _log(self, *args) -> None:
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            print(*args)

    def _request_with_retries(
        self,
        method: str,
        url: str,
        headers: Optional[dict] = None,
        json: Optional[dict] = None,
        max_retries: int = 3,
        retry_delay_seconds: float = 1.0,
        timeout: tuple[float, float] = (10.0, 60.0),
        operation_name: str = "Request",
    ):
        """Make an HTTP request with retries for transient failures."""
        retriable_status_codes = {408, 429, 500, 502, 503, 504}

        for attempt in range(max_retries + 1):
            try:
                response = request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json,
                    timeout=timeout,
                )
            except RequestException as error:
                if attempt == max_retries:
                    raise Exception(
                        f"{operation_name} failed after {max_retries + 1} attempts"
                    ) from error

                print(
                    f"[yellow]{operation_name} network error: {error}. "
                    f"Retrying ({attempt + 1}/{max_retries})...[/yellow]"
                )
                time.sleep(retry_delay_seconds * (2**attempt))
                continue

            if response.status_code in retriable_status_codes:
                if attempt == max_retries:
                    return response

                print(
                    f"[yellow]{operation_name} failed with status {response.status_code}. "
                    f"Retrying ({attempt + 1}/{max_retries})...[/yellow]"
                )
                time.sleep(retry_delay_seconds * (2**attempt))
                continue

            return response

        raise Exception(f"{operation_name} failed")

    def _make_request(
        self, url: str, response_model: Type[ApiResponse[DataType]]
    ) -> ApiResponse[DataType]:
        """Make a GET request to the Agouti API and parse the response."""
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self._request_with_retries(
            "GET", url, headers=headers, operation_name="API request"
        )

        if response.status_code != 200:
            try:
                error_response = ErrorResponse(**response.json())
                for error in error_response.errors:
                    print(f"[red]{error.detail}[/red]")
            except Exception:
                print(
                    f"[red]API request failed with status {response.status_code}[/red]"
                )
            raise Exception("API request failed")

        parsed_response = response_model(**response.json())

        # Tried using the .links object but some aren't being written correctly so falling back
        # to using .meta and checking pages_total vs current_page
        if (
            parsed_response.meta
            and parsed_response.meta.pages_total > parsed_response.meta.current_page
        ):
            next_page_number = parsed_response.meta.current_page + 1

            parsed_url = furl(url)
            parsed_url.args["page[offset]"] = next_page_number
            next_page_url = parsed_url.url
            self._log(f"Fetching next page: {next_page_url}")
            next_page_response = self._make_request(next_page_url, response_model)
            # Ensure both current and next page data are lists before concatenating.
            if isinstance(parsed_response.data, list):
                if isinstance(next_page_response.data, list):
                    parsed_response.data.extend(next_page_response.data)
                else:
                    parsed_response.data.append(next_page_response.data)
            else:
                # Convert single-item data into a list and combine with next page(s)
                if isinstance(next_page_response.data, list):
                    parsed_response.data = [
                        parsed_response.data
                    ] + next_page_response.data
                else:
                    parsed_response.data = [
                        parsed_response.data,
                        next_page_response.data,
                    ]

        return parsed_response

    def login(self) -> None:
        self._log(f"Logging in as {self.email}")
        response = self._request_with_retries(
            "POST",
            "https://api.agouti.eu/user/login",
            json={"email": self.email, "password": self.password},
            operation_name="Login request",
        )

        if response.status_code != 200:
            try:
                error_response = ErrorResponse(**response.json())
                raise Exception(f"Login failed: {error_response.errors[0].detail}")
            except Exception as error:
                raise Exception(
                    f"Login failed with status {response.status_code}"
                ) from error

        login_response = SucessfulLoginResponse(**response.json())
        if not login_response.success:
            print(f"[red]{login_response.message}[/red]")
            raise Exception("Login failed")

        self.token = login_response.token
        self.user_id = login_response.userId

        print(f"[green]{login_response.message}[/green]")

    def list_projects(self) -> List[Project]:
        """List projects accessible by the authenticated user."""
        url = f"https://api.agouti.eu/projects?filter%5Buser%5D={self.user_id}&page%5Blimit%5D=100&page%5Boffset%5D=0"
        response = self._make_request(url, ProjectsResponse)
        return response.data

    def list_project_observations(
        self,
        project_id: str,
        filter_observation_type: Optional[str] = None,
        page_limit: int = 100,
        page_offset: int = 0,
    ) -> List[Observation]:
        """List observations for a project, optionally filtered by observation type."""
        self._log(f"Listing observations for project {project_id}")
        url = f"https://api.agouti.eu/observations?filter%5Bcustom-deployments-filter%5D=true&filter%5Bcustom-filter%5D=true&filter%5Bproject%5D={project_id}&page[limit]={page_limit}&page[offset]={page_offset}"
        if filter_observation_type:
            url += f"&filter%5BobservationType%5D={filter_observation_type}"
        response = self._make_request(url, ObservationsResponse)
        self._log(f"Found {len(response.data)} observations")
        return response.data

    def list_project_deployments(self, project_id: str) -> List[Deployment]:
        """List deployments for a project."""
        self._log(f"Listing deployments for project {project_id}")
        url = f"https://api.agouti.eu/deployments?filter%5Bcustom-deployments-filter%5D=true&filter%5Bcustom-filter%5D=true&filter%5Bproject%5D={project_id}&page%5Blimit%5D=100&page%5Boffset%5D=0"
        response = self._make_request(url, DeploymentsResponse)
        self._log(f"Found {len(response.data)} deployments")
        return response.data

    def list_deployment_calibrations(
        self, deployment_id: str
    ) -> List[DeploymentCalibration]:
        """List calibrations for a deployment."""
        self._log(f"Listing deployment calibrations for deployment {deployment_id}")
        url = f"https://api.agouti.eu/deploymentcalibrations?filter%5Bdeployment%5D={deployment_id}"
        response = self._make_request(url, DeploymentCalibrationsResponse)
        return response.data

    def list_observation_positions(
        self, observation_id: str
    ) -> List[ObservationPosition]:
        """List positions for an observation."""
        url = f"https://api.agouti.eu/observationpositions?filter%5Bobservation%5D={observation_id}"
        response = self._make_request(url, ObservationPositionsResponse)
        return response.data

    def list_favorites(self, project_id: str) -> List[AssetReferenceResponse]:
        """List favorite assets for a project."""
        self._log(f"Listing favorite assets for project {project_id}")
        url = f"https://api.agouti.eu/assets/favorites?filter[project]={project_id}&page%5Blimit%5D=100&page%5Boffset%5D=0"
        response = self._make_request(url, AssetReferenceResponse)
        return response.data

    def get_sequence(self, sequence_id: str) -> List[SequenceResponse]:
        """Get all assets for a sequence."""
        self._log(f"Fetching assets for sequence {sequence_id}")
        url = f"https://api.agouti.eu/sequences/{sequence_id}?include=assets%2Cobservations%2Cobservations.createdBy%2Cdeployment"
        response = self._make_request(url, SequenceResponse)
        return response.data

    def get_asset(self, asset_id: str) -> Asset:
        """Get metadata for an asset."""
        self._log(f"Fetching metadata for asset {asset_id}")
        url = f"https://api.agouti.eu/assets/{asset_id}"
        response: ApiResponse[Asset] = self._make_request(url, ApiResponse[Asset])
        assert isinstance(response.data, Asset), "Expected single Asset, got list"
        return response.data

    def get_asset_file(
        self,
        asset_id: str,
        max_retries: int = 3,
        retry_delay_seconds: float = 1.0,
    ) -> tuple[bytes, str]:
        """Download an asset file with retry logic for transient failures."""
        self._log(f"Downloading asset {asset_id}")
        url = f"https://api.agouti.eu/assets/{asset_id}/file"
        headers = {"Authorization": f"Bearer {self.token}"}

        response = self._request_with_retries(
            "GET",
            url,
            headers=headers,
            max_retries=max_retries,
            retry_delay_seconds=retry_delay_seconds,
            operation_name="Asset download",
        )

        if response.status_code != 200:
            try:
                error_response = ErrorResponse(**response.json())
                for error in error_response.errors:
                    print(f"[red]{error.detail}[/red]")
            except Exception:
                print(
                    f"[red]Asset download failed with status {response.status_code}[/red]"
                )
            raise Exception("API request failed")

        filename = response.headers.get(
            "Content-Disposition", f"attachment; filename={asset_id}"
        ).split("filename=")[-1]

        return response.content, filename
