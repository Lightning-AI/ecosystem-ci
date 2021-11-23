# Lightning EcoSystem CI

**Automated Testing for Lightning EcoSystem Projects**

[![CI testing](https://github.com/PyTorchLightning/ecosystem-ci/workflows/CI%20testing/badge.svg?branch=main&event=push)](https://github.com/PyTorchLightning/ecosystem-ci/actions?query=workflow%3A%22CI+testing%22)
[![Build Status](https://dev.azure.com/PytorchLightning/ecosystem-ci/_apis/build/status/PyTorchLightning.ecosystem-ci?branchName=main)](https://dev.azure.com/PytorchLightning/ecosystem-ci/_build/latest?definitionId=17&branchName=main)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/PyTorchLightning/ecosystem-ci/main.svg?badge_token=mqheL1-cTn-280Vx4cJUdg)](https://results.pre-commit.ci/latest/github/PyTorchLightning/ecosystem-ci/main?badge_token=mqheL1-cTn-280Vx4cJUdg)

______________________________________________________________________

<div align="center">
Lightning EcoSystem CI allows you to discover issues in your own projects against Lightning nightly and the latest release.
<br / >
You get CPUs, Multi-GPUs testing for free, and Slack notification alerts if issues arise!
</div>

## How do I add my own Project?

### Pre-requisites

Here are pre-requisites for your project before adding to the Lightning EcoSystem CI:

- Your project already include some **python tests with PyTorch Lightning** as a dependency
- You'll be a **contact/responsible** person to resolve any issues that the CI finds in the future for your project

### Adding your own project config

1. First, fork this project (with [CLI](https://cli.github.com/) or in browser) to be able to create a new Pull Request, and work within a specific branch.

```bash
gh repo fork PyTorchLightning/ecosystem-ci
cd ecosystem-ci/
```

2. Copy the [template file](configs/_template.yaml) in `configs` folder and call it `<my_project_name>.yaml`.

```
cp configs/template.yaml configs/<my_project_name>.yaml
```

3. At the minimum, modify the `HTTPS` variable to point to your repository. See [Configuring my project](<>) for more options

```yaml
target_repository:
  HTTPS: https://github.com/MyUsername/MyProject.git
...
```

If your project tests multiple configurations or you'd like to test against multiple Lightning versions such as master and release branches, create a config file for each one of them.

As an example, have a look at [metrics master](configs/PyTorchLightning/metrics_pl-master.yaml) and [metrics release](configs/PyTorchLightning/metrics_pl-release.yaml) CI files.

4. Add your config filename to the either/both the [GitHub CPU CI file](.github/workflows/ci_testing.yml) or the [Azure GPU CI file](.azure/ci-testig-parameterized.yml).

For example, for the [GitHub CPU CI file](.github/workflows/ci_testing.yml) we append our config into the pytest parametrization:

```yaml
...
jobs:
  pytest:
    ...
        config:
          - "PyTorchLightning/metrics_pl-release.yaml"
          - "PyTorchLightning/transformers_pl-release.yaml"
          - "MyUsername/myproject-release.yaml"
        include:
          - {os: "ubuntu-20.04", python-version: "3.8", config: "PyTorchLightning/metrics_pl-master.yaml"}
          - {os: "ubuntu-20.04", python-version: "3.9", config: "PyTorchLightning/transformers_pl-master.yaml"}
          - {os: "ubuntu-20.04", python-version: "3.9", config: "MyUsername/my_project-master.yaml"}
        exclude:
          - {os: "windows-2019", config: "PyTorchLightning/transformers_pl-release.yaml"}
...
```

For example, in the [Azure GPU CI file](.azure/ci-testig-parameterized.yml) file:

```yaml
...
jobs:
- template: testing-template.yml
  parameters:
    configs:
    - "PyTorchLightning/metrics_pl-master.yaml"
    - "PyTorchLightning/metrics_pl-release.yaml"
    - "MyUsername/my_project-master.yaml"
```

5. Add the responsible person(s) to [CODEOWNERS](.github/CODEOWNERS) for your organization folder or just the project.

```
# MyProject
/configs/Myusername/MyProject*    @Myusername
```

6. Finally create a draft PR to the repo!

(Optional). \[wip\] join our Slack channel to be notified if your project is breaking

## Configuring my project

The config include a few different sections:

- `target_repository` include your project
- `env` (optional) environment variable in case soe compilations expects them
- `dependencies` listing all dependencies which are taken outside pip
- `testing` defines specific pytest arguments and what folders shall be tested

All dependencies as well as the target repository is sharing the same template with the only required field `HTTPS` and all others are optional:

```yaml
target_repository:
  HTTPS: https://github.com/PyTorchLightning/metrics.git
  # OPTIONAL, for a private/protected repository
  username: my-nick
  # OPTIONAL, paired with the username
  password: dont-tell-anyone
  # OPTIONAL, overrides the user/pass
  token: authentication-token
  # OPTIONAL, checkout a particular branch or a tag
  checkout: master
  # define installing package extras
  install_extras: all

copy_tests:
    - integrations
    # this is copied as we use the helpers inside integrations as regular python package
    - tests/__init__.py
    - tests/helpers
```

Note: If you define some files as done above, and they are using internal-cross imports, you need to copy the `__init__.py` files from each particular package level.

The `testing` section provides access to the pytest run args and command.

```yaml
testing:
  # by default pytest is called on all copied items/tests
  dirs:
    - integrations
  # OPTIONAL, additional pytest arguments
  pytest_args: --strict
```
