test-postgres:
	make test-postgres-setup
	tests=( \
	)
	for test in $${tests[*]}; do
		mk_test_initialise $$test
		make $$test
	done
	make test-postgres-teardown

test-postgres-setup:
	:

test-postgres-teardown:
	:
