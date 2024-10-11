# bouajajais/dockerfiles-orchestrator

`bouajajais/dockerfiles-orchestrator` is a tool designed to help you manage and update multiple repositories by building and pushing Docker images with new versions. It also updates the README files of each of those repositories.

## Features

- Build Docker images for multiple repositories.
- Push Docker images to a registry.
- Update README files with new versions.

## Managed Repositories

This orchestrator manages the following repositories:

- [https://github.com/bouajajais/poetry](https://github.com/bouajajais/poetry)
- [https://github.com/bouajajais/poetry-init](https://github.com/bouajajais/poetry-init)
- [https://github.com/bouajajais/cuda-python](https://github.com/bouajajais/cuda-python)
- [https://github.com/bouajajais/cuda-poetry](https://github.com/bouajajais/cuda-poetry)

## Usage

1. Clone this repository:
    ```sh
    git clone https://github.com/bouajajais/dockerfiles-orchestrator.git
    cd dockerfiles-orchestrator
    ```

2. Configure the repositories and Docker settings in the configuration file.

3. Run the orchestrator script to build and push Docker images and update README files:
    ```sh
    python update_images.py
    ```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.