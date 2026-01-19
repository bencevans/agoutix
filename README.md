# Agouti Annotation Exporter

A command-line tool to export annotations data from the Agouti platform with a focus on REM calibration annotations.

## Installation

You can install the package using pip:

```bash
pip install agouti-annotation-exporter
```

Or if you have [uv] installed, you can run the tool directly by prefixing the command with `uvx`. e.g.,

```bash
uvx agouti-annotation-exporter --help
```

## Usage

### 1. List Projects

To use the Agouti Annotation Exporter, first run the following command to list all projects associated with your account:

```bash
agouti-annotation-exporter --username YOUR_USERNAME --password YOUR_PASSWORD list-projects
```

Replace `YOUR_USERNAME` and `YOUR_PASSWORD` with your actual Agouti account credentials.

This will display a list of all projects available in your Agouti account.

### 2. Export Calibration Dataset

A Calibration dataset contains all calibration pole annotations.

```bash
agouti-annotation-exporter --username YOUR_USERNAME --password YOUR_PASSWORD export-calibration-dataset --project-id YOUR_PROJECT_ID
```

A JSON formatted file named `calibration_dataset.json` will be created in the current directory, containing all calibration pole annotations for the specified project.

```json
[
  {
    "asset_id": "123456767",
    "asset_filename": "image_001.jpg",
    "filename": "123456767-image_001.jpg",
    "keypoints": [
      {
        "label": "top",
        "x": 0.34,
        "y": 0.78,
        "height": 0.6
      },
      {
        "label": "top",
        "x": 0.56,
        "y": 0.45,
        "height": 0.8
      }
    ]
  }
]
```

### 3. Export Observation Positions

An Observation Positions dataset contains all observation position annotations (e.g., front-leg positions) for all species observations in a project.

```bash
agouti-annotation-exporter --username YOUR_USERNAME --password YOUR_PASSWORD export-observation-positions --project-id YOUR_PROJECT_ID
```

A JSON formatted file named `observation_positions.json` will be created in the current directory, containing all observation position annotations for the specified project.

```json
[
  {
    "asset_id": "123456767",
    "asset_filename": "image_001.jpg",
    "filename": "123456767-image_001.jpg",
    "observation_id": "89012345",
    "keypoints": [
      {
        "label": "front-leg",
        "x": 0.45,
        "y": 0.67
      }
    ]
  }
]
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.