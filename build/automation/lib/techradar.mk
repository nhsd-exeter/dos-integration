techradar-inspect: ### Inspect Docker image - mandatory: IMAGE=[image name]
	hash="$$(make techradar-image-get-hash)"
	date="$$(make techradar-image-get-date)"
	size="$$(make techradar-image-get-size)"
	trace=$$(make techradar-image-get-trace | base64 -w 0)
	tech="$$(make techradar-image-detect-tech)"
	echo "{$$tech,\"image\":{\"name\":\"$(IMAGE)\",\"hash\":\"$$hash\",\"date\":\"$$date\",\"size\":$$size,\"trace\":\"$$trace\"},\"build\":{\"buildId\":\"$(BUILD_ID)\",\"buildDate\":\"$(BUILD_DATE)\",\"buildRepo\":\"$(BUILD_REPO)\",\"buildBranch\":\"$(BUILD_BRANCH)\",\"buildCommitHash\":\"$(BUILD_COMMIT_HASH)\",\"buildCommitData\":\"$(BUILD_COMMIT_DATE)\"},\"project\":{\"orgName\":\"$(ORG_NAME)\",\"programme\":\"$(PROGRAMME)\",\"projectGroup\":\"$(PROJECT_GROUP)\",\"projectGroupShort\":\"$(PROJECT_GROUP_SHORT)\",\"projectName\":\"$(PROJECT_NAME)\",\"projectNameShort\":\"$(PROJECT_NAME_SHORT)\",\"projectDisplayName\":\"$(PROJECT_DISPLAY_NAME)\",\"projectId\":\"$(PROJECT_ID)\",\"projectTag\":\"$(PROJECT_TAG)\",\"serviceTag\":\"$(SERVICE_TAG)\"}}"

# ==============================================================================

techradar-image-get-hash: ### Get Docker image hash - mandatory: IMAGE=[image name]
	docker images --no-trunc --quiet $(IMAGE)

techradar-image-get-date: ### Get Docker image date - mandatory: IMAGE=[image name]
	docker inspect --format='{{ .Created }}' $(IMAGE)

techradar-image-get-size: ### Get Docker image size - mandatory: IMAGE=[image name]
	docker image inspect --format='{{ .Size }}' $(IMAGE)

techradar-image-get-trace: ### Get Docker image trace - mandatory: IMAGE=[image name]
	function trace() {
		local parent=$$(docker inspect -f '{{ .Parent }}' $$1) 2>/dev/null
		declare -i level=$$2
		echo $${level}: $$(docker inspect -f '{{ .ContainerConfig.Cmd }}' $$1 2>/dev/null)
		level=level+1
		if [ "$${parent}" != "" ]; then
			echo $${level}: $$parent
			trace $$parent $$level
		fi
	}
	trace $(IMAGE)

techradar-image-detect-tech: ### Detect Docker image technologies - mandatory: IMAGE=[image name]
	make -s ADD=$(LIB_DIR)/techradar CMD="/init.sh" \
		_techradar-image-run \
		_techradar-image-clean

# ==============================================================================

_techradar-image-run: ### Run an image in a custom scrip - mandatory: IMAGE=[image name]; optional: ADD=[file to add],CMD=[command to execute]
	hash=$$(echo '$(BUILD_COMMIT_HASH)$(BUILD_ID)$(IMAGE)$(CMD)' | md5sum | cut -c1-7)
	make HASH=$$hash \
		_techradar-image-entrypoint \
		_techradar-image-dockerfile \
		_techradar-image-build
	docker run --rm $(IMAGE)-wrap-$$hash $(CMD)

_techradar-image-entrypoint:
	file=$(TMP_DIR)/entrypoint.sh.$(HASH)
	echo '#!/bin/sh' > $$file
	echo '$$*' >> $$file
	chmod +x $$file

_techradar-image-dockerfile:
	[ -n "$(ADD)" ] && rm -rf $(TMP_DIR)/$(HASH)-$$(basename $(ADD)) && cp -r $(ADD) $(TMP_DIR)/$(HASH)-$$(basename $(ADD))
	file=$(TMP_DIR)/Dockerfile.$(HASH)
	echo "FROM $(IMAGE)" > $$file
	[ -n "$(ADD)" ] && echo "ADD $(HASH)-$$(basename $(ADD)) /" >> $$file
	echo "COPY entrypoint.sh.$(HASH) /entrypoint.sh" >> $$file
	echo 'ENTRYPOINT [ "/entrypoint.sh" ]' >> $$file

_techradar-image-build:
	cd $(TMP_DIR)
	docker build --rm \
		--file $(TMP_DIR)/Dockerfile.$(HASH) \
		--tag $(IMAGE)-wrap-$(HASH) \
		. > /dev/null 2>&1

_techradar-image-clean:
	docker rmi --force $$(docker images | grep -- "-wrap-" | awk '{ print $$3 }') > /dev/null 2>&1

# ==============================================================================

.SILENT: \
	techradar-image-detect-tech \
	techradar-image-get-date \
	techradar-image-get-hash \
	techradar-image-get-size \
	techradar-image-get-trace \
	techradar-inspect
