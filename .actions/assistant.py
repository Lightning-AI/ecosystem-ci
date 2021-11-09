import os

import fire


class AssistantCLI:

    @staticmethod
    def script_env(config_file: str):
        assert os.path.isfile(config_file)

        # TODO

    @staticmethod
    def copy_tests(config_file: str):
        assert os.path.isfile(config_file)

        # TODO


if __name__ == "__main__":
    fire.Fire(AssistantCLI)
