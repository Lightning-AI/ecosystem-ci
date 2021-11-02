# Lightning Compatibility

This is starter project template which shall set some regular testing between Lightning head and external package...

[![CI testing](https://github.com/PyTorchLightning/compatibility/workflows/CI%20testing/badge.svg?branch=main&event=push)](https://github.com/PyTorchLightning/compatibility/actions?query=workflow%3A%22CI+testing%22)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/PyTorchLightning/compatibility/main.svg?badge_token=mqheL1-cTn-280Vx4cJUdg)](https://results.pre-commit.ci/latest/github/PyTorchLightning/compatibility/main?badge_token=mqheL1-cTn-280Vx4cJUdg)


## Included

Listing the implemented sections:

- setting [CI](https://github.com/PyTorchLightning/compatibility/actions?query=workflow%3A%22CI+testing%22) for package and _tests_ folder

## To be Done

You still need to enable some external integrations such as:

- update path used in the badges to the repository

## Tests / Docs notes

- We are using [Napoleon style](https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html) and we shall use static types...
- It is nice to se [doctest](https://docs.python.org/3/library/doctest.html) as they are also generated as examples in documentation
- For wider and edge cases testing use [pytest parametrization](https://docs.pytest.org/en/stable/parametrize.html) :\]
