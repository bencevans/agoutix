import agoutix
from pathlib import Path
from typing import List, Optional, Tuple
from rich import print
from agoutix.agouti import Agouti
from pydantic import BaseModel
from tqdm import tqdm


def list_projects(agouti: Agouti) -> None:
    projects = agouti.list_projects()
    print("Projects:")
    for project in projects:
        print(f"- ID: {project.id}, Name: {project.attributes.name}")


def list_deployments(agouti: Agouti, project_id: str) -> None:
    deployments = agouti.list_project_deployments(project_id)
    print(f"Deployments for Project ID {project_id}:")
    for deployment in deployments:
        print(
            f"- ID: {deployment.id}, Inspected: {deployment.attributes.percent_inspected}%"
        )


def list_project_observations(agouti: Agouti, project_id: str) -> None:
    observations = agouti.list_project_observations(project_id)
    print(f"Observations for Project ID {project_id}:")
    for observation in observations:
        print(
            f"- ID: {observation.id}, Type: {observation.attributes.observation_type}, "
            f"Sampling Point: {observation.attributes.sampling_point}, "
            f"Scientific Name: {observation.attributes.scientific_name}"
        )


def list_deployment_calibrations(agouti: Agouti, deployment_id: str) -> None:
    calibrations = agouti.list_deployment_calibrations(deployment_id)
    print(f"Calibrations for Deployment ID {deployment_id}:")
    for calibration in calibrations:
        print(
            f"- ID: {calibration.id}, Label: {calibration.attributes.label}, "
            f"Asset: {calibration.attributes.asset}, X: {calibration.attributes.x}, "
            f"Y: {calibration.attributes.y}, Height: {calibration.attributes.height}"
        )


def download_asset(
    agouti: Agouti, asset_id: str, output_path: Optional[Path] = None
) -> None:
    content, filename = agouti.get_asset_file(asset_id)

    if output_path is None:
        output_path = Path(filename)

    elif output_path.is_dir():
        output_path = output_path / filename

    print(f"Downloading asset {asset_id} to file {output_path}")
    with open(output_path, "wb") as f:
        f.write(content)


class ExportCalibrationAnnotation(BaseModel):
    project_id: str
    deployment_id: str
    calibration_id: str
    asset_id: str
    label: str
    x: str
    y: str
    height: str


def export_calibration_dataset(agouti: Agouti, project_ids: List[str]) -> None:
    # Enumerate deployments
    for project_id in project_ids:
        deployments = agouti.list_project_deployments(project_id)
        print(f"Exporting calibration dataset for project {project_id}")

        annotations = [
            ExportCalibrationAnnotation(
                project_id=project_id,
                deployment_id=deployment.id,
                calibration_id=calibration.id,
                asset_id=calibration.attributes.asset,
                label=calibration.attributes.label,
                x=calibration.attributes.x,
                y=calibration.attributes.y,
                height=calibration.attributes.height,
            )
            for deployment in deployments
            for calibration in agouti.list_deployment_calibrations(deployment.id)
        ]

    asset_ids = {calibration.asset_id for calibration in annotations}
    print(f"Total unique assets to download: {len(asset_ids)}")

    annotations_by_asset_id = {}
    for calibration in annotations:
        annotations_by_asset_id.setdefault(calibration.asset_id, []).append(calibration)

    assets_by_id = {
        asset_id: agouti.get_asset(asset_id)
        for asset_id in tqdm(asset_ids, desc="Downloading assets")
    }

    # for asset_id in tqdm(asset_ids, desc="Downloading assets"):
    #     content, filename = agouti.get_asset_file(asset_id)
    #     asset_id_to_filename[asset_id] = filename

    calibration_dataset = CalibrationDataset(
        images=[
            CalibrationDataset.CalibrationDatasetImage(
                asset_id=asset_id,
                filename=assets_by_id[asset_id].attributes.filename,
                project_id=annotations[0].project_id,
                deployment_id=annotations[0].deployment_id,
                annotations=[
                    CalibrationDataset.CalibrationDatasetImage.CalibrationAnnotation(
                        calibration_id=ann.calibration_id,
                        label=ann.label,
                        x=float(ann.x),
                        y=float(ann.y),
                        height=float(ann.height),
                    )
                    for ann in annotations_by_asset_id[asset_id]
                ],
            )
            for asset_id in asset_ids
        ],
    )

    calibration_dataset_path = Path(f"calibration_dataset_project_{project_id}.json")
    print(f"Saving calibration dataset to {calibration_dataset_path}")
    with open(calibration_dataset_path, "w") as f:
        f.write(calibration_dataset.model_dump_json(indent=2))


class CalibrationDataset(BaseModel):
    class CalibrationDatasetImage(BaseModel):
        class CalibrationAnnotation(BaseModel):
            calibration_id: str
            label: str
            x: float
            y: float
            height: float

        asset_id: str
        filename: str
        project_id: str
        deployment_id: str
        annotations: List[CalibrationAnnotation]

    images: List[CalibrationDatasetImage]


class ObservationDataset(BaseModel):
    class Image(BaseModel):
        file_name: str
        asset_id: str
        sequence_id: str
        original_filename: str
        created_at: str
        deployment: str
        project_id: str
        width: int
        height: int

    class Observation(BaseModel):
        observation_id: Optional[str]
        scientific_name: Optional[str]
        observation_type: str
        sampling_point: str

    class Position(BaseModel):
        position_id: str
        observation_id: str
        asset_id: str
        x: float
        y: float

    images: List[Image]
    observations: List[Observation]
    positions: List[Position]


def export_observation_positions_dataset(
    agouti: Agouti,
    project_ids: List[str],
    output_path: Optional[Path] = None,
) -> None:
    output_path = output_path or Path(".")

    observations: List[Tuple[str, agoutix.agouti.Observation]] = []
    for project_id in project_ids:
        print(f"Exporting observation positions dataset for project {project_id}")
        observations.extend(
            [
                (project_id, obs)
                for obs in agouti.list_project_observations(
                    project_id, filter_observation_type="Species"
                )
            ]
        )

    print(f"Total observations found: {len(observations)}")

    # Enumerate Observation Positions
    observation_positions = [
        (project_id, agouti.list_observation_positions(obs.attributes.observation_id))
        for project_id, obs in tqdm(
            observations, desc="Collecting observation positions"
        )
        if obs.attributes.observation_type == "Species"
    ]

    observation_positions_flat = [
        (project_id, pos)
        for (project_id, positions) in observation_positions
        for pos in positions
    ]
    print(f"Total observation positions found: {len(observation_positions_flat)}")

    asset_ids = {
        pos.attributes.asset for (project_id, pos) in observation_positions_flat
    }
    print(f"Total unique assets to download: {len(asset_ids)}")

    # Create assets directory
    assets_dir_path = output_path / "assets"
    assets_dir_path.mkdir(parents=True, exist_ok=True)

    assets_by_id = {
        asset_id: agouti.get_asset(asset_id)
        for asset_id in tqdm(asset_ids, desc="Retrieving asset metadata")
    }

    # Build dataset
    dataset = ObservationDataset(
        images=[
            ObservationDataset.Image(
                file_name=assets_by_id[asset_id].attributes.filename,
                asset_id=asset_id,
                sequence_id=img.attributes.sequence,
                original_filename=img.attributes.original_filename,
                created_at=img.attributes.created_at,
                deployment=img.attributes.deployment,
                project_id=project_id,
                width=img.attributes.width,
                height=img.attributes.height,
            )
            for asset_id, img in [
                (pos.attributes.asset, assets_by_id[pos.attributes.asset])
                for (project_id, pos) in observation_positions_flat
            ]
        ],
        observations=[
            ObservationDataset.Observation(
                observation_id=obs.attributes.observation_id,
                scientific_name=obs.attributes.scientific_name,
                observation_type=obs.attributes.observation_type,
                sampling_point=obs.attributes.sampling_point,
            )
            for (project_id, obs) in observations
        ],
        positions=[
            ObservationDataset.Position(
                position_id=pos.id,
                observation_id=pos.attributes.observation,
                asset_id=pos.attributes.asset,
                # Agouti stores positions as relative to 640px width, both x and y and relative to the image width.
                x=float(pos.attributes.x)
                * assets_by_id[pos.attributes.asset].attributes.width
                / 640,
                y=float(pos.attributes.y)
                * assets_by_id[pos.attributes.asset].attributes.width
                / 640,
            )
            for (project_id, pos) in observation_positions_flat
        ],
    )

    dataset_path = output_path / "observation_positions_dataset.json"
    print(f"Saving observation positions dataset to {dataset_path}")
    with open(dataset_path, "w") as f:
        f.write(dataset.model_dump_json(indent=2))

    #  Download assets
    for asset_id in tqdm(asset_ids, desc="Downloading assets"):
        content, filename = agouti.get_asset_file(asset_id)
        asset_path = assets_dir_path / filename
        with open(asset_path, "wb") as f:
            f.write(content)


def export_camtrapdp_dataset(
    agouti: Agouti, project_id: str, output_path: Optional[Path] = None
) -> None:
    from .public import AgoutiPublicAPI, AuthJWT

    output_path = output_path or Path("export")
    output_path.mkdir(parents=True, exist_ok=True)

    public_api = AgoutiPublicAPI(AuthJWT(agouti.token))

    print(f"Exporting project {project_id} as CamtrapDP datapackage")

    # datapackage = public_api.export_project_datapackage(project_id)
    # datapackage_path = output_path / "datapackage.json"
    # print(f"Saving datapackage to {datapackage_path}")
    # with open(datapackage_path, "w") as f:
    #     f.write(datapackage.model_dump_json(indent=2))

    deployments = public_api.export_project_deployments_csv(project_id)
    deployments_path = output_path / "deployments.csv"
    print(f"Saving deployments CSV to {deployments_path}")
    with open(deployments_path, "w") as f:
        f.write(deployments)

    observations = public_api.export_project_observations_csv(project_id)
    observations_path = output_path / "observations.csv"
    print(f"Saving observations CSV to {observations_path}")
    with open(observations_path, "w") as f:
        f.write(observations)

    media = public_api.export_project_media_csv(project_id)
    media_path = output_path / "media.csv"
    print(f"Saving media CSV to {media_path}")
    with open(media_path, "w") as f:
        f.write(media)

    print("Export complete")
