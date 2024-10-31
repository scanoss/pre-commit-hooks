# SCANOSS Pre-commit Hooks


## Table of Contents

- [Installation](#installation)
- [Available Hooks](#available-hooks)
- [Developing Locally](#developing-locally)
- [Contributing](#contributing)
- [License](#license)

## Installation

To get started with this project, you'll need to install the pre-commit package manager and configure it to use the hooks provided in this repository.

### Step 1: Install Pre-commit

You can install pre-commit using various methods:

- **Using pip**:

  ```bash
  pip install pre-commit
  ```

  Add `pre-commit` to your `requirements.txt` or `requirements-dev.txt`:

  ```
  pre-commit
  ```

- **Using Homebrew**:

  ```bash
  brew install pre-commit
  ```


For more installation options, refer to the [pre-commit documentation](https://pre-commit.com/).

### Step 2: Configure Pre-commit Hooks

1. In the root of your project where you want to use these hooks, create a `.pre-commit-config.yaml` file with the following content:


    ```yaml
    repos:
    -   repo: https://github.com/scanoss/pre-commit-hooks
        rev: v0.0.1
        hooks:
        -   id: check-open-source-software
    ```

    Check the latest release [here](https://github.com/scanoss/pre-commit-hooks/releases)

2. Install the pre-commit hooks:

    ```bash
    pre-commit install
    ```

3. (Optional) Run the hooks against all files to ensure everything is in order:

    ```bash
    pre-commit run --all-files
    ```

## Available Hooks

This repository currently includes the following pre-commit hook:

- **check-open-source-software**: This hook checks for potential open source software in the files being committed. It is designed to run at the `pre-commit`, `pre-push`, and `manual` stages.

## Developing Locally

To develop this project locally, follow these steps:

1. Clone the repository:

    ```bash
    git clone https://github.com/scanoss/pre-commit-hooks.git
    cd pre-commit-hooks
    ```

2. Install the necessary dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Set up pre-commit hooks:

    ```bash
    pre-commit install
    ```

## Contributing

We welcome contributions to this project! Please clone the repository and submit a pull request with your changes. Ensure that your code passes all pre-commit checks before submitting.
