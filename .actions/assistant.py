import os
from typing import Dict, List, Optional, Union

import fire
import yaml

_PATH_ROOT = os.path.dirname(os.path.dirname(__file__))


class AssistantCLI:

    _BASH_SCRIPT = ("#!/bin/bash", "set -e")
    _FIELD_TARGET_REPO = "target_repository"
    _FIELD_REQ = "dependencies"
    _FIELD_TESTS = "testing"

    @staticmethod
    def _https(
        https: str, token: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None
    ) -> str:
        login = token if token else ""
        if not login and username:
            login = f"{username}:{password}" if password else username
        url = https.replace("https://", "")
        if login:
            login = f"{login}@"
        return f"https://{login}{url}"

    @staticmethod
    def _extras(extras: Union[str, list, tuple] = "") -> str:
        extras = " ".join(extras) if isinstance(extras, (tuple, list, set)) else extras
        return extras

    @staticmethod
    def _install_pip(repo: Dict[str, str]) -> str:
        assert "HTTPS" in repo, f"Missing key `HTTPS` among {repo.keys()}"
        # pip install -q 'https://github.com/...#egg=lightning-flash[tabular]
        repo_name, _ = os.path.splitext(os.path.basename(repo.get("HTTPS")))
        name = repo.get("name", repo_name)
        url = AssistantCLI._https(
            repo.get("HTTPS"), token=repo.get("token"), username=repo.get("username"), password=repo.get("password")
        )

        cmd = f"pip install --quiet git+{url}"
        if "checkout" in repo:
            assert isinstance(repo["checkout"], str)
            cmd += f"@{repo['checkout']}"
        if "install_extras" in repo:
            cmd += f"#egg={name}[{AssistantCLI._extras(repo['install_extras'])}]"
        return cmd

    @staticmethod
    def _install_repo(repo: Dict[str, str], remove_dir: bool = True) -> List[str]:
        assert "HTTPS" in repo, f"Missing key `HTTPS` among {repo.keys()}"
        url = AssistantCLI._https(
            repo.get("HTTPS"), token=repo.get("token"), username=repo.get("username"), password=repo.get("password")
        )
        cmd_git = f"git clone {url}"
        repo_name, _ = os.path.splitext(os.path.basename(repo.get("HTTPS")))
        cmds = [cmd_git, f"cd {repo_name}"]
        if "checkout" in repo:
            assert isinstance(repo["checkout"], str)
            cmds.append(f"git checkout {repo['checkout']}")
        pip_install = "."
        if "install_extras" in repo:
            pip_install += f"[{AssistantCLI._extras(repo['install_extras'])}]"
        cmds.append(f"pip install --quiet {pip_install}")
        if "install_file" in repo:
            assert isinstance(repo["install_file"], str)
            cmds.append(f"pip install --quiet -r {repo['install_file']}")
        cmds.append("cd ..")
        if remove_dir:
            cmds.append(f"rm -rf {repo_name}")
        return cmds

    @staticmethod
    def prepare_env(config_file: str = "config.yaml", path_root: str = _PATH_ROOT):
        assert os.path.isfile(config_file)
        script = list(AssistantCLI._BASH_SCRIPT)
        with open(config_file) as fp:
            config = yaml.safe_load(fp)
        repo = config[AssistantCLI._FIELD_TARGET_REPO]
        script += AssistantCLI._install_repo(repo, remove_dir=False)
        repo_name, _ = os.path.splitext(os.path.basename(repo.get("HTTPS")))

        if "copy_tests" in repo:
            if isinstance(repo["copy_tests"], str):
                repo["copy_tests"] = [repo["copy_tests"]]
            for test in repo["copy_tests"]:
                path_test = os.path.join(path_root, repo_name, test)
                test_dir = os.path.dirname(test)
                if test_dir:
                    script.append(f"mkdir -p {test_dir}")
                is_file = os.path.splitext(test)[-1] != ""
                script.append(f"cp {'-r' if not is_file else ''} {path_test} {test}")
        script.append(f"rm -rf {repo_name}")

        reqs = config.get("dependencies", [])
        for req in reqs:
            script.append(AssistantCLI._install_pip(req))

        return os.linesep.join(script)

    @staticmethod
    def specify_tests(config_file: str = "config.yaml"):
        assert os.path.isfile(config_file)
        with open(config_file) as fp:
            config = yaml.safe_load(fp)
        testing = config[AssistantCLI._FIELD_TESTS]

        dirs = " ".join(testing.get("dirs", []))
        args = " ".join(testing.get("pytest_args", []))
        return f"{dirs} {args}"


if __name__ == "__main__":
    fire.Fire(AssistantCLI)
