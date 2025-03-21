# SCANOSS Pre-commit Hooks


## Table of Contents
- [Available Hooks](#available-hooks)
- [Installation](#installation)
- [Local Development](#local-development)
- [License](#license)
- [Bugs/Features](#bugsfeatures)
- [Contributing](#contributing)
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

## Changelog
Details of major changes to the library can be found in [CHANGELOG.md](CHANGELOG.md).
