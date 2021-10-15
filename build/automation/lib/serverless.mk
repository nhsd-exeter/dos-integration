SERVERLESS_VERSION = 2.62
SERVERLESS_DIR := $(or $(SERVERLESS_DIR), deployment)
SERVERLESS_CONFIG_FILE := $(or $(SERVERLESS_CONFIG_FILE), serverless.yml)

serverless-deploy: # Deploy AWS resources - mandatory: PROFILE=[]
	make serverless-run CMD=deploy

serverless-remove: # Delete existing AWS resources - mandatory: PROFILE=[]
	make serverless-run CMD=remove

serverless-info: # See info on deployed environment - mandatory: PROFILE=[]
	make serverless-run CMD=info

serverless-run: # Runs serverless commands - mandatory: PROFILE=[], CMD=[serverless command]; optional: SERVERLESS_DIR=[directory where .serverless is, defaults to deployment],SERVERLESS_CONFIG_FILE=[serverless config file name, defaults to serverless.yml]
	make docker-run-serverless \
	IMAGE=$(DOCKER_REGISTRY)/serverless \
	DIR=$(SERVERLESS_DIR) \
	CMD="serverless $(CMD) --config $(SERVERLESS_CONFIG_FILE) --stage $(ENVIRONMENT)"

serverless-install-plugin: ### Install serverless plugin - mandatory: NAME=[plugin name]; optional: SERVERLESS_DIR=[directory where .serverless is, defaults to deployment]
	make docker-run-serverless \
	IMAGE=$(DOCKER_REGISTRY)/serverless \
	DIR=$(SERVERLESS_DIR) \
	CMD="serverless plugin install -n $(NAME)"

serverless-clean: ### Clean serverless directory - optional: SERVERLESS_DIR=[directory where .serverless is, defaults to deployment]
	rm -rf $(SERVERLESS_DIR)/.serverless

docker-run-serverless:
	make docker-config > /dev/null 2>&1
		container=$$([ -n "$(CONTAINER)" ] && echo $(CONTAINER) || echo $$(echo '$(IMAGE)' | md5sum | cut -c1-7)-$(BUILD_COMMIT_HASH)-$(BUILD_ID)-$$(date --date=$$(date -u +"%Y-%m-%dT%H:%M:%S%z") -u +"%Y%m%d%H%M%S" 2> /dev/null)-$$(make secret-random LENGTH=8))
		docker run --interactive $(_TTY) --rm \
			--name $$container \
			--env-file <(make _list-variables PATTERN="^(AWS|TX|TEXAS|NHSD|TERRAFORM)") \
			--env-file <(make _list-variables PATTERN="^(DB|DATABASE|SMTP|APP|APPLICATION|UI|API|SERVER|HOST|URL)") \
			--env-file <(make _list-variables PATTERN="^(PROFILE|ENVIRONMENT|BUILD|PROGRAMME|ORG|SERVICE|PROJECT)") \
			--env-file <(make _docker-get-variables-from-file VARS_FILE=$(VARS_FILE)) \
			--volume $(PROJECT_DIR):/project \
			--network $(DOCKER_NETWORK) \
			--workdir /project/$(shell echo $(abspath $(DIR)) | sed "s;$(PROJECT_DIR);;g") \
			$(ARGS) \
			$(IMAGE) \
				$(CMD)
