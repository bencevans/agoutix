from rich import print
from agouti_annotation_exporter.agouti import Agouti


def parse_args():
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Agouti Annotation Exporter")
    parser.add_argument("--username", required=True, help="Agouti username")
    parser.add_argument("--password", required=True, help="Agouti password")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser(
        "list-projects", help="List all projects"
    )
    list_observations_parser = subparsers.add_parser(
        "list-observations", help="List all observations for a project"
    )
    list_observations_parser.add_argument(
        "--project-id", required=True, help="Project ID"
    )
    list_deployment_calibrations_parser = subparsers.add_parser(
        "list-deployment-calibrations",
        help="List all deployment calibrations for a deployment",
    )
    list_deployment_calibrations_parser.add_argument(
        "--deployment-id", required=True, help="Deployment ID"
    )
    download_asset_parser = subparsers.add_parser(
        "download-asset", help="Download an asset by its ID"
    )
    download_asset_parser.add_argument("--asset-id", required=True, help="Asset ID")
    export_deployment_calibrations_parser = subparsers.add_parser(
        "export-deployment-calibrations",
        help="Export deployment calibration annotations for a project",
    )
    export_deployment_calibrations_parser.add_argument(
        "--project-id", required=True, help="Project ID"
    )
    export_annotations_parser = subparsers.add_parser(
        "export-annotations", help="Export annotations for a project"
    )
    export_annotations_parser.add_argument(
        "--project-id", required=True, help="Project ID"
    )
    export_annotations_parser.add_argument(
        "--output-file", required=True, help="Output file for annotations"
    )
    export_media_parser = subparsers.add_parser(
        "export-media", help="Export media for a project"
    )
    export_media_parser.add_argument("--project-id", required=True, help="Project ID")
    export_media_parser.add_argument(
        "--output-dir", required=True, help="Output directory for media"
    )
    export_annotation_positions_parser = subparsers.add_parser(
        "export-observation-positions",
        help="Export observation position annotations for a project",
    )
    export_annotation_positions_parser.add_argument(
        "--project-id", required=True, help="Project ID"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.command:
        print("[red]No command provided. Use --help for more information.[/red]")
        return

    agouti = Agouti(args.username, args.password)

    if args.command == "list-projects":
        agouti.list_projects()

    elif args.command == "list-observations":
        agouti.list_observations(args.project_id)

    elif args.command == "list-deployment-calibrations":
        agouti.list_deployment_calibrations(args.deployment_id)

    elif args.command == "download-asset":
        response = agouti.download_asset(args.asset_id)

        filename = response.headers.get(
            "Content-Disposition", f"attachment; filename={args.asset_id}"
        ).split("filename=")[1]

        print(f"Saving asset to {args.asset_id}-{filename}")

        with open(f"{args.asset_id}-{filename}", "wb") as f:
            f.write(response.content)

    elif args.command == "export-deployment-calibrations":
        from agouti_annotation_exporter.cli import export_calibration_dataset

        export_calibration_dataset(agouti, args.project_id)

    elif args.command == "export-observation-positions":
        from agouti_annotation_exporter.cli import export_observation_positions_dataset

        export_observation_positions_dataset(agouti, args.project_id)

    else:
        raise NotImplementedError(f"Command {args.command} not implemented")
