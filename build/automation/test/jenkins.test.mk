test-jenkins:
	make test-jenkins-setup
	tests=( \
		test-jenkins-create-pipeline-from-template \
		test-jenkins-upload-workspace-archived \
		test-jenkins-upload-workspace-exploded \
	)
	for test in $${tests[*]}; do
		mk_test_initialise $$test
		make $$test
	done
	make test-jenkins-teardown

test-jenkins-setup:
	make localstack-start
	# Prerequisites
	make docker-pull NAME=tools VERSION=$(DOCKER_LIBRARY_TOOLS_VERSION)

test-jenkins-teardown:
	make localstack-stop
	rm -rf \
		$(TMP_DIR)/localstack \
		$(TMP_DIR)/workspace-*.download

# ==============================================================================

test-jenkins-create-pipeline-from-template:
	mk_test_skip

test-jenkins-upload-workspace-archived:
	mk_test_skip
	# # act
	# make jenkins-upload-workspace ARCHIVE=true
	# # assert
	# make aws-s3-download \
	# 	URI=$(JENKINS_WORKSPACE_BUCKET_URI)/workspace-$(PROJECT_NAME_SHORT)-$(BUILD_TIMESTAMP)-$$(printf "%04d\n" $(BUILD_ID))-$(BUILD_COMMIT_HASH).tar.gz \
	# 	FILE=$(TMP_DIR_REL)/workspace-$(PROJECT_NAME_SHORT)-$(BUILD_TIMESTAMP)-$$(printf "%04d\n" $(BUILD_ID))-$(BUILD_COMMIT_HASH).tar.gz.download
	# mk_test "-f $(TMP_DIR)/workspace-$(PROJECT_NAME_SHORT)-$(BUILD_TIMESTAMP)-$$(printf "%04d\n" $(BUILD_ID))-$(BUILD_COMMIT_HASH).tar.gz.download"

test-jenkins-upload-workspace-exploded:
	mk_test_skip
	# # act
	# make jenkins-upload-workspace
	# # assert
	# id=$$(printf "%04d\n" $(BUILD_ID))
	# make aws-s3-download \
	# 	URI=$(JENKINS_WORKSPACE_BUCKET_URI)/$(BUILD_TIMESTAMP)-$${id}-$(BUILD_COMMIT_HASH)/README.md \
	# 	FILE=$(TMP_DIR_REL)/workspace-README.md.download
	# mk_test "-f $(TMP_DIR)/workspace-README.md.download"
