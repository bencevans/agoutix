# Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## Development Setup

The project uses [uv](https://docs.astral.sh/uv/) for development and testing. To set up the development environment, ensure you have `uv` installed, then run:

```bash
# Download the repository
git clone ...
cd agoutix

# Setup the development environment
uv sync
```

Then to run the tool from the development environment, use:

```bash
uv run agoutix --help
```

## Testing

To run the tests, you need to have a number of environment variables set for authentication and asserting expected values.

```bash
export AGOUTI_EMAIL="your_email"
export AGOUTI_PASSWORD="your_password"
export AGOUTI_PROJECT_ID="your_project_id"
export AGOUTI_PROJECT_ID_N_OBSERVATIONS=32 # number_of_observations_in_project
export AGOUTI_PROJECT_ID_N_DEPLOYMENTS=10 # number_of_deployments_in_project
export AGOUTI_ASSET_ID="your_asset_id"
export AGOUTI_ASSET_FILENAME="your_asset_filename.jpg"
```

Then run the tests with:

```bash
uv run pytest
```
