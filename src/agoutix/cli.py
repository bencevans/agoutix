from pathlib import Path
from typing import List, Optional
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
    content, filename = agouti.download_asset(asset_id)

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

    asset_id_to_filename = {}

    annotations_by_asset_id = {}
    for calibration in annotations:
        annotations_by_asset_id.setdefault(calibration.asset_id, []).append(calibration)

    for asset_id in tqdm(asset_ids, desc="Downloading assets"):
        content, filename = agouti.download_asset(asset_id)
        asset_id_to_filename[asset_id] = filename

    calibration_dataset = CalibrationDataset(
        images=[
            CalibrationDataset.CalibrationDatasetImage(
                asset_id=asset_id,
                filename=asset_id_to_filename[asset_id],
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


def export_observation_positions_dataset(
    agouti: Agouti, project_id: str, output_file: str = "observation_positions.csv"
) -> None:
    print(f"Exporting observation positions dataset for project {project_id}")
    observations = agouti.list_project_observations(
        project_id, filter_observation_type="Species"
    )
    print(f"Total observations found: {len(observations)}")

    # Enumerate Observation Positions
    observation_positions = [
        agouti.list_observation_positions(obs.attributes.observation_id)
        for obs in tqdm(observations, desc="Collecting observation positions")
        if obs.attributes.observation_type == "Species"
    ]

    observation_positions_flat = [
        pos for sublist in observation_positions for pos in sublist
    ]
    print(f"Total observation positions found: {len(observation_positions_flat)}")

    asset_ids = {pos.attributes.asset for pos in observation_positions_flat}
    print(f"Total unique assets to download: {len(asset_ids)}")
