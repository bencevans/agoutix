from typing import List
from rich import print
from agouti_annotation_exporter.agouti import Agouti
from pydantic import BaseModel
from tqdm import tqdm


class ExportCalibrationAnnotation(BaseModel):
    project_id: str
    deployment_id: str
    calibration_id: str
    asset_id: str
    label: str
    x: str
    y: str
    height: str


def export_calibration_dataset(agouti: Agouti, project_id: str) -> None:
    deployments = agouti.list_project_deployments(project_id)
    print(f"Exporting calibration dataset for project {project_id}")

    all_calibrations: List[ExportCalibrationAnnotation] = []

    # Enumerate Calibration Annotations
    for deployment in deployments:
        calibrations = agouti.list_deployment_calibrations(deployment.id)

        for calibration in calibrations:
            print(f"- Deployment ID: {deployment.id}, Calibration ID: {calibration.id}")

            annotation = ExportCalibrationAnnotation(
                project_id=project_id,
                deployment_id=deployment.id,
                calibration_id=calibration.id,
                asset_id=calibration.attributes.asset,
                label=calibration.attributes.label,
                x=calibration.attributes.x,
                y=calibration.attributes.y,
                height=calibration.attributes.height,
            )
            all_calibrations.append(annotation)

    print(f"Total calibration annotations found: {len(all_calibrations)}")

    asset_ids = {calibration.asset_id for calibration in all_calibrations}
    print(f"Total unique assets to download: {len(asset_ids)}")

    asset_id_to_filename = {}

    for asset_id in asset_ids:
        response = agouti.download_asset(asset_id)
        filename = (
            response.headers.get("Content-Disposition", f"asset-{asset_id}")
            .split("filename=")[-1]
            .strip('"')
        )
        print(f"Saving asset {asset_id} to {filename}")
        with open(filename, "wb") as f:
            f.write(response.content)
        asset_id_to_filename[asset_id] = filename

    # Save calibration annotations to CSV
    import csv

    output_csv = f"calibration_annotations_{project_id}.csv"
    with open(output_csv, "w", newline="") as csvfile:
        fieldnames = [
            "project_id",
            "deployment_id",
            "calibration_id",
            "asset_id",
            "asset_filename",
            "label",
            "x",
            "y",
            "height",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for calibration in all_calibrations:
            writer.writerow(
                {
                    **calibration.dict(),
                    "asset_filename": asset_id_to_filename.get(
                        calibration.asset_id, ""
                    ),
                }
            )


def export_observation_positions_dataset(
    agouti: Agouti, project_id: str, output_file: str = "observation_positions.csv"
) -> None:
    print(f"Exporting observation positions dataset for project {project_id}")
    observations = agouti.list_observations(
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
