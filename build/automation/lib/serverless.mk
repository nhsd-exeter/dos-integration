SERVERLESS_VERSION = 2.62
SERVERLESS_DIR := $(or $(SERVERLESS_DIR), deployment)
SERVERLESS_CONFIG_FILE := $(or $(SERVERLESS_CONFIG_FILE), serverless.yml)

serverless-build:
	cd $(SERVERLESS_DIR)
	tar -czf $(DOCKER_DIR)/serverless/assets/serverless.tar.gz serverless.yml
	cd $(PROJECT_DIR)
	make docker-build NAME=serverless

serverless-deploy: # Deploy AWS resources - mandatory: PROFILE
	make serverless-run CMD=deploy

serverless-deploy-single-function: # Deploy single AWS lambda - mandatory: PROFILE, FUNCTION_NAME
	make serverless-run CMD="deploy function -f $(FUNCTION_NAME)"

serverless-remove: # Delete existing AWS resources - mandatory: PROFILE
	make serverless-run CMD=remove

serverless-info: # See info on deployed environment - mandatory: PROFILE
	make serverless-run CMD=info

serverless-clean: ### Clean serverless directory - optional: SERVERLESS_DIR=[directory where .serverless is, defaults to deployment]
	rm -fv $(DOCKER_DIR)/serverless/assets/*.tar.gz

serverless-run: # Runs serverless commands - mandatory: PROFILE, CMD=[serverless command]; optional: SERVERLESS_DIR=[directory where .serverless is, defaults to deployment],SERVERLESS_CONFIG_FILE=[serverless config file name, defaults to serverless.yml]
	make docker-run-serverless \
	IMAGE=$(DOCKER_REGISTRY)/serverless:latest \
	ARGS="-v $(PROJECT_DIR)/$(SERVERLESS_DIR)/$(SERVERLESS_CONFIG_FILE):/deployment/serverless.yml" \
	CMD="serverless $(CMD) --config $(SERVERLESS_CONFIG_FILE) --stage $(BLUE_GREEN_ENVIRONMENT)"

serverless-install-plugin: ### Install serverless plugin - mandatory: NAME=[plugin name]; optional: SERVERLESS_DIR=[directory where .serverless is, defaults to deployment]
	make docker-run-serverless \
	IMAGE=$(DOCKER_REGISTRY)/serverless \
	CMD="serverless plugin install -n $(NAME)"

docker-run-serverless:
	make docker-config > /dev/null 2>&1
	container=$$([ -n "$(CONTAINER)" ] && echo $(CONTAINER) || echo $$(echo '$(IMAGE)' | md5sum | cut -c1-7)-$(BUILD_COMMIT_HASH)-$(BUILD_ID)-$$(date --date=$$(date -u +"%Y-%m-%dT%H:%M:%S%z") -u +"%Y%m%d%H%M%S" 2> /dev/null)-$$(make secret-random LENGTH=8))
	docker run --interactive $(_TTY) --rm \
		--name $$container \
			--env-file <(make _list-variables PATTERN="^(AWS|TX|TEXAS|NHSD|TERRAFORM|SLACK)") \
			--env-file <(make _list-variables PATTERN="^(DB|DATABASE|SMTP|APP|APPLICATION|UI|API|SERVER|HOST|URL)") \
			--env-file <(make _list-variables PATTERN="^(PROFILE|ENVIRONMENT|BUILD|PROGRAMME|ORG|SERVICE|PROJECT|VERSION)") \
			--env-file <(make _docker-get-variables-from-file VARS_FILE=$(VAR_DIR)/project.mk) \
			--env-file <(make _docker-get-variables-from-file VARS_FILE=$(VAR_DIR)/profile/$(PROFILE).mk) \
			--env-file <(make _docker-get-variables-from-file VARS_FILE=$(VARS_FILE)) \
			-e DOCKER_REGISTRY=$(DOCKER_REGISTRY) \
		--network $(DOCKER_NETWORK) \
		$(ARGS) \
		$(IMAGE) \
			$(CMD)
