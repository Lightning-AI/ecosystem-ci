.PHONY: all clean env

env:
	pip install -q -r requirements.txt

# CONFIGS := $(shell find -regex "configs/*/*.y[a]?ml")
CONFIGS := $(shell find configs/ -name "*.yaml")
BUILDS := $(CONFIGS:%.yaml=%)

all: clean env ${BUILDS}
	@echo $<

%: %.y*ml
	@echo $<
	python .actions/assistant.py prepare_env --config_file=$< > prepare_env.sh
	bash prepare_env.sh
	coverage run -m pytest $(python .actions/assistant.py specify_tests --config_file=$< 2>&1) -v

clean:
	# clean all temp runs
	rm -rf .mypy_cache
	rm -rf .pytest_cache
