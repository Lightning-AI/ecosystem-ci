.PHONY: test clean env

env:
	pip install -q -r requirements.txt

# test: clean env
# 	python .actions/assistant.py prepare_env --config_file=.actions/_config.yaml > prepare_env.sh
# 	bash prepare_env.sh
# 	coverage run -m pytest $(python .actions/assistant.py specify_tests --config_file=.actions/_config.yaml 2>&1) -v

clean:
	# clean all temp runs
	rm -rf .mypy_cache
	rm -rf .pytest_cache
