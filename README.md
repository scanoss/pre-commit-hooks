# SCANOSS Pre-commit Hooks


## Table of Contents
- [Available Hooks](#available-hooks)
- [Installation](#installation)
- [Local Development](#local-development)
- [License](#license)
- [Bugs/Features](#bugsfeatures)
- [Contributing](#contributing)
- [Release and Deployment](#release-and-deployment)
- [Changelog](#changelog)

## Available Hooks
This repository currently includes the following pre-commit hooks:

- **scanoss-check-undeclared-code**
  - This hook checks for potential undeclared open source software in the files being committed.
  - It is designed to run at the `pre-commit`, `pre-push`, and `manual` stages.


## Installation
To get started with this project, you'll need to install the pre-commit package manager and configure it to use the hooks provided in this repository.

### Step 1: Install Pre-commit
You can install pre-commit using various methods:

- **Using PIP**:

  ```bash
  pip install pre-commit
  ```
  
- **Using Homebrew**:

  ```bash
  brew install pre-commit
  ```

For more installation options, refer to the [pre-commit documentation](https://pre-commit.com/).

### Step 2: Configure Pre-commit Hooks

1. In the root of your project repository where you want to use these hooks, create a `.pre-commit-config.yaml` file with the following content:

    ```yaml
    repos:
    -   repo: https://github.com/scanoss/pre-commit-hooks
        rev: v0
        hooks:
        -   id: scanoss-check-undeclared-code
    ```

    Check the latest release [here](https://github.com/scanoss/pre-commit-hooks/releases)

2. Verify config:

    ```bash
   pre-commit validate-config
   ```
   
3. Install the pre-commit hooks:

    ```bash
    pre-commit install
    ```

4. (Optional) Run the hooks against all files to ensure everything is in order:

    ```bash
    pre-commit run --all-files
    ```

## Local Development

**Note:** This project requires a minimum of Python 3.9.

To develop this project locally, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/scanoss/pre-commit-hooks.git
    cd pre-commit-hooks
    ```
2. Create a local branch for isolated development

3. Install dev requirements:
    ```bash
   pip install -r requirements-dev.txt
    ```
4. Set up the development environment using the Makefile:
    ```bash
    make dev_setup
    ```
   This will install the package in development mode with all necessary dependencies.

5. Set up pre-commit hooks:
    ```bash
    pre-commit install
    ```
6. Try out the command using:
    ```bash
   pre-commit try-repo ../pre-commit-hooks scanoss-check-undeclared-code --verbose
    ```
   This will attempt to run `scanoss-check-undeclared-code` against the `pre-commit-hooks` repo.

    **Note:** This checker requires files to be `staged` in order to be considered for processing
   
    You can achieve this using:
    ```bash
   git add <file>
    ```

7. When you're done with development, you can uninstall using:
    ```bash
    make dev_uninstall
    ```

8. Contributing

   Please following the [contributing](#contributing) instructions to share updates with the community.

## License
This project is licensed under MIT. License file can be found [here](LICENSE).

## Bugs/Features
To request features or alert about bugs, please do so [here](https://github.com/scanoss/pre-commit-hooks/issues).

## Contributing
We welcome contributions to this project! Please clone the repository and submit a pull request with your changes. Ensure that your code passes all pre-commit checks before submitting.

## Release and Deployment

This project uses automated GitHub Actions workflows to manage releases. The package is distributed through GitHub Releases and the pre-commit framework (not PyPI).

### Release Process

1. **Update Version**: Modify `__version__` in `src/hooks/__init__.py` following semantic versioning (MAJOR.MINOR.PATCH)

2. **Create Tag**: Run the `tag-version.yml` workflow manually:
   - Go to Actions → "Tag Version" → "Run workflow"
   - The workflow compares the Python package version with the latest Git tag
   - If versions differ, it creates and pushes a new tag (e.g., `v0.3.0`)

3. **Automated Release**: The `release.yml` workflow triggers automatically when a tag is pushed:
   - Builds the package in a clean environment
   - Runs verification tests (binary check, `--help`, basic execution)
   - Creates a draft GitHub Release

4. **Publish Release**: A maintainer reviews and publishes the draft release manually

### Version Management

- **Current Version Source**: `src/hooks/__init__.py`
- **Versioning Strategy**: Semantic Versioning (SemVer)
- **Tag Format**: `v0.3.0` (with 'v' prefix)
- **Major Version Tags**: The repository maintains `v0` and `v1` tags that point to the latest patch release, allowing users to pin to a major version and automatically receive updates

### Distribution

Users reference this package in their `.pre-commit-config.yaml`:

```yaml
repos:
-   repo: https://github.com/scanoss/pre-commit-hooks
    rev: v0  # Pin to major version, or use v0.3.0 for specific version
    hooks:
    -   id: scanoss-check-undeclared-code
```

The pre-commit framework installs directly from the Git repository—no PyPI publishing required.

### Key Workflows

- `.github/workflows/tag-version.yml` - Manual workflow for version tagging
- `.github/workflows/release.yml` - Automated draft release creation
- `.github/workflows/test.yml` - Continuous testing on main branch and PRs
- `.github/workflows/update-main-version.yml` - Major version tag maintenance

## Changelog
Details of major changes to the library can be found in [CHANGELOG.md](CHANGELOG.md).
