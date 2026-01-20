# Agoutix




A Python package and command-line tool for exporting annotation datasets from [Agouti](https://www.agouti.eu/) projects.

Agoutix is not affiliated with or endorsed by the creators of Agouti. This tool is developed independently to facilitate data export and analysis for users of the Agouti platform.

Agoutix makes use of the Agouti API used by the Agouti web application. This API is not publicly documented, and may change without notice. Use Agoutix at your own risk.

**Table of Contents**

- [Agoutix](#agoutix)
  - [Features](#features)
  - [Installation](#installation)
  - [Usage (Python API)](#usage-python-api)
  - [Usage (Command-Line Interface)](#usage-command-line-interface)
    - [List Projects](#list-projects)
    - [Export Calibration Dataset](#export-calibration-dataset)
    - [Export Observation Positions](#export-observation-positions)
  - [Citation](#citation)
  - [License](#license)

## Features

- List projects
- Download media assets
- Export calibration datasets
- Export observation position datasets
- Easy-to-use command-line interface

## Installation

You can install the package using pip:

```bash
pip install agoutix
```

Or if you have [`uv`](https://docs.astral.sh/uv/) installed, you can run the tool directly by prefixing the command with `uvx`. e.g.,

```bash
uvx agoutix --help
```

or add the package to your `uv` project dependencies:

```bash
uv add agoutix
```

## Usage (Python API)

Here's a simple example of how to use Agoutix in your Python code:

```python
from agoutix.agouti import Agouti

# Initialize the Agouti client
client = Agouti(
  email="YOUR_EMAIL",
  password="YOUR_PASSWORD"
)

# List projects
projects = client.list_projects()
for project in projects:
    print(f"Project ID: {project.id}, Name: {project.attributes.name}")

# List observations in a specific project
observations = client.list_project_observations(project_id="YOUR_PROJECT_ID")
for observation in observations:
    print(f"- Observation ID: observation.attributes.observation_id")
    print(f"  Observation Type: {observation.attributes.observation_type}")
    print(f"  Sequence ID: {observation.attributes.sequence_id}")
    print(f"  Scientific Name: {observation.attributes.scientific_name}")
    print(f"  Deployment ID: {observation.attributes.deployment_id}")
```

There are additional methods available. Refer to the [agouti.py](src/agoutix/agouti.py) source code for more details.

## Usage (Command-Line Interface)

The Agoutix command-line tool provides several commands to interact with the Agouti platform. Below are examples of how to use the tool to export different datasets.

### List Projects

To use the Agouti Annotation Exporter, first run the following command to list all projects associated with your account:

```bash
agoutix --email YOUR_EMAIL --password YOUR_PASSWORD list-projects
```

Replace `YOUR_EMAIL` and `YOUR_PASSWORD` with your actual Agouti account credentials.

This will display a list of all projects available in your Agouti account.



### Export Calibration Dataset

A Calibration dataset contains all calibration pole annotations.

```bash
agoutix --email YOUR_EMAIL --password YOUR_PASSWORD export-calibration-dataset --project-id YOUR_PROJECT_ID
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

### Export Observation Positions

An Observation Positions dataset contains all observation position annotations (e.g., front-leg positions) for all species observations in a project.

```bash
agoutix --email YOUR_EMAIL --password YOUR_PASSWORD export-observation-positions --project-id YOUR_PROJECT_ID
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

## Citation

If you use Agoutix in your research, please cite it as follows:

```
@software{agoutix,
  author = {Benjamin C. Evans},
  title = {Agoutix: A Python package and command-line tool for exporting annotation datasets from Agouti projects},
  year = {2026},
  url = {
    "https://github.com/bencevans/agoutix"
  },
}
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
