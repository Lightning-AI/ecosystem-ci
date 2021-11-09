import os
from typing import Dict, List, Optional, Tuple

import fire
import yaml

PATH_ROOT = os.path.dirname(os.path.dirname(__file__))


class AssistantCLI:

    BASH_SCRIPT = ("#!/bin/bash", "set -e")
    FIELD_TARGET_REPO = "target_repository"
    FIELD_REQ = "dependencies"
    FIELD_TESTS = "testing"

    @staticmethod
    def _git_clone(
        https: str, token: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None
    ) -> Tuple[str, str]:
        login = token if token else ""
        if not login and username:
            login = f"{username}:{password}" if password else username
        url = https.replace("https://", "")
        if login:
            login = f"{login}@"
        cmd = f"git clone https://{login}{url}"
        name, _ = os.path.splitext(os.path.basename(url))
        return cmd, name

    @staticmethod
    def _install_repo(repo: Dict[str, str], remove_dir: bool = True) -> List[str]:
        assert "HTTPS" in repo, f"Missing key `HTTPS` among {repo.keys()}"
        cmd_git, repo_name = AssistantCLI._git_clone(
            repo.get("HTTPS"), token=repo.get("token"), username=repo.get("username"), password=repo.get("password")
        )
        # todo: checkout during clone
        cmds = [cmd_git, f"cd {repo_name}"]
        if "checkout" in repo:
            assert isinstance(repo["checkout"], str)
            cmds.append(f"git checkout {repo['checkout']}")
        pip_install = "."
        if "install_extras" in repo:
            assert isinstance(repo["install_extras"], str)  # todo: allow also list of strings
            pip_install += f"[{repo['install_extras']}]"
        cmds.append(f"pip install --quiet {pip_install}")
        if "install_file" in repo:
            assert isinstance(repo["install_file"], str)
            cmds.append(f"pip install --quiet -r {repo['install_file']}")
        cmds.append("cd ..")
        if remove_dir:
            cmds.append(f"rm -rf {repo_name}")
        return cmds

    @staticmethod
    def prepare_env(config_file: str = "config.yaml", path_root: str = PATH_ROOT):
        assert os.path.isfile(config_file)
        script = list(AssistantCLI.BASH_SCRIPT)
        with open(config_file) as fp:
            config = yaml.safe_load(fp)
        repo = config[AssistantCLI.FIELD_TARGET_REPO]
        script += AssistantCLI._install_repo(repo, remove_dir=False)
        _, repo_name = AssistantCLI._git_clone(
            repo.get("HTTPS"), token=repo.get("token"), username=repo.get("username"), password=repo.get("password")
        )

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
            script += AssistantCLI._install_repo(req)

        return os.linesep.join(script)

    @staticmethod
    def copy_tests(config_file: str):
        assert os.path.isfile(config_file)

        # TODO


if __name__ == "__main__":
    fire.Fire(AssistantCLI)
