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
	python ${CLI} prepare_env --config_file=$< > prepare_env.sh
	bash prepare_env.sh
	coverage run -m pytest $(python $CLI specify_tests --config_file=$< 2>&1) -v
	rm -rf $(python $CLI folder_local_tests 2>&1)
	rm -rf $(python $CLI folder_repo --config_file=$< 2>&1)

clean:
	# clean all temp runs
	rm -rf .mypy_cache
	rm -rf .pytest_cache
