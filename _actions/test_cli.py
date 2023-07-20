import os

import pytest

from _actions.assistant import AssistantCLI

_PATH_DIR = os.path.dirname(__file__)
_PATH_CONFIG = os.path.join(_PATH_DIR, "_config.yaml")


@pytest.mark.parametrize(
    "cmd",
    [
        "folder_repo",
        "find_all_configs",
        "list_runtimes",
        "contacts",
        "list_env",
        "dict_env",
        "before_commands",
        "prepare_env",
        "specify_tests",
    ],
)
def test_assistant_commands(cmd: str) -> None:
    AssistantCLI().__getattribute__(cmd)(_PATH_CONFIG)
