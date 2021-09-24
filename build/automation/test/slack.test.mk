test-slack:
	make test-slack-setup
	tests=( \
		test-slack-send-standard-notification \
		test-slack-send-notification \
		test-slack-render-template \
	)
	for test in $${tests[*]}; do
		mk_test_initialise $$test
		make $$test
	done
	make test-slack-teardown

test-slack-setup:
	:

test-slack-teardown:
	:

test-slack-send-standard-notification:
	mk_test_skip

test-slack-send-notification:
	mk_test_skip

test-slack-render-template:
	mk_test_skip
