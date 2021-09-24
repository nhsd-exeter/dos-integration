test-project:
	make test-project-setup
	tests=( \
		test-project-config-dev-env \
		test-project-document-infrastructure \
	)
	for test in $${tests[*]}; do
		mk_test_initialise $$test
		make $$test
	done
	make test-project-teardown

test-project-setup:
	:

test-project-teardown:
	:

test-project-config-dev-env:
	# arrange
	rm -f $(_PROJECT_CONFIG_DEV_ENV_TIMESTAMP_FILE)
	# act
	export BUILD_ID=0
	export _PROJECT_CONFIG_DEV_ENV_TARGET=_test-project-config-dev-env
	export _PROJECT_CONFIG_DEV_ENV_TIMESTAMP=$(BUILD_TIMESTAMP)
	export _PROJECT_CONFIG_DEV_ENV_FORCE=yes
	output=$$(make project-config | grep "running _test-project-config-dev-env" | wc -l)
	# assert
	mk_test "target" "0 -lt $$output"
	mk_test "timestamp file" "-f $(_PROJECT_CONFIG_DEV_ENV_TIMESTAMP_FILE)"
	mk_test_complete

test-project-document-infrastructure:
	# act
	make project-document-infrastructure \
		FIN=$(LIB_DIR_REL)/project/template/infrastructure/diagram.py \
		FOUT=$(TMP_DIR_REL)/diagram
	# assert
	mk_test "-f $(TMP_DIR_REL)/diagram.png"
	# clean up
	rm -f $(TMP_DIR_REL)/diagram.png

# ==============================================================================

_test-project-config-dev-env:
	echo "running _test-project-config-dev-env"
