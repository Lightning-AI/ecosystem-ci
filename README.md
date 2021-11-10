# Lightning Compatibility

__This is starter project template which shall set some regular testing between Lightning head and external package...__

[![CI testing](https://github.com/PyTorchLightning/compatibility/workflows/CI%20testing/badge.svg?branch=main&event=push)](https://github.com/PyTorchLightning/compatibility/actions?query=workflow%3A%22CI+testing%22)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/PyTorchLightning/compatibility/main.svg?badge_token=mqheL1-cTn-280Vx4cJUdg)](https://results.pre-commit.ci/latest/github/PyTorchLightning/compatibility/main?badge_token=mqheL1-cTn-280Vx4cJUdg)

Any user who wants to keep her/his project well aligned with PL, should user this project.
We recommend forking this repository or create your own from this template with setting this one as upstream to be able to receive any future integration fixes and improvements.

To simplify and unify the workflow se expect that a user fills only the `configs/<Organization>/<project>.yaml` file.
The actual integration is with GitHub pipelines abut with generated environment scripts it can be easily extended to any other CI such as Azure if you require testing on GPUs or other specific machines.

## Included

Listing the implemented sections:

- preparing the target repo environment with specified dependencies
- extracting tests from target repository
- setting [CI](https://github.com/PyTorchLightning/compatibility/actions?query=workflow%3A%22CI+testing%22) and scheduling

This template showcase integration between [Pytorch-Lightning](https://github.com/PyTorchLightning/pytorch-lightning) and [TorchMetrics](https://github.com/PyTorchLightning/metrics)

```yaml
target_repository:
  HTTPS: https://github.com/PyTorchLightning/metrics.git
  # OPTIONAL, checkout a particular branch or a tag
  checkout: master
  # OPTIONAL, define installing package extras
  install_extras: all
  # OPTIONAL, copy some  test from the target repository
  copy_tests:
    - integrations
    - tests/__init__.py
    - tests/helpers

dependencies:
  - name: pytorch-lightning
    HTTPS: https://github.com/PyTorchLightning/pytorch-lightning.git
    checkout: release/1.5.x
    install_extras: all
```

Eventually you can parametrize multiple configs inside your CI, for example if you eed testing against multiple heads...

## To be Done

You still need to enable some external integrations such as:

- notification on CI failure to a Slack channel
- notification on CI failure to via email
- update Makefile to run any and all integrations
