
#vars
VERSION=$(shell ./version.py)

# HELP
# This will output the help for each task
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help

help: ## This help
	@awk 'BEGIN {FS = ":.*?## "} /^[0-9a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help

clean:  ## Clean all dev data
	@echo "Removing dev and distribution data..."
	@rm -rf dist/* build/* venv/bin/scanoss-check-undeclared-code src/scanoss_pre_commit_hooks.egg-info

dev_setup:  ## Setup Python dev env for the current user
	@echo "Setting up dev env for the current user..."
	pip3 install -e .

dev_uninstall:  ## Uninstall Python dev setup for the current user
	@echo "Uninstalling dev env..."
	pip3 uninstall -y scanoss_pre_commit_hooks
	@rm -rf dist/* build/* venv/bin/scanoss-check-undeclared-code src/scanoss_pre_commit_hooks.egg-info
