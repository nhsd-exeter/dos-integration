INFRASTRUCTURE_DIR = $(abspath $(TEST_DIR)/terraform/infrastructure)
TERRAFORM_REINIT = false
TF_VAR_localstack_host = $(LOCALSTACK_HOST)

test-terraform:
	make test-terraform-setup
	tests=( \
		test-terraform-export-variables \
		test-terraform-export-variables-from-secret \
		test-terraform-export-variables-from-shell-vars \
		test-terraform-export-variables-from-shell-pattern \
		test-terraform-export-variables-from-shell-pattern-and-vars \
		test-terraform-export-variables-from-json \
		test-terraform-fmt \
		test-terraform-validate \
		test-terraform-plan-before-apply \
		test-terraform-apply \
		test-terraform-plan-after-apply \
		test-terraform-output \
		test-terraform-show \
		test-terraform-destroy \
		test-terraform-unlock \
	)
	for test in $${tests[*]}; do
		mk_test_initialise $$test
		make $$test
	done
	make test-terraform-teardown

test-terraform-setup:
	make localstack-start
	find $(TEST_DIR)/terraform -type d -name '.terraform' -print0 | xargs -0 rm -rfv
	find $(TEST_DIR)/terraform -type f -name '*terraform.tfstate*' -print0 | xargs -0 rm -rfv
	# Prerequisites
	make docker-pull NAME=tools VERSION=$(DOCKER_LIBRARY_TOOLS_VERSION)

test-terraform-teardown:
	make localstack-stop
	rm -f \
		$(TEST_TERRAFORM_FORMATTING_INPUT) \
		$(TEST_TERRAFORM_FORMATTING_OUTPUT)

# ==============================================================================

test-terraform-export-variables:
	# arrange
	export AWS_ACCESS_KEY_ID_test=value
	export AWS_SECRET_ACCESS_KEY_test=value
	export AWS_SESSION_TOKEN_test=value
	# act
	export=$$(make terraform-export-variables)
	# assert
	count=$$(echo "$$export" | grep -E "TF_VAR_aws_[a-z_]*='value'" | wc -l)
	mk_test "3 = $$count"

test-terraform-export-variables-from-secret:
	# arrange
	export _TEST_DB_USERNAME=admin
	export _TEST_DB_PASSWORD=secret
	make secret-create NAME=service/deployment-$(@) VARS=_TEST_DB_USERNAME,_TEST_DB_PASSWORD
	secret=$$(make secret-fetch NAME=service/deployment-$(@))
	# act
	export=$$(make terraform-export-variables-from-json JSON="$$secret")
	# assert
	mk_test "true = $$(echo "$$export" | grep -q "export TF_VAR__test_db_username='admin'" && echo $$export | grep -q "export TF_VAR__test_db_password='secret'" && echo true)"

test-terraform-export-variables-from-shell-vars:
	# arrange
	export _TEST_DB_USERNAME=admin
	export _TEST_DB_PASSWORD=secret
	# act
	export=$$(make terraform-export-variables-from-shell VARS=_TEST_DB_USERNAME,_TEST_DB_PASSWORD)
	# assert
	count=$$(echo "$$export" | grep TF_VAR__test_db_ | wc -l)
	mk_test "2 = $$count"

test-terraform-export-variables-from-shell-pattern:
	# arrange
	export _TEST_DB_USERNAME=admin
	export _TEST_DB_PASSWORD=secret
	# act
	export=$$(make terraform-export-variables-from-shell PATTERN="^_TEST_DB_")
	# assert
	count=$$(echo "$$export" | grep TF_VAR__test_db_ | wc -l)
	mk_test "2 = $$count"

test-terraform-export-variables-from-shell-pattern-and-vars:
	# arrange
	export _TEST_DB_USERNAME=admin
	export _TEST_DB_PASSWORD=secret
	export _TEST_UI_USERNAME=user
	export _TEST_UI_PASSWORD=secret
	# act
	export=$$(make terraform-export-variables-from-shell \
		PATTERN="^_TEST_DB_" \
		VARS=_TEST_DB_USERNAME,_TEST_DB_PASSWORD,_TEST_UI_USERNAME,_TEST_UI_PASSWORD \
	)
	# assert
	count=$$(echo "$$export" | grep TF_VAR__test_ | wc -l)
	mk_test "6 = $$count"

test-terraform-export-variables-from-json:
	# arrange
	json='{"DB_USERNAME":"admin","DB_PASSWORD":"secret"}'
	# act
	export=$$(make terraform-export-variables-from-json JSON="$$json")
	# assert
	mk_test "true = $$(echo "$$export" | grep -q "TF_VAR_db_username='admin'" && echo "$$export" | grep -q "export TF_VAR_db_password='secret'" && echo true)"

test-terraform-fmt:
	# arrange
	make TEST_TERRAFORM_FORMATTING_INPUT
	# act
	make terraform-fmt DIR=$$(echo $(TMP_DIR) | sed "s;$(PROJECT_DIR);;g")
	# assert
	make TEST_TERRAFORM_FORMATTING_OUTPUT
	mk_test "$$(md5sum $(TEST_TERRAFORM_FORMATTING_OUTPUT) | awk '{ print $$1 }')" = "$$(md5sum $(TEST_TERRAFORM_FORMATTING_INPUT) | awk '{ print $$1 }')"

test-terraform-validate:
	mk_test_skip

test-terraform-plan-before-apply:
	# act
	output=$$(make terraform-plan STACKS=service)
	# assert
	str="1 to add, 0 to change, 0 to destroy\."
	count=$$(echo "$$output" | grep "$$str" | wc -l)
	mk_test "1 = $$count"

test-terraform-apply:
	# act
	output=$$(make terraform-apply-auto-approve STACKS=service)
	# assert
	str="Apply complete! Resources: 1 added, 0 changed, 0 destroyed\."
	count=$$(echo "$$output" | grep "$$str" | wc -l)
	mk_test "1 = $$count"

test-terraform-plan-after-apply:
	# act
	output=$$(make terraform-plan STACKS=service)
	# assert
	str="No changes\. Infrastructure is up-to-date\."
	count=$$(echo "$$output" | grep "$$str" | wc -l)
	mk_test "1 = $$count"

test-terraform-output:
	mk_test_skip

test-terraform-show:
	mk_test_skip

test-terraform-destroy:
	# act
	output=$$(make terraform-destroy-auto-approve STACKS=service)
	# assert
	str="Destroy complete! Resources: 1 destroyed\."
	count=$$(echo "$$output" | grep "$$str" | wc -l)
	mk_test "1 = $$count"

test-terraform-unlock:
	mk_test_skip

# ==============================================================================

TEST_TERRAFORM_FORMATTING_INPUT = $(TMP_DIR)/terraform-input.tf
TEST_TERRAFORM_FORMATTING_INPUT:
	echo 'resource "aws_s3_bucket" "b" {' > $(TEST_TERRAFORM_FORMATTING_INPUT)
	echo '  bucket = "test-bucket"' >> $(TEST_TERRAFORM_FORMATTING_INPUT)
	echo '      acl= "public-read"' >> $(TEST_TERRAFORM_FORMATTING_INPUT)
	echo '}' >> $(TEST_TERRAFORM_FORMATTING_INPUT)

TEST_TERRAFORM_FORMATTING_OUTPUT = $(TMP_DIR)/terraform-output.tf
TEST_TERRAFORM_FORMATTING_OUTPUT:
	echo 'resource "aws_s3_bucket" "b" {' > $(TEST_TERRAFORM_FORMATTING_OUTPUT)
	echo '  bucket = "test-bucket"' >> $(TEST_TERRAFORM_FORMATTING_OUTPUT)
	echo '  acl    = "public-read"' >> $(TEST_TERRAFORM_FORMATTING_OUTPUT)
	echo '}' >> $(TEST_TERRAFORM_FORMATTING_OUTPUT)
