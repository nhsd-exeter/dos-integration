test-secret:
	make test-secret-setup
	tests=( \
		test-secret-get-random-string \
		test-secret-create \
		test-secret-fetch \
		test-secret-fetch-and-export-variables \
		test-secret-get-existing-value-from-object \
		test-secret-get-existing-value-from-single \
		test-secret-update-existing-value \
		test-secret-copy-value-from \
	)
	for test in $${tests[*]}; do
		mk_test_initialise $$test
		make $$test
	done
	make test-secret-teardown

test-secret-setup:
	make localstack-start
	# Prerequisites
	make docker-pull NAME=tools VERSION=$(DOCKER_LIBRARY_TOOLS_VERSION)

test-secret-teardown:
	make localstack-stop

# ==============================================================================

test-secret-get-random-string:
	# act
	secret=$$(make secret-get-random-string LENGTH=128)
	# assert
	mk_test "128 -eq $$(expr length $$secret)"

test-secret-create:
	# arrange
	export DB_HOST=localhost
	export DB_PORT=5432
	# act
	make secret-create NAME=$(@) VARS=DB_HOST,DB_PORT
	# assert
	secret=$$(make secret-fetch NAME=$(@))
	mk_test "{\"DB_HOST\":\"localhost\",\"DB_PORT\":\"5432\"} = $$secret"

test-secret-fetch:
	# arrange
	export DB_USERNAME=admin
	export DB_PASSWORD=secret
	make secret-create NAME=$(@) VARS=DB_USERNAME,DB_PASSWORD
	# act
	secret=$$(make secret-fetch NAME=$(@))
	# assert
	mk_test "{\"DB_USERNAME\":\"admin\",\"DB_PASSWORD\":\"secret\"} = $$secret"

test-secret-fetch-and-export-variables:
	# arrange
	export DB_HOST=localhost
	export DB_PORT=5432
	export DB_NAME=test
	export DB_USERNAME=admin
	export DB_PASSWORD=secret
	make secret-create NAME=$(@) VARS=DB_HOST,DB_PORT,DB_NAME,DB_USERNAME,DB_PASSWORD
	# act
	secret=$$(make secret-fetch-and-export-variables NAME=$(@))
	# assert
	mk_test "environment" "5 -eq $$(echo "$$secret" | grep DB_ | wc -l)"
	mk_test "terraform" "5 -eq $$(echo "$$secret" | grep TF_VAR_db_ | wc -l)"
	mk_test_complete

test-secret-get-existing-value-from-object:
	# arrange
	export DB_HOST=localhost
	export DB_PORT=5432
	export DB_NAME=test
	export DB_USERNAME=admin
	export DB_PASSWORD=secret
	make secret-create NAME=$(@) VARS=DB_HOST,DB_PORT,DB_NAME,DB_USERNAME,DB_PASSWORD
	# act
	value=$$(make secret-get-existing-value NAME=$(@) KEY=DB_NAME)
	# assert
	mk_test "$$value == test"

test-secret-get-existing-value-from-single:
	# arrange
	make aws-secret-create NAME=$(@) VALUE=value
	# act
	value=$$(make secret-get-existing-value NAME=$(@))
	# assert
	mk_test "$$value == value"

test-secret-update-existing-value:
	# arrange
	export DB_HOST=localhost
	export DB_PORT=5432
	export DB_NAME=test
	export DB_USERNAME=admin
	export DB_PASSWORD=secret
	make secret-create NAME=$(@) VARS=DB_HOST,DB_PORT,DB_NAME,DB_USERNAME,DB_PASSWORD
	# act
	make secret-update-existing-value NAME=$(@) KEY=DB_NAME VALUE=other
	# assert
	secret=$$(make secret-fetch-and-export-variables NAME=$(@))
	([[ $$secret == *DB_HOST=*localhost* ]] && [[ $$secret == *DB_NAME=*other* ]] && [[ $$secret == *DB_PASSWORD=*secret* ]]) && mk_test true || mk_test false

test-secret-copy-value-from:
	# arrange
	make aws-secret-create NAME=$(@)-src VALUE=value
	export DB_HOST=localhost
	export DB_PORT=5432
	export DB_NAME=test
	export DB_USERNAME=admin
	export DB_PASSWORD=secret
	make secret-create NAME=$(@)-dest VARS=DB_HOST,DB_PORT,DB_NAME,DB_USERNAME,DB_PASSWORD
	# act
	make secret-copy-value-from SRC_NAME=$(@)-src DEST_NAME=$(@)-dest KEY=DB_PASSWORD
	# assert
	value=$$(make secret-get-existing-value NAME=$(@)-dest KEY=DB_PASSWORD)
	mk_test "$$value == value"
