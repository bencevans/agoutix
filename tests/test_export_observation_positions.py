import json
import threading
import time
from types import SimpleNamespace

import pytest

from agoutix.cli import export_observation_positions_dataset


def resource(resource_id, **attributes):
    return SimpleNamespace(id=resource_id, attributes=SimpleNamespace(**attributes))


class FakeAgouti:
    def __init__(self):
        self.active_requests = 0
        self.max_active_requests = 0
        self.lock = threading.Lock()

    def _request(self):
        with self.lock:
            self.active_requests += 1
            self.max_active_requests = max(
                self.max_active_requests, self.active_requests
            )
        time.sleep(0.01)
        with self.lock:
            self.active_requests -= 1

    def list_project_observations(self, project_id, filter_observation_type=None):
        return [
            resource(
                f"cached-{index}",
                observation_id=f"observation-{index}",
                scientific_name="Meles meles",
                observation_type="Species",
                sampling_point="camera-1",
            )
            for index in range(4)
        ]

    def list_observation_positions(self, observation_id):
        self._request()
        index = observation_id.rsplit("-", 1)[-1]
        return [
            resource(
                f"position-{index}",
                observation=observation_id,
                asset=f"asset-{int(index) % 2}",
                x="320",
                y="160",
            )
        ]

    def get_asset(self, asset_id):
        self._request()
        return resource(
            asset_id,
            filename=f"{asset_id}.jpg",
            sequence=f"sequence-{asset_id}",
            original_filename=f"original-{asset_id}.jpg",
            created_at="2026-01-01T00:00:00Z",
            deployment="deployment-1",
            width=1280,
            height=720,
        )

    def get_asset_file(self, asset_id):
        self._request()
        return asset_id.encode(), f"{asset_id}.jpg"


def test_export_fetches_concurrently_and_emits_unique_images(tmp_path):
    agouti = FakeAgouti()

    export_observation_positions_dataset(
        agouti, ["project-1"], tmp_path, workers=4
    )

    dataset = json.loads(
        (tmp_path / "observation_positions_dataset.json").read_text()
    )
    assert agouti.max_active_requests > 1
    assert len(dataset["observations"]) == 4
    assert len(dataset["positions"]) == 4
    assert {image["asset_id"] for image in dataset["images"]} == {
        "asset-0",
        "asset-1",
    }
    assert (tmp_path / "assets" / "asset-0.jpg").read_bytes() == b"asset-0"
    assert (tmp_path / "assets" / "asset-1.jpg").read_bytes() == b"asset-1"


def test_export_rejects_invalid_worker_count(tmp_path):
    with pytest.raises(ValueError, match="workers must be at least 1"):
        export_observation_positions_dataset(FakeAgouti(), [], tmp_path, workers=0)
