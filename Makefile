.PHONY: test clean docs

test:
	pip install -r requirements.txt
	pip install -r tests/requirements.txt

	# use this to run tests
	rm -rf _ckpt_*
	rm -rf ./lightning_logs
	python -m coverage run --source pl_sandbox -m pytest pl_sandbox tests -v --flake8
	python -m coverage report

	# specific file
	# python -m coverage run --source pl_sandbox -m pytest --flake8 --durations=0 -v -k

clean:
	# clean all temp runs
	rm -rf $(shell find . -name "mlruns")
	rm -rf .mypy_cache
	rm -rf .pytest_cache
