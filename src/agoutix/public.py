"""
Agouti Public API Client
"""

from typing import Optional
import requests


class AuthAPIKey:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def __call__(self, r):
        r.headers["X-API-KEY"] = f"Bearer {self.api_key}"
        return r


class AuthJWT:
    def __init__(self, jwt_token: str):
        self.jwt_token = jwt_token

    def __call__(self, r):
        r.headers["Authorization"] = f"Bearer {self.jwt_token}"
        return r


class AgoutiPublicAPI:
    """Client for Agouti Public API

    Endpoint documentation at https://docs.agouti.eu/api/endpoints.html
    """

    base_url = "https://api.agouti.eu/v1"

    def __init__(self, auth_scheme: AuthAPIKey | AuthJWT):
        self.auth_scheme = auth_scheme

    def _get(self, endpoint: str, params: Optional[dict] = None):
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, params=params, auth=self.auth_scheme)
        response.raise_for_status()
        return response.json()

    def _post(self, endpoint: str, data: Optional[dict] = None):
        url = f"{self.base_url}/{endpoint}"
        response = requests.post(url, json=data, auth=self.auth_scheme)
        response.raise_for_status()
        return response.json()

    def _patch(self, endpoint: str, data: Optional[dict] = None):
        url = f"{self.base_url}/{endpoint}"
        response = requests.patch(url, json=data, auth=self.auth_scheme)
        response.raise_for_status()
        return response.json()

    def _delete(self, endpoint: str):
        url = f"{self.base_url}/{endpoint}"
        response = requests.delete(url, auth=self.auth_scheme)
        response.raise_for_status()
        return response.status_code == 204

    def list_projects(self):
        return self._get("me/projects")

    def get_project(self, project_id: str):
        return self._get(f"projects/{project_id}")

    def list_project_cameras(self, project_id: str):
        return self._get(f"projects/{project_id}/cameras")

    def add_project_camera(self, project_id: str, camera_details: dict):
        url = f"{self.base_url}/projects/{project_id}/cameras"
        response = self._post(url, data=camera_details)
        return response.json()

    def update_project_camera(
        self, project_id: str, camera_id: str, camera_details: dict
    ):
        url = f"{self.base_url}/projects/{project_id}/cameras/{camera_id}"
        response = self._patch(url, data=camera_details)
        return response.json()

    def delete_project_camera(self, project_id: str, camera_id: str):
        url = f"{self.base_url}/projects/{project_id}/cameras/{camera_id}"
        response = self._delete(url)
        return response

    def list_project_locations(self, project_id: str):
        return self._get(f"projects/{project_id}/locations")

    def add_project_location(self, project_id: str, location_details: dict):
        url = f"{self.base_url}/projects/{project_id}/locations"
        response = self._post(url, data=location_details)
        return response.json()

    def update_project_location(
        self, project_id: str, location_id: str, location_details: dict
    ):
        url = f"{self.base_url}/projects/{project_id}/locations/{location_id}"
        response = self._patch(url, data=location_details)
        return response.json()

    def delete_project_location(self, project_id: str, location_id: str):
        url = f"{self.base_url}/projects/{project_id}/locations/{location_id}"
        response = self._delete(url)
        return response

    def list_project_deployments(self, project_id: str):
        return self._get(f"projects/{project_id}/deployments")

    def add_project_deployment(self, project_id: str, deployment_details: dict):
        url = f"{self.base_url}/projects/{project_id}/deployments"
        response = self._post(url, data=deployment_details)
        return response.json()

    def get_project_deployment(self, project_id: str, deployment_id: str):
        return self._get(f"projects/{project_id}/deployments/{deployment_id}")

    def get_project_deployment_status(self, project_id: str, deployment_id: str):
        return self._get(f"projects/{project_id}/deployments/{deployment_id}/status")

    def upload_project_deployment_files(
        self, project_id: str, deployment_id: str, files: dict[str, bytes]
    ):
        url = f"projects/{project_id}/deployments/{deployment_id}/files"
        response = requests.post(url, files=files, auth=self.auth_scheme)
        response.raise_for_status()
        return response.json()

    def finalise_project_deployment(self, project_id: str, deployment_id: str):
        url = f"projects/{project_id}/deployments/{deployment_id}/finalise"
        response = self._post(url)
        return response.text()

    def export_project_deployments_csv(self, project_id: str):
        url = f"projects/{project_id}/deployments.csv"
        response = self._post(url)
        return response.text()

    def export_project_media_csv(self, project_id: str):
        url = f"projects/{project_id}/media.csv"
        response = self._post(url)
        return response.text()

    def export_project_observations_csv(self, project_id: str):
        url = f"projects/{project_id}/observations.csv"
        response = self._post(url)
        return response.text()

    def export_project_datapackage(self, project_id: str):
        url = f"projects/{project_id}/datapackage.json"
        response = self._post(url)
        return response.json()
