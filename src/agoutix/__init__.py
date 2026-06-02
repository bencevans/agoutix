from agoutix.agouti import Agouti


def parse_args():
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Agouti Multi-tool")
    parser.add_argument("--email", required=True, help="Agouti login email")
    parser.add_argument("--password", required=True, help="Agouti password")
    subparsers = parser.add_subparsers(dest="command")

    # list-projects
    subparsers.add_parser("list-projects", help="List all projects")

    # list-observations --project-id <project_id>
    list_observations_parser = subparsers.add_parser(
        "list-observations", help="List all observations for a project"
    )
    list_observations_parser.add_argument(
        "--project-id", required=True, help="Project ID"
    )

    # list-deployment-calibrations --deployment-id <deployment_id>
    list_deployment_calibrations_parser = subparsers.add_parser(
        "list-deployment-calibrations",
        help="List all deployment calibrations for a deployment",
    )
    list_deployment_calibrations_parser.add_argument(
        "--deployment-id", required=True, help="Deployment ID"
    )

    # download-asset --asset-id <asset_id> [--output-path <output_path>]
    download_asset_parser = subparsers.add_parser(
        "download-asset", help="Download an asset by its ID"
    )
    download_asset_parser.add_argument("--asset-id", required=True, help="Asset ID")
    download_asset_parser.add_argument(
        "--output-path",
        required=False,
        help="Output path for the downloaded asset",
    )

    # export-deployment-calibrations --project-id <project_id>,<project_id>,...
    export_calibrations_parser = subparsers.add_parser(
        "export-calibration-dataset",
        help="Export deployment calibrations dataset for a project",
    )
    export_calibrations_parser.add_argument(
        "--project-id", required=True, help="Project ID", nargs="+"
    )

    # export-observation-positions --project-id <project_id>,<project_id>,...
    export_observation_positions_parser = subparsers.add_parser(
        "export-observation-positions",
        help="Export observation positions dataset for a project",
    )
    export_observation_positions_parser.add_argument(
        "--project-id", required=True, help="Project ID", nargs="+"
    )
    export_observation_positions_parser.add_argument(
        "--output-path",
        required=False,
        help="Output path for the observation positions dataset",
    )

    export_camtrapdp_parser = subparsers.add_parser(
        "export-camtrapdp",
        help="Export CamtrapDP dataset for a project",
    )
    export_camtrapdp_parser.add_argument(
        "--project-id", required=True, help="Project ID", type=str
    )
    export_camtrapdp_parser.add_argument(
        "--output-path",
        required=False,
        help="Output path for the CamtrapDP dataset",
    )

    return parser.parse_args()


def main() -> None:
    from pathlib import Path
    from rich import print
    from agoutix import cli

    args = parse_args()

    if not args.command:
        print("[red]No command provided. Use --help for more information.[/red]")
        return

    agouti = Agouti(args.email, args.password)

    if args.command == "list-projects":
        cli.list_projects(agouti)

    elif args.command == "list-observations":
        cli.list_project_observations(agouti, args.project_id)

    elif args.command == "list-deployment-calibrations":
        cli.list_deployment_calibrations(agouti, args.deployment_id)

    elif args.command == "download-asset":
        cli.download_asset(
            agouti, args.asset_id, Path(args.output_path) if args.output_path else None
        )

    elif args.command == "export-calibration-dataset":
        cli.export_calibration_dataset(agouti, args.project_id)

    elif args.command == "export-observation-positions":
        cli.export_observation_positions_dataset(agouti, args.project_id, Path(args.output_path) if args.output_path else None)

    elif args.command == "export-camtrapdp":
        cli.export_camtrapdp_dataset(agouti, args.project_id, Path(args.output_path) if args.output_path else None)

    else:
        raise NotImplementedError(f"Command {args.command} not implemented")
