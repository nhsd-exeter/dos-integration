test-techradar:
	make test-techradar-setup
	tests=( \
		test-techradar-inspect-filesystem \
		test-techradar-inspect-image \
		test-techradar-inspect-build \
	)
	for test in $${tests[*]}; do
		mk_test_initialise $$test
		make $$test
	done
	make test-techradar-teardown

test-techradar-setup:
	make docker-config

test-techradar-teardown:
	:

# ==============================================================================

test-techradar-inspect-filesystem:
	# arrange
	docker pull alpine:$(DOCKER_ALPINE_VERSION)
	# act
	output=$$(make techradar-inspect IMAGE=alpine:$(DOCKER_ALPINE_VERSION))
	name=$$(echo $$output | make -s docker-run-tools CMD="jq -r '.filesystem.name'")
	version=$$(echo $$output | make -s docker-run-tools CMD="jq -r '.filesystem.version'")
	# assert
	mk_test "name" "alpine = $$name"
	mk_test "version" "$(DOCKER_ALPINE_VERSION) = $$version"
	mk_test_complete

test-techradar-inspect-image:
	# arrange
	docker pull alpine:$(DOCKER_ALPINE_VERSION)
	# act
	output=$$(make techradar-inspect IMAGE=alpine:$(DOCKER_ALPINE_VERSION))
	hash=$$(echo $$output | make -s docker-run-tools CMD="jq -r '.image.hash'")
	date=$$(echo $$output | make -s docker-run-tools CMD="jq -r '.image.date'")
	size=$$(echo $$output | make -s docker-run-tools CMD="jq -r '.image.size'")
	trace=$$(echo $$output | make -s docker-run-tools CMD="jq -r '.image.trace'")
	# assert
	mk_test "hash" "-n $$hash"
	mk_test "date" "-n $$date"
	mk_test "size" "0 -lt $$size"
	mk_test "trace" "-n $$trace"
	mk_test_complete

test-techradar-inspect-build:
	# arrange
	docker pull alpine:$(DOCKER_ALPINE_VERSION)
	# act
	output=$$(make techradar-inspect IMAGE=alpine:$(DOCKER_ALPINE_VERSION))
	id=$$(echo $$output | make -s docker-run-tools CMD="jq -r '.build.id'")
	date=$$(echo $$output | make -s docker-run-tools CMD="jq -r '.build.date'")
	hash=$$(echo $$output | make -s docker-run-tools CMD="jq -r '.build.hash'")
	repo=$$(echo $$output | make -s docker-run-tools CMD="jq -r '.build.repo'")
	# assert
	mk_test "id" "-n $$id"
	mk_test "date" "-n $$date"
	mk_test "hash" "-n $$hash"
	mk_test "repo" "-n $$repo"
	mk_test_complete
