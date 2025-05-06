#################################################################################
#
# Makefile to build the project
#
#################################################################################

PROJECT_NAME = de-streaming-data-project
REGION ?= eu-west-2
PYTHON_INTERPRETER = python
WD=$(shell pwd)
PYTHONPATH=${WD}:${WD}/src
SHELL := /bin/bash
PROFILE ?= default
PIP := pip

# Define utility variable to help calling Python from the virtual environment
ACTIVATE_ENV := source ./venv/bin/activate


## Build the environment requirements
requirements: create-environment
	$(call execute_in_env, $(PIP) install -r ./requirements.txt)
layer-dependencies:
	$(PIP) install -r ./layer-requirements.txt -t dependencies/python

