.PHONY: clean env

# CONFIGS := $(shell find -regex "configs/*/*.y[a]?ml")
CONFIGS := $(shell find configs/ -name "*.yaml")
BUILDS := $(CONFIGS:%.yaml=%)
CLI = ".actions/assistant.py"

env:
	pip install -q -r requirements.txt

all: clean env ${BUILDS}
	@echo $<

%: %.y*ml
	@echo $<
	echo "pip install virtualenv" > run.sh
	echo "python -m virtualenv --system-site-packages venv" >> run.sh
	echo "source venv/bin/activate" >> run.sh
	python ${CLI} prepare_env --config_file=$< >> run.sh
	echo "coverage run -m pytest $(shell python ${CLI} specify_tests --config_file=$<) -v" >> run.sh
	echo "rm -rf $(shell python ${CLI} folder_local_tests)" >> run.sh
	echo "rm -rf $(shell python ${CLI} folder_repo --config_file=$<)" >> run.sh
	echo "deactivate" >> run.sh
	echo "rm -rf venv" >> run.sh
	bash run.sh

clean:
	# clean all temp runs
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf $(shell python ${CLI} folder_local_tests)
	rm -rf venv
