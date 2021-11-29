import os
from typing import Dict, List, Optional, Union

import fire
import yaml

_PATH_ROOT = os.path.dirname(os.path.dirname(__file__))


class AssistantCLI:

    _BASH_SCRIPT = ("set -e",)
    _FIELD_TARGET_REPO = "target_repository"
    _FIELD_REQ = "dependencies"
    _FIELD_TESTS = "testing"
    _FOLDER_TESTS = "_integrations"

    @staticmethod
    def folder_local_tests() -> str:
        return AssistantCLI._FOLDER_TESTS

    @staticmethod
    def folder_repo(config_file: str = "config.yaml") -> str:
        """Parse the project repository name."""
        assert os.path.isfile(config_file), f"Missing config file: {config_file}"
        with open(config_file) as fp:
            config = yaml.safe_load(fp)
        repo = config[AssistantCLI._FIELD_TARGET_REPO]
        repo_name, _ = os.path.splitext(os.path.basename(repo.get("HTTPS")))
        return repo_name

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
        """Create command for instaling a project from source (if HTTPS is given) or from PyPI (if at least name is
        given)."""
        assert any(k in repo for k in ["HTTPS", "name"]), f"Missing key `HTTPS` or `name` among {repo.keys()}"
        # pip install -q 'https://github.com/...#egg=lightning-flash[tabular]
        name = repo.get("name")
        if not name:
            # ig no name is given parse it from repo path as last element
            name, _ = os.path.splitext(os.path.basename(repo.get("HTTPS")))
        if "HTTPS" in repo:
            # creat installation from Git repository
            url = AssistantCLI._https(
                repo.get("HTTPS"), token=repo.get("token"), username=repo.get("username"), password=repo.get("password")
            )

            cmd = f"git+{url}"
            if "checkout" in repo:
                assert isinstance(repo["checkout"], str)
                cmd += f"@{repo['checkout']}"
            if "install_extras" in repo:
                cmd += f"#egg={name}[{AssistantCLI._extras(repo['install_extras'])}]"
        else:
            # make installation from pypi package
            cmd = name
            if "install_extras" in repo:
                cmd += f"[{repo['install_extras']}]"
            if "checkout" in repo:
                cmd += f"=={repo['checkout']}"
        return "pip install --quiet " + cmd

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
        pip_install = "."
        if "install_extras" in repo:
            pip_install += f"[{AssistantCLI._extras(repo['install_extras'])}]"
        cmds.append(f"pip install --quiet {pip_install}")
        if "install_file" in repo:
            assert isinstance(repo["install_file"], str)
            cmds.append(f"pip install --quiet --upgrade -r {repo['install_file']}")
        cmds.append("cd ..")
        if remove_dir:
            cmds.append(f"rm -rf {repo_name}")
        return cmds

    @staticmethod
    def list_env(config_file: str = "config.yaml") -> str:
        """Parse environment variables and pass then in format to be accepted before calling testing command."""
        assert os.path.isfile(config_file), f"Missing config file: {config_file}"
        with open(config_file) as fp:
            config = yaml.safe_load(fp)
        env = config.get("env", {})
        env = [f'{name}="{val}"' for name, val in env.items()]
        return " ".join(env)

    @staticmethod
    def before_commands(
        config_file: str = "config.yaml", stage: str = "install", as_append: bool = False
    ) -> Union[str, List[str]]:
        """Parse commands for eventual custom execution before install or before testing."""
        assert os.path.isfile(config_file), f"Missing config file: {config_file}"
        with open(config_file) as fp:
            config = yaml.safe_load(fp)
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
        assert os.path.isfile(config_file), f"Missing config file: {config_file}"
        script = list(AssistantCLI._BASH_SCRIPT)
        with open(config_file) as fp:
            config = yaml.safe_load(fp)
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
        if dirs:
            dirs = [os.path.join(AssistantCLI._FOLDER_TESTS, d) for d in dirs]
            dirs = " ".join(dirs) if isinstance(dirs, (tuple, list, set)) else dirs
        else:
            dirs = AssistantCLI._FOLDER_TESTS
        return dirs

    @staticmethod
    def _pytest_args(args: Union[None, str, list, tuple] = "") -> str:
        args = args or ""
        args = " ".join(args) if isinstance(args, (tuple, list, set)) else args
        return args

    @staticmethod
    def specify_tests(config_file: str = "config.yaml"):
        assert os.path.isfile(config_file), f"Missing config file: {config_file}"
        with open(config_file) as fp:
            config = yaml.safe_load(fp)
        testing = config.get(AssistantCLI._FIELD_TESTS, {})

        dirs = AssistantCLI._pytest_dirs(testing.get("dirs"))
        args = AssistantCLI._pytest_args(testing.get("pytest_args"))
        return f"{dirs} {args}"


if __name__ == "__main__":
    fire.Fire(AssistantCLI)
