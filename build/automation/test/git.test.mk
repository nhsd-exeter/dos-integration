TEST_GIT_COMMIT_MESSAGE_FILE = $(TMP_DIR_REL)/test-git-commit-message-file.txt

test-git:
	make test-git-setup
	tests=( \
		test-git-config \
		test-git-check-if-branch-name-is-correct \
		test-git-check-if-commit-msg-is-correct \
		test-git-check-if-pull-request-title-is-correct \
		test-git-secrets-load \
		test-git-secrets-add-banned \
		test-git-secrets-add-allowed \
		test-git-secrets-scan-repo-history \
		test-git-secrets-scan-repo-files \
		test-git-check-if-commit-changed-directory \
		test-git-commit-get-hash \
		test-git-commit-get-timestamp \
		test-git-commit-get-message \
		test-git-tag-is-environment-deployment \
		test-git-tag-create-environment-deployment \
		test-git-tag-get-environment-deployment \
		test-git-tag-list \
		test-git-tag-clear \
	)
	for test in $${tests[*]}; do
		mk_test_initialise $$test
		make $$test
	done
	make test-git-teardown

test-git-setup:
	:

test-git-teardown:
	:

# ==============================================================================

test-git-config:
	# act
	make git-config
	# assert
	mk_test "branch.autosetupmerge" "false = $$(git config branch.autosetupmerge)"
	mk_test "branch.autosetuprebase" "always = $$(git config branch.autosetuprebase)"
	mk_test "commit.gpgsign" "true = $$(git config commit.gpgsign)"
	mk_test "core.autocrlf" "input = $$(git config core.autocrlf)"
	mk_test "core.filemode" "true = $$(git config core.filemode)"
	mk_test "core.hidedotfiles" "false = $$(git config core.hidedotfiles)"
	mk_test "core.hooksPath" "$(GITHOOKS_DIR_REL) = $$(git config core.hooksPath)"
	mk_test "core.ignorecase" "false = $$(git config core.ignorecase)"
	mk_test "pull.rebase" "true = $$(git config pull.rebase)"
	mk_test "push.default" "current = $$(git config push.default)"
	mk_test "push.followTags" "true = $$(git config push.followTags)"
	mk_test "rebase.autoStash" "true = $$(git config rebase.autoStash)"
	mk_test "remote.origin.prune" "true = $$(git config remote.origin.prune)"
	mk_test ".git/hooks/commit-msg" "-x $(PROJECT_DIR)/.git/hooks/commit-msg"
	mk_test ".git/hooks/pre-commit" "-x $(PROJECT_DIR)/.git/hooks/pre-commit"
	mk_test ".git/hooks/prepare-commit-msg" "-x $(PROJECT_DIR)/.git/hooks/prepare-commit-msg"
	mk_test "secrets.providers git secrets --aws-provider" "0 -lt $$(git-secrets --list | grep 'secrets.providers git secrets --aws-provider' | wc -l)"
	mk_test_complete

test-git-check-if-branch-name-is-correct:
	# assert
	mk_test "01" "$$(make git-check-if-branch-name-is-correct BUILD_BRANCH=main) = true"
	mk_test "02" "$$(make git-check-if-branch-name-is-correct BUILD_BRANCH=task/ABC-123_Descriptive_branch_name) = true"
	mk_test "03" "$$(make git-check-if-branch-name-is-correct BUILD_BRANCH=task/Update_automation_scripts) = true"
	mk_test "04" "$$(make git-check-if-branch-name-is-correct BUILD_BRANCH=task/Update_dependencies) = true"
	mk_test "05" "$$(make git-check-if-branch-name-is-correct BUILD_BRANCH=task/Update_documentation) = true"
	mk_test "06" "$$(make git-check-if-branch-name-is-correct BUILD_BRANCH=task/Update_tests) = true"
	mk_test "07" "$$(make git-check-if-branch-name-is-correct BUILD_BRANCH=task/Update_versions) = true"
	mk_test "08" "$$(make git-check-if-branch-name-is-correct BUILD_BRANCH=task/Refactor) = true"
	mk_test "09" "$$(make git-check-if-branch-name-is-correct BUILD_BRANCH=devops/This_is_a_special_branch_for_the_automation_scripts_changes) = true"
	mk_test "10" "$$(make git-check-if-branch-name-is-correct BUILD_BRANCH=spike/ABC-123_Descriptive_branch_name) = true"
	mk_test "11" "$$(make git-check-if-branch-name-is-correct BUILD_BRANCH=automation/ABC-123_Descriptive_branch_name) = true"
	mk_test "12" "$$(make git-check-if-branch-name-is-correct BUILD_BRANCH=test/ABC-123_Descriptive_branch_name) = true"
	mk_test "13" "$$(make git-check-if-branch-name-is-correct BUILD_BRANCH=bugfix/ABC-123_Descriptive_branch_name) = true"
	mk_test "14" "$$(make git-check-if-branch-name-is-correct BUILD_BRANCH=hotfix/ABC-123_Descriptive_branch_name) = true"
	mk_test "15" "$$(make git-check-if-branch-name-is-correct BUILD_BRANCH=fix/ABC-123_Descriptive_branch_name) = true"
	mk_test "16" "$$(make git-check-if-branch-name-is-correct BUILD_BRANCH=release/ABC-123_Descriptive_branch_name) = true"
	mk_test "17" "$$(make git-check-if-branch-name-is-correct BUILD_BRANCH=migration/ABC-123_Descriptive_branch_name) = true"
	mk_test "18" "$$(make git-check-if-branch-name-is-correct BUILD_BRANCH=unknown/ABC-123_Descriptive_branch_name) = false"
	mk_test "19" "$$(make git-check-if-branch-name-is-correct BUILD_BRANCH=task/ABC-123_Too_long_branch_name_too_long_branch_name_too_long_branch_name) = false"
	mk_test "20" "$$(make git-check-if-branch-name-is-correct BUILD_BRANCH=task/ABC-123_Too_short) = false"
	mk_test "21" "$$(make git-check-if-branch-name-is-correct BUILD_BRANCH=task/ABC-123_descriptive_branch_name) = false"
	mk_test "22" "$$(make git-check-if-branch-name-is-correct BUILD_BRANCH=task/abc-123_Descriptive_branch_name) = false"
	mk_test_complete

test-git-check-if-commit-msg-is-correct:
	# arrange
	echo -e "ABC-123 This commit message is ok\n\nHere is more information" > $(TEST_GIT_COMMIT_MESSAGE_FILE)
	# assert
	mk_test "01" "$$(make git-check-if-commit-msg-is-correct BUILD_BRANCH=main BUILD_COMMIT_MESSAGE="ABC-123 This is a test") = true"
	mk_test "02" "$$(make git-check-if-commit-msg-is-correct BUILD_BRANCH=main BUILD_COMMIT_MESSAGE="Update automation scripts") = true"
	mk_test "03" "$$(make git-check-if-commit-msg-is-correct BUILD_BRANCH=main BUILD_COMMIT_MESSAGE="Update automation scripts to 20210609082320-b083a16") = true"
	mk_test "04" "$$(make git-check-if-commit-msg-is-correct BUILD_BRANCH=main BUILD_COMMIT_MESSAGE="Update dependencies") = true"
	mk_test "05" "$$(make git-check-if-commit-msg-is-correct BUILD_BRANCH=main BUILD_COMMIT_MESSAGE="Update dependencies!") = false"
	mk_test "06" "$$(make git-check-if-commit-msg-is-correct BUILD_BRANCH=main BUILD_COMMIT_MESSAGE="Update dependencies this time?") = false"
	mk_test "07" "$$(make git-check-if-commit-msg-is-correct BUILD_BRANCH=main BUILD_COMMIT_MESSAGE="Update versions") = true"
	mk_test "08" "$$(make git-check-if-commit-msg-is-correct BUILD_BRANCH=main BUILD_COMMIT_MESSAGE="Update documentation") = true"
	mk_test "09" "$$(make git-check-if-commit-msg-is-correct BUILD_BRANCH=main BUILD_COMMIT_MESSAGE="Update this thing") = true"
	mk_test "10" "$$(make git-check-if-commit-msg-is-correct BUILD_BRANCH=main BUILD_COMMIT_MESSAGE="Refactor this thing") = true"
	mk_test "11" "$$(make git-check-if-commit-msg-is-correct BUILD_BRANCH=main BUILD_COMMIT_MESSAGE="Automate this thing") = true"
	mk_test "12" "$$(make git-check-if-commit-msg-is-correct BUILD_BRANCH=main BUILD_COMMIT_MESSAGE="Test this thing") = true"
	mk_test "13" "$$(make git-check-if-commit-msg-is-correct BUILD_BRANCH=main BUILD_COMMIT_MESSAGE="Fix this thing") = true"
	mk_test "14" "$$(make git-check-if-commit-msg-is-correct BUILD_BRANCH=main BUILD_COMMIT_MESSAGE="Release to live") = true"
	mk_test "15" "$$(make git-check-if-commit-msg-is-correct BUILD_BRANCH=main BUILD_COMMIT_MESSAGE="Migrate this to alternative") = true"
	mk_test "16" "$$(make git-check-if-commit-msg-is-correct BUILD_BRANCH=main BUILD_COMMIT_MESSAGE="Put not conventional commit message") = false"
	mk_test "17" "$$(make git-check-if-commit-msg-is-correct BUILD_BRANCH=main BUILD_COMMIT_MESSAGE="start with a lowercase letter") = false"
	mk_test "18" "$$(make git-check-if-commit-msg-is-correct BUILD_BRANCH=task/ABC-123_Descriptive_branch_name BUILD_COMMIT_MESSAGE="ABC-123 Too short") = false"
	mk_test "19" "$$(make git-check-if-commit-msg-is-correct BUILD_BRANCH=task/ABC-123_Descriptive_branch_name BUILD_COMMIT_MESSAGE="abc-123 Not so ok commit message") = false"
	mk_test "20" "$$(make git-check-if-commit-msg-is-correct BUILD_BRANCH=task/ABC-123_Descriptive_branch_name BUILD_COMMIT_MESSAGE="ABC-123 another not so ok commit message") = false"
	mk_test "21" "$$(make git-check-if-commit-msg-is-correct BUILD_BRANCH=task/ABC-123_Descriptive_branch_name BUILD_COMMIT_MESSAGE="ABC-123 This commit message is ok") = true"
	mk_test "22" "$$(make git-check-if-commit-msg-is-correct BUILD_BRANCH=task/ABC-123_Descriptive_branch_name BUILD_COMMIT_MESSAGE="Another commit message that is ok") = true"
	mk_test "23" "$$(make git-check-if-commit-msg-is-correct BUILD_BRANCH=task/ABC-123_Descriptive_branch_name BUILD_COMMIT_MESSAGE="Commit message cannot end with punctuation mark.") = false"
	mk_test "24" "$$(make git-check-if-commit-msg-is-correct BUILD_BRANCH=task/ABC-123_Descriptive_branch_name BUILD_COMMIT_MESSAGE="Trigger CI stages [ci:skip,build-app,deploy-app,run-smoke-test]") = true"
	mk_test "25" "$$(make git-check-if-commit-msg-is-correct BUILD_BRANCH=task/ABC-123_Descriptive_branch_name BUILD_COMMIT_MESSAGE="$$(cat $(TEST_GIT_COMMIT_MESSAGE_FILE))") = true"
	mk_test "26" "$$(make git-check-if-commit-msg-is-correct BUILD_BRANCH=task/Refactor BUILD_COMMIT_MESSAGE="Suitable length message, indeed") = true"
	mk_test "27" "$$(make git-check-if-commit-msg-is-correct BUILD_BRANCH=task/Refactor BUILD_COMMIT_MESSAGE="Too long message, too long message, too long message, too long message, too long message") = false"
	mk_test_complete
	# clean up
	rm -f $(TEST_GIT_COMMIT_MESSAGE_FILE)

test-git-check-if-pull-request-title-is-correct:
	# assert
	mk_test "01" "$$(make git-check-if-pull-request-title-is-correct BUILD_BRANCH=main PULL_REQUEST_TITLE="ABC-123 This is a passing test") = true"
	mk_test "02" "$$(make git-check-if-pull-request-title-is-correct BUILD_BRANCH=main PULL_REQUEST_TITLE="ABC-123 This is a failing tast due to the summary being too long being too long being too long being too long being too long") = false"

test-git-secrets-load:
	mk_test_skip

test-git-secrets-add-banned:
	mk_test_skip

test-git-secrets-add-allowed:
	mk_test_skip

test-git-secrets-scan-repo-history:
	# act
	make git-secrets-scan-repo-history ||:
	# assert
	mk_test "0 -eq $$?"

test-git-secrets-scan-repo-files:
	# act
	make git-secrets-scan-repo-files
	# assert
	mk_test "0 -eq $$?"

test-git-check-if-commit-changed-directory:
	# act
	output=$$(make git-check-if-commit-changed-directory DIR=build/automation/tmp)
	# assert
	mk_test "false == $$output"

test-git-commit-get-hash:
	mk_test_skip

test-git-commit-get-timestamp:
	mk_test_skip

test-git-commit-get-message:
	mk_test_skip

test-git-tag-is-environment-deployment:
	mk_test_skip

test-git-tag-create-environment-deployment:
	mk_test_skip

test-git-tag-get-environment-deployment:
	mk_test_skip

test-git-tag-list:
	mk_test_skip

test-git-tag-clear:
	mk_test_skip
