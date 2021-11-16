# Lightning Compatibility

__This is the integration/compatibility testing platform between PytorchLightning (PL) and other project on regular bases with failure notifications...__

[![CI testing](https://github.com/PyTorchLightning/compatibility/workflows/CI%20testing/badge.svg?branch=main&event=push)](https://github.com/PyTorchLightning/compatibility/actions?query=workflow%3A%22CI+testing%22)
[![Build Status](https://dev.azure.com/PytorchLightning/compatibility/_apis/build/status/PyTorchLightning.compatibility?branchName=main)](https://dev.azure.com/PytorchLightning/compatibility/_build/latest?definitionId=17&branchName=main)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/PyTorchLightning/compatibility/main.svg?badge_token=mqheL1-cTn-280Vx4cJUdg)](https://results.pre-commit.ci/latest/github/PyTorchLightning/compatibility/main?badge_token=mqheL1-cTn-280Vx4cJUdg)

Any user who wants to keep her/his project well aligned with PL, should user this platform and set integrations.
One of the main goals to prevent breaking compatibility and discovering all eventual issue on a regular basis not when release is created and published (as it is irreversible  with PIP registry).
Using this platform you get out of the box nightly testing on CPU as well as multi-GPU.
An alternative is forking this repository and run all compatibilities in your own environments and resources.

To simplify and unify the workflow we expect that:

- your project already include some **python tests with PL** as dependency
- filling the **configuration file** `configs/<Organization>/<project>.yaml` (we will talk about it later)
- setting a **contact/responsible** person to resolve eventual issues

The actual integration uses GitHub actions and Azure pipelines.
We also provide native parallelization so all projects are tested in parallel and using cache to speed-up environment creation if it is the same over consecutive runs for a particular project and configuration.
This platform is build around two simple steps:

1. prepare target environment with installing or dependencies
1. copy integration tests and run them

which are wrapped in generated script, so they can be easily extended and used in any other CI such as CircleCI if you require testing on other specific machines.

## How to add new project?

We are open to include your project on PytorchLightning family and provide integration/compatibility testing to ensure that we won't accidentally break anything that your project relies on...

For adding your project you need to do these simple steps

0. Fork this project to be able to create a new Pull Request, and work within a specific branch
1. Create new configuration file in `configs/<Organization>` folder and call it `<project>.yaml`
1. Add path to this new config to at least one CI
   - with GitHub action you can specify target OS and Python version
   - with Azure you only add path to the config; OS, Python version are fixed
1. Add responsible person to the `.github/CODEOWNERS` for your organization folder or just single project
1. Create a (draft) PR with all early mentioned requirements
1. \[wip\] join our Slack channel to be notified if your project is breaking

If your project shall be run with multiple configurations or test against multiple PL versions such as master and release branch, you would need to and a config ile for each of them.

## How to configure my project?

Tha config include a few ain sections:

- `target_repository` include your project
- `env` (optional) environment variable in case soe compilations expects them
- `dependencies` listing all dependencies which are taken outside pip
- `testing` defines specific pytest arguments and what folders shall be tested

All dependencies as well as the target repository is sharing the same template with the only required field `HTTPS` and all others are optional:

```yaml
  HTTPS: https://github.com/PyTorchLightning/metrics.git
  # OPTIONAL, for some protected repository
  username: my-nick
  # OPTIONAL, paired with the username
  password: dont-tell-anyone
  # OPTIONAL, overrides the user/pass
  token: authentication-token
  # OPTIONAL, checkout a particular branch or a tag
  checkout: master
  # define installing package extras
  install_extras: all
```

In case user is pulling private or protected repository he can use login with username/password or authentication token (the token is prioritized over user/pass).
The `checkout` allowing user to select a head/branch or tag which shall be installed, in particular the most common option is testing against development (master branch) and stable (release branch) states.
The `install_extras` refers to standard pip option to install some additional dependencies defined with setuptools, typically used as `<my-package>[<install_extras>]`.

The`target_repository` is an extended version of dependency as described above.
In addition, this item has to include `copy_tests` with list of folders and/or files with tests.
Note that if you define just some files, and they are using internal-cross imports you need to copy also `__init__.py` from each particular package level.

```yaml
  copy_tests:
    - integrations
    # this is copied as we use the helpers inside integrations as regular python package
    - tests/__init__.py
    - tests/helpers
```

The `testing` section aims only on enrichment the pytest command

```yaml
testing:
  # by default pytest is called on all copied items/tests
  dirs:
    - integrations
  # OPTIONAL, additional pytest arguments
  pytest_args: --strict
```

This starter showcase integration between [Pytorch-Lightning](https://github.com/PyTorchLightning/pytorch-lightning) and [TorchMetrics](https://github.com/PyTorchLightning/metrics)

## To be Done

This is still early stage we not all is ideal yet, and actually we are working on:

- enable some external messaging on CI failure to via email
- update Makefile to run any and all integrations
