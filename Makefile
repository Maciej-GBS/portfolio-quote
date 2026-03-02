PACKAGE_ROOT := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))/portfolioq

all: test run

run:
	. .venv/bin/activate && streamlit run portfolioq/web/__main__.py

test:
	. .venv/bin/activate && python -m pytest tests/
