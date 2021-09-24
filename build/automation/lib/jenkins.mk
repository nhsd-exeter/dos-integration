JENKINS_JOB_NAME = $(shell echo "$(JOB_NAME)" | sed "s/[^a-zA-Z0-9]/-/g" | sed 's/--*/-/g')
JENKINS_WORKSPACE_BUCKET_NAME = $(PROJECT_GROUP_SHORT)-$(PROJECT_NAME)-jenkins-workspace
JENKINS_WORKSPACE_BUCKET_URI = $(JENKINS_WORKSPACE_BUCKET_NAME)/$(or $(JENKINS_JOB_NAME), local)/$(BUILD_BRANCH)

# ==============================================================================

jenkins-create-pipeline-from-template: ### Create Jenkins pipeline from template
	if [ ! -f $(PROJECT_DIR)/build/jenkins/Jenkinsfile.development ]; then
		mkdir -p $(PROJECT_DIR)/build/jenkins
		cp -rfv \
			$(LIB_DIR)/jenkins/Jenkinsfile.* \
			$(PROJECT_DIR)/build/jenkins
		make -s file-replace-variables-in-dir DIR=$(PROJECT_DIR)/build/jenkins
	fi

# ==============================================================================

jenkins-upload-workspace: ### Upload the project workspace to a storage - optional: ARCHIVE=true
	# set up
	eval "$$(make aws-assume-role-export-variables)"
	# upload workspace
	make _jenkins-create-workspace-storage
	if [[ "$(ARCHIVE)" =~ ^(true|yes|y|on|1|TRUE|YES|Y|ON)$$ ]]; then
		make _jenkins-upload-workspace-archived
	else
		make _jenkins-upload-workspace-exploded
	fi

_jenkins-create-workspace-storage:
	if [ false == $$(make aws-s3-exists NAME=$(JENKINS_WORKSPACE_BUCKET_NAME)) ]; then
		make aws-s3-create NAME=$(JENKINS_WORKSPACE_BUCKET_NAME)
	fi

_jenkins-upload-workspace-archived:
	id=$$(printf "%04d\n" $(BUILD_ID))
	file=workspace-$(PROJECT_NAME_SHORT)-$(BUILD_TIMESTAMP)-$${id}-$(BUILD_COMMIT_HASH).tar.gz
	tar --exclude-vcs --exclude='$(TMP_DIR_REL)' -zcvf $(TMP_DIR)/$$file .
	make aws-s3-upload \
		FILE=$(TMP_DIR_REL)/$$file \
		URI=$(JENKINS_WORKSPACE_BUCKET_URI)/$$file
	rm -f $(TMP_DIR)/workspace-$(PROJECT_NAME_SHORT)-*
	echo -e "\nJenkins workspace URL is https://s3.console.aws.amazon.com/s3/object/$(JENKINS_WORKSPACE_BUCKET_URI)/$$file\n"

_jenkins-upload-workspace-exploded:
	id=$$(printf "%04d\n" $(BUILD_ID))
	make aws-s3-upload \
		FILE=. \
		URI=$(JENKINS_WORKSPACE_BUCKET_URI)/$(BUILD_TIMESTAMP)-$${id}-$(BUILD_COMMIT_HASH) \
		ARGS=" \
			--recursive \
			--exclude '.git/*' \
		"
	echo -e "\nJenkins workspace URL is https://s3.console.aws.amazon.com/s3/buckets/$(JENKINS_WORKSPACE_BUCKET_URI)/$${date}-$${id}-$(BUILD_COMMIT_HASH)/\n"
