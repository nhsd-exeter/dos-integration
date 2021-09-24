test-node:
	make test-node-setup
	tests=( \
		test-node-virtualenv \
	)
	for test in $${tests[*]}; do
		mk_test_initialise $$test
		make $$test
	done
	make test-node-teardown

test-node-setup:
	:

test-node-teardown:
	:

test-node-virtualenv:
	mk_test_skip
