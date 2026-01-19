from typing import List, Literal, Optional
from requests import get, post
from pydantic import BaseModel, Field
from rich import print


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


class Project(BaseModel):
    class Attributes(BaseModel):
        # description: str
        # image-src: str
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
            "Empty", "DeploymentCalibration", "SetupPickup", "Unclassified", "Species"
        ] = Field(alias="observation-type")
        sequence_id: str = Field(alias="sequence-id")
        scientific_name: Optional[str] = Field(alias="scientific-name", default=None)
        deployment_id: str = Field(alias="deployment-id")

    type: Literal["cachedobservations"]
    id: str
    attributes: Attributes


class ObservationsResponse(BaseModel):
    class JsonApiDetails(BaseModel):
        version: str

    data: List[Observation]
    jsonapi: JsonApiDetails


class ProjectsResponse(BaseModel):
    class JsonApiDetails(BaseModel):
        version: str

    data: List[Project]
    jsonapi: JsonApiDetails


class Deployment(BaseModel):
    class Attributes(BaseModel):
        pass

    type: Literal["deployments"]
    id: str
    attributes: Attributes

class DeploymentsResponse(BaseModel):
    class JsonApiDetails(BaseModel):
        version: str

    data: List[Deployment]
    jsonapi: JsonApiDetails


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


class DeploymentCalibrationsResponse(BaseModel):
    class JsonApiDetails(BaseModel):
        version: str

    data: List[DeploymentCalibration]
    jsonapi: JsonApiDetails


class Agouti:
    username: str
    password: str
    token: str
    user_id: str

    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password

        self.login()

    def login(self) -> None:
        print(f"Logging in as {self.username}")
        response = post(
            "https://api.agouti.eu/user/login",
            json={"email": self.username, "password": self.password},
        )

        if response.status_code != 200:
            error_response = ErrorResponse(**response.json())
            for error in error_response.errors:
                print(f"[red]{error.detail}[/red]")
            raise Exception("Login failed")

        login_response = SucessfulLoginResponse(**response.json())
        if not login_response.success:
            print(f"[red]{login_response.message}[/red]")
            raise Exception("Login failed")

        self.token = login_response.token
        self.user_id = login_response.userId

        print(f"[green]{login_response.message}[/green]")

    def _get_projects(self, url: str) -> ProjectsResponse:
        headers = {"Authorization": f"Bearer {self.token}"}
        response = get(url, headers=headers)

        if response.status_code != 200:
            error_response = ErrorResponse(**response.json())
            for error in error_response.errors:
                print(f"[red]{error.detail}[/red]")
            raise Exception("API request failed")

        api_response = ProjectsResponse(**response.json())
        return api_response

    def list_projects(self) -> None:
        print(f"Listing projects for user {self.username}")
        response = self._get_projects(
            f"https://api.agouti.eu/projects?filter%5Buser%5D={self.user_id}&page%5Blimit%5D=25&page%5Boffset%5D=0"
        )
        # Don't print the full response object - it causes issues with Pydantic Generic models
        print(f"Found {len(response.data)} projects")
        for project in response.data:
            print(f"- (ID: {project.id}) {project.attributes.name}")

    def _get_observations(self, url: str):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = get(url, headers=headers)
        if response.status_code != 200:
            error_response = ErrorResponse(**response.json())
            for error in error_response.errors:
                print(f"[red]{error.detail}[/red]")
            raise Exception("API request failed")
        api_response = ObservationsResponse(**response.json())
        return api_response

    def list_observations(self, project_id: str, filter_observation_type: Optional[str] = None) -> List[Observation]:
        print(f"Listing observations for project {project_id}")
        url = f"https://api.agouti.eu/observations?filter%5Bcustom-deployments-filter%5D=true&filter%5Bcustom-filter%5D=true&filter%5Bproject%5D={project_id}&page%5Blimit%5D=25&page%5Boffset%5D=0"
        if filter_observation_type:
            url += f"&filter%5BobservationType%5D={filter_observation_type}"
        response = self._get_observations(url)
        print(f"Found {len(response.data)} observations")
        return response.data
        
    def _get_deployments(self, url: str):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = get(url, headers=headers)
        if response.status_code != 200:
            error_response = ErrorResponse(**response.json())
            for error in error_response.errors:
                print(f"[red]{error.detail}[/red]")
            raise Exception("API request failed")
        api_response = DeploymentsResponse(**response.json())
        return api_response

    def _get_deployment_calibrations(self, url: str):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = get(url, headers=headers)
        if response.status_code != 200:
            error_response = ErrorResponse(**response.json())
            for error in error_response.errors:
                print(f"[red]{error.detail}[/red]")
            raise Exception("API request failed")
        api_response = DeploymentCalibrationsResponse(**response.json())
        return api_response

    def list_deployment_calibrations(self, deployment_id: str) -> List[DeploymentCalibration]:
        print(f"Listing deployment calibrations for deployment {deployment_id}")
        response = self._get_deployment_calibrations(
            f"https://api.agouti.eu/deploymentcalibrations?filter%5Bdeployment%5D={deployment_id}"
        )
        return response.data

    def download_asset(self, asset_id: str):
        print(f"Downloading asset {asset_id}")
        url = f"https://api.agouti.eu/assets/{asset_id}/file"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = get(url, headers=headers)
        if response.status_code != 200:
            error_response = ErrorResponse(**response.json())
            for error in error_response.errors:
                print(f"[red]{error.detail}[/red]")
            raise Exception("API request failed")
        return response


    def list_project_deployments(self, project_id: str) -> List[Deployment]:
        # https://api.agouti.eu/deployments?filter%5Bcustom-deployments-filter%5D=true&filter%5Bcustom-filter%5D=true&filter%5Bproject%5D=0859a83e-aec5-4764-99e7-9ca7b0a9653e&page%5Blimit%5D=100&page%5Boffset%5D=0
        print(f"Listing deployments for project {project_id}")
        response = self._get_deployments(
            f"https://api.agouti.eu/deployments?filter%5Bcustom-deployments-filter%5D=true&filter%5Bcustom-filter%5D=true&filter%5Bproject%5D={project_id}&page%5Blimit%5D=100&page%5Boffset%5D=0"
        )
        print(f"Found {len(response.data)} deployments")
        return response.data

    def export_deployment_calibrations(self, project_id: str, output_file: str) -> None:
        print(f"Exporting deployment calibrations for project {project_id} to {output_file}")
        # Implementation goes here
        pass

    def list_observation_positions(self, observation_id: str) -> List['ObservationPosition']:
        # https://api.agouti.eu/observationpositions?auth_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY3Rpb24iOiJzZXNzaW9uIiwiaWQiOiJkZjIxMzMwYy02YTY5LTQxYzAtOWUzMS0zOTY5OWUxOWJiZDQiLCJpYXQiOjE3Njg4MzIyOTgsImV4cCI6MTc2OTQzNzA5OH0.CPnf2DFWMdVQQUrRhD4quWtcdklvextZp5Sr57jVuwM&filter[observation]=6973262b-322a-41e1-9457-f2d1eb647214
        url = f"https://api.agouti.eu/observationpositions?filter%5Bobservation%5D={observation_id}"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = get(url, headers=headers)
        if response.status_code != 200:
            error_response = ErrorResponse(**response.json())
            for error in error_response.errors:
                print(f"[red]{error.detail}[/red]")
            raise Exception("API request failed")
        api_response = ObservationPositionsResponse(**response.json())
        return api_response.data
        

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

class ObservationPositionsResponse(BaseModel):
    class JsonApiDetails(BaseModel):
        version: str

    data: List[ObservationPosition]
    jsonapi: JsonApiDetails