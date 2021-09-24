test-localstack:
	make test-localstack-setup
	tests=( \
		test-localstack-start-stop \
	)
	for test in $${tests[*]}; do
		mk_test_initialise $$test
		make $$test
	done
	make test-localstack-teardown

test-localstack-setup:
	:

test-localstack-teardown:
	:

# ==============================================================================

test-localstack-start-stop:
	# act & assert
	make localstack-start && \
		mk_test "start" "true" || mk_test "start" "false"
	make localstack-stop && \
		mk_test "stop" "true" || mk_test "stop" "false"
	mk_test_complete
