import glob
import json
import os
import traceback
from typing import Dict, List, Optional, Union

import fire
import requests
import yaml

_PATH_ROOT = os.path.dirname(os.path.dirname(__file__))
_REQUEST_TIMEOUT = 10


def request_url(url: str, auth_token: Optional[str] = None) -> Optional[dict]:
    """General request with checking if request limit was reached."""
    auth_header = {"Authorization": f"token {auth_token}"} if auth_token else {}
    try:
        req = requests.get(url, headers=auth_header, timeout=_REQUEST_TIMEOUT)
    except requests.exceptions.Timeout:
        traceback.print_exc()
        return None
    if req.status_code == 403:
        return None
    return json.loads(req.content.decode(req.encoding))


class AssistantCLI:

    _BASH_SCRIPT = ("set -e",)
    _FIELD_TARGET_REPO = "target_repository"
    _FIELD_REQUIRE = "dependencies"
    _FIELD_TESTS = "testing"
    _MANDATORY_FIELDS = (_FIELD_TARGET_REPO, _FIELD_REQUIRE)
    _FOLDER_TESTS = "_integrations"
    _PATH_CONFIGS = os.path.join(_PATH_ROOT, "configs")

    @staticmethod
    def folder_local_tests() -> str:
        return AssistantCLI._FOLDER_TESTS

    @staticmethod
    def changed_configs(pr: int, auth_token: Optional[str] = None, as_list: bool = True) -> Union[str, List[str]]:
        """Determine what configs were changed in particular PR."""
        url = f"https://api.github.com/repos/Lightning-AI/ecosystem-ci/pulls/{pr}/files"
        data = request_url(url, auth_token)
        if not data:
            return [] if as_list else ""
        files = [d["filename"] for d in data if os.path.isfile(d["filename"])]
        configs = [f.replace("configs/", "") for f in files if f.startswith("configs/")]
        return configs if as_list else "|".join(configs)

    @staticmethod
    def find_all_configs(configs_folder: str = _PATH_CONFIGS) -> List[str]:
        """Find all configs YAML|YML in given folder recursively."""
        files = glob.glob(os.path.join(configs_folder, "**", "*.yaml"), recursive=True)
        files += glob.glob(os.path.join(configs_folder, "**", "*.yml"), recursive=True)
        files = [cfg.replace("configs/", "") if cfg.startswith("configs/") else cfg for cfg in files]
        return files

    @staticmethod
    def list_runtimes(pr: Optional[int] = None, auth_token: Optional[str] = None) -> str:
        """Extract all runtime combinations in the whole repository or just for particular PR."""
        if isinstance(pr, int):
            configs = AssistantCLI.changed_configs(pr, auth_token)
        else:
            configs = AssistantCLI.find_all_configs()
        runtimes = []
        for cfg in configs:
            cfg_runtimes = AssistantCLI._load_config(cfg).get("runtimes", {})
            if not cfg_runtimes:  # filter empty runtimes
                continue
            runtimes += [dict(config=cfg, **c) for c in cfg_runtimes]
        return json.dumps(runtimes)

    @staticmethod
    def _load_config(config_file: str = "config.yaml", strict: bool = True) -> dict:
        if not os.path.isfile(config_file):
            config_file = os.path.join("configs", config_file)
        assert os.path.isfile(config_file), f"Missing config file: {config_file}"
        with open(config_file) as fp:
            config = yaml.safe_load(fp)
        if strict:
            miss = [fd for fd in AssistantCLI._MANDATORY_FIELDS if fd not in config]
            if miss:
                raise AttributeError(f"Config '{config_file}' has missing following fields: {miss}")
        return config

    @staticmethod
    def folder_repo(config_file: str = "config.yaml") -> str:
        """Parse the project repository name."""
        config = AssistantCLI._load_config(config_file)
        repo = config[AssistantCLI._FIELD_TARGET_REPO]
        repo_name, _ = os.path.splitext(os.path.basename(repo.get("HTTPS")))
        return repo_name

    @staticmethod
    def contacts(config_file: str = "config.yaml", channel: str = "slack") -> str:
        """Parse the project repository name."""
        config = AssistantCLI._load_config(config_file)
        contacts = config.get("contact", {}).get(channel)
        if not contacts:
            return ""
        if not isinstance(contacts, list):
            contacts = [contacts]
        if channel == "slack":
            # see: https://stackoverflow.com/a/58688117/4521646
            contacts = [f"<@{name}>" for name in contacts]
        return ", ".join(contacts)

    @staticmethod
    def _https(
        https: str, token: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None
    ) -> str:
        """Format the complete HTTPS path in case token or user authentication is required."""
        login = token if token else ""
        if not login and username:
            login = f"{username}:{password}" if password else username
        url = https.replace("https://", "")
        if login:
            login = f"{login}@"
        return f"https://{login}{url}"

    @staticmethod
    def _extras(extras: Union[str, list, tuple] = "") -> str:
        """Create a list of eventual extras fro pip installation."""
        extras = ",".join(extras) if isinstance(extras, (tuple, list, set)) else extras
        return extras

    @staticmethod
    def _install_pip(repo: Dict[str, str]) -> str:
        """Create command for installing a project from source (if HTTPS is given) or from PyPI (if at least name is
        given).

        Args:
            repo: it is package or repository with additional key fields
        """
        assert any(k in repo for k in ["HTTPS", "name"]), f"Missing key `HTTPS` or `name` among {repo.keys()}"
        # pip install -q 'https://github.com/...#egg=lightning-flash[tabular]
        name = repo.get("name")
        if not name:
            # ig no name is given parse it from repo path as last element
            name, _ = os.path.splitext(os.path.basename(repo.get("HTTPS")))
        if "HTTPS" in repo:
            # creat installation from Git repository
            url = AssistantCLI._https(
                repo.get("HTTPS"),
                token=repo.get("token"),
                username=repo.get("username"),
                password=repo.get("password"),
            )

            pkg = f"git+{url}"
            if "checkout" in repo:
                assert isinstance(repo["checkout"], str)
                pkg += f"@{repo['checkout']}"
            if "install_extras" in repo:
                pkg += f"#egg={name}[{AssistantCLI._extras(repo['install_extras'])}]"
        else:
            # make installation from pypi package
            pkg = name
            if "install_extras" in repo:
                pkg += f"[{repo['install_extras']}]"
            if "checkout" in repo:
                pkg += f"=={repo['checkout']}"
        flags = " ".join(["--quiet"] + repo.get('install_flags', []))
        cmd = " ".join(["pip install", pkg, flags])
        return cmd

    @staticmethod
    def _install_repo(repo: Dict[str, str], remove_dir: bool = True) -> List[str]:
        """Create command for installing a project from source assuming it is Git project."""
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

        if "requirements_file" in repo:
            reqs = repo["requirements_file"]
            reqs = [reqs] if isinstance(reqs, str) else reqs
            cmds.append(f"pip install --quiet --upgrade {' '.join([f'-r {req}' for req in reqs])}")

        pip_install = "."
        if "install_extras" in repo:
            pip_install += f"[{AssistantCLI._extras(repo['install_extras'])}]"
        cmds.append(f"pip install --quiet {pip_install}")
        cmds.append("cd ..")
        if remove_dir:
            cmds.append(f"rm -rf {repo_name}")
        return cmds

    @staticmethod
    def list_env(config_file: str = "config.yaml", export: bool = False) -> str:
        """Parse environment variables and pass then in format to be accepted before calling testing command."""
        config = AssistantCLI._load_config(config_file)
        env = config.get("env", {})
        env = [f'{name}="{val}"' for name, val in env.items()]
        if export:
            env = [f"export {e}" for e in env]
        sep = " ; " if export else " "
        return sep.join(env)

    @staticmethod
    def dict_env(config_file: str = "config.yaml") -> str:
        """Parse environment variables and pass then as dictionary/string for testing command."""
        config = AssistantCLI._load_config(config_file)
        env = config.get("env", {})
        return json.dumps(env)

    @staticmethod
    def before_commands(
        config_file: str = "config.yaml", stage: str = "install", as_append: bool = False
    ) -> Union[str, List[str]]:
        """Parse commands for eventual custom execution before install or before testing."""
        config = AssistantCLI._load_config(config_file)
        cmds = config.get(f"before_{stage}", [])
        if not as_append:
            cmds = os.linesep.join(list(AssistantCLI._BASH_SCRIPT) + cmds)
        return cmds

    @staticmethod
    def _export_env(env: Dict[str, str]) -> List[str]:
        """Create exporting for environment variables from config."""
        return [f'export {name}="{val}"' for name, val in env.items()]

    @staticmethod
    def prepare_env(config_file: str = "config.yaml", path_root: str = _PATH_ROOT) -> str:
        """Prepare the CI environment from given project config.

        the workflow includes:
        1. exporting environment variables
        2. execute custom before install commands
        3. install project repository
        4. copy integrations tests
        5. install additional/specific dependencies
        6. execute custom before test commands
        """
        config = AssistantCLI._load_config(config_file)
        script = list(AssistantCLI._BASH_SCRIPT)
        repo = config[AssistantCLI._FIELD_TARGET_REPO]

        script += AssistantCLI._export_env(config.get("env", {}))
        script += AssistantCLI.before_commands(config_file, stage="install", as_append=True)

        script += AssistantCLI._install_repo(repo, remove_dir=False)
        repo_name, _ = os.path.splitext(os.path.basename(repo.get("HTTPS")))

        if "copy_tests" in repo:
            if isinstance(repo["copy_tests"], str):
                repo["copy_tests"] = [repo["copy_tests"]]
            created_dirs = []
            script.append(f'mkdir "{AssistantCLI._FOLDER_TESTS}"')
            for test in repo["copy_tests"]:
                test = test.replace("/", os.path.sep)
                repo_test = os.path.join(path_root, repo_name, test)
                test_dir = os.path.dirname(test)
                if test_dir and test_dir not in created_dirs:
                    script.append(f'mkdir -p "{os.path.join(AssistantCLI._FOLDER_TESTS, test_dir)}"')
                    created_dirs.append(test_dir)
                is_file = os.path.splitext(test)[-1] != ""
                copy_flag = "-r" if not is_file else ""
                script.append(f'cp {copy_flag} "{repo_test}" "{os.path.join(AssistantCLI._FOLDER_TESTS, test)}"')
        script.append(f'rm -rf "{repo_name}"')

        reqs = config.get("dependencies", [])
        for req in reqs:
            script.append(AssistantCLI._install_pip(req))

        script += AssistantCLI.before_commands(config_file, stage="test", as_append=True)
        return os.linesep.join(script)

    @staticmethod
    def _pytest_dirs(dirs: Union[None, str, list, tuple] = "") -> str:
        dirs = "." if not dirs else dirs
        dirs = " ".join(dirs) if isinstance(dirs, (tuple, list, set)) else dirs
        return dirs

    @staticmethod
    def _pytest_args(args: Union[None, str, list, tuple] = "") -> str:
        args = args or ""
        args = " ".join(args) if isinstance(args, (tuple, list, set)) else args
        return args

    @staticmethod
    def specify_tests(config_file: str = "config.yaml") -> str:
        config = AssistantCLI._load_config(config_file)
        testing = config.get(AssistantCLI._FIELD_TESTS, {})

        dirs = AssistantCLI._pytest_dirs(testing.get("dirs"))
        args = AssistantCLI._pytest_args(testing.get("pytest_args"))
        return f"{dirs} {args}"


if __name__ == "__main__":
    fire.Fire(AssistantCLI)
