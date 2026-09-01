# Agoutix




A Python package and command-line tool for exporting annotation datasets from [Agouti](https://www.agouti.eu/) projects.

Agoutix is not affiliated with or endorsed by the creators of Agouti. This tool is developed independently to facilitate data export and analysis for users of the Agouti platform.

Agoutix makes use of the Agouti API used by the Agouti web application. Agouti now has a [public API](https://api.agouti.eu/docs/), however Agoutix uses some API calls that aren't documented, and may change without notice. Use Agoutix at your own risk.

**Table of Contents**

- [Agoutix](#agoutix)
  - [Features](#features)
  - [Installation](#installation)
  - [Usage (Python API)](#usage-python-api)
  - [Usage (Command-Line Interface)](#usage-command-line-interface)
    - [List Projects](#list-projects)
    - [Export Calibration Dataset](#export-calibration-dataset)
    - [Export Observation Positions](#export-observation-positions)
  - [Acknowledgements](#acknowledgements)
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

A Calibration dataset contains all calibration pole annotations for a project.

```bash
agoutix --email YOUR_EMAIL --password YOUR_PASSWORD export-calibration-dataset --project-id YOUR_PROJECT_ID
```

A JSON formatted file named `calibration_dataset_project_<PROJECT_ID>.json` will be created in the current directory, containing all calibration pole annotations for the specified project.

```json
{
  "images": [
    {
      "asset_id": "a8b4c7e2-1f3a-4b6d-8c9e-0d5f2a7b9c1e",
      "filename": "image_001.jpg",
      "project_id": "41cb7cb1-a511-4632-8d7f-1c717c81af97",
      "deployment_id": "2b32fd97-d017-444d-92b5-2a6f8c822bd6",
      "annotations": [
        {
          "calibration_id": "e046191a-a475-453d-bb94-bf67f86122b4",
          "label": "top",
          "x": 0.34,
          "y": 0.78,
          "height": 0.6
        },
        {
          "calibration_id": "b8ff0533-4ce3-4615-ba76-22a275dfd82d",
          "label": "bottom",
          "x": 0.34,
          "y": 0.95,
          "height": 0.6
        }
      ]
    }
  ]
}
```

The dataset is structured as follows:
- **images**: Array of images containing calibration annotations
  - **asset_id**: Unique identifier for the image asset
  - **filename**: Original filename of the image
  - **project_id**: Project ID this image belongs to
  - **deployment_id**: Deployment ID this image belongs to
  - **annotations**: Array of calibration pole annotations
    - **calibration_id**: Unique identifier for the calibration annotation
    - **label**: Position label ("top" or "bottom")
    - **x**: X coordinate (normalized to 0-1 range)
    - **y**: Y coordinate (normalized to 0-1 range)
    - **height**: Height of the calibration pole

### Export Observation Positions

An Observation Positions dataset contains all observation position annotations (e.g., front-leg positions) for all species observations in a project. This command also downloads all associated image assets to a local `assets/` directory.

```bash
agoutix --email YOUR_EMAIL --password YOUR_PASSWORD export-observation-positions --project-id YOUR_PROJECT_ID
```

A JSON formatted file named `observation_positions_dataset.json` will be created in the current directory, and all image assets will be downloaded to the `assets/` subdirectory.
Position lookups, asset metadata requests, and downloads run concurrently. Use
`--workers N` to tune concurrency (the default is 8); reduce it if the API starts
rate-limiting requests.

```json
{
  "images": [
    {
      "file_name": "20250115182634-IMG_0467.JPG",
      "asset_id": "38956f9a-9edb-4d72-97bc-05ac32f2a80d",
      "sequence_id": "58d7636f-7c03-4796-9e11-c6e624c3b569",
      "original_filename": "IMG_0467.JPG",
      "created_at": "2023-07-30T23:57:05.000Z",
      "deployment": "ce839553-8d38-454d-98b6-9f34b159eef1",
      "project_id": "080d2776-9411-4799-be28-19aa4a1eb652",
      "width": 2688,
      "height": 1512
    }
  ],
  "observations": [
    {
      "observation_id": "7e932f89-58ee-41de-9fda-d83adbda29ec",
      "scientific_name": "Meles meles",
      "observation_type": "Species",
      "sampling_point": "04_NHMP_054_Brackenhurst23 (15367)"
    }
  ],
  "positions": [
    {
      "position_id": "1ae3607a-ada4-4637-8037-5f3bd37b3c99",
      "observation_id": "7e932f89-58ee-41de-9fda-d83adbda29ec",
      "asset_id": "38956f9a-9edb-4d72-97bc-05ac32f2a80d",
      "x": 1008.0,
      "y": 1825.15
    }
  ]
}
```

The dataset is structured as follows:
- **images**: Array of image metadata
  - **file_name**: Filename of the image
  - **asset_id**: Unique identifier for the image asset
  - **sequence_id**: Sequence identifier
  - **original_filename**: Original filename as uploaded
  - **created_at**: Timestamp when the image was created
  - **deployment**: Deployment ID
  - **project_id**: Project ID
  - **width**: Image width in pixels
  - **height**: Image height in pixels
- **observations**: Array of observation metadata
  - **observation_id**: Unique identifier for the observation
  - **scientific_name**: Species scientific name
  - **observation_type**: Type of observation (always "Species" for this dataset)
  - **sampling_point**: Sampling point name
- **positions**: Array of keypoint annotations
  - **position_id**: Unique identifier for the position annotation
  - **observation_id**: Associated observation ID
  - **asset_id**: Associated image asset ID
  - **x**: X coordinate in pixels (adjusted to actual image dimensions)
  - **y**: Y coordinate in pixels (adjusted to actual image dimensions)

## Acknowledgements

Thank you to the Agouti Team for creating an excellent platform for camera trap data management and generous support during development and delivery of the NHMP pilot project and broader community.

This tool was developed by Ben Evans at the Institute of Zoology, ZSL as part of the [NHMP](https://www.nhmp.org.uk/) project.

We would like to thank Natural England which provided the majority of the funds to support the NHMP pilot through the Species Recovery Programme funding stream. People’s Trust for Endangered Species and British Hedgehog Preservation Society also contributed significant funds to enable the pilot project to extend to Wales and Scotland


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
