.PHONY: test clean env

env:
	pip install -q -r requirements.txt
	python .actions/assistant.py prepare_env --config_file=.actions/config.yaml > prepare_env.sh
	bash prepare_env.sh

test: clean env
	test_args=$(python .actions/assistant.py specify_tests --config_file=.actions/config.yaml 2>&1)
	coverage run -m pytest ${test_args} -v

clean:
	# clean all temp runs
	rm -rf .mypy_cache
	rm -rf .pytest_cache
