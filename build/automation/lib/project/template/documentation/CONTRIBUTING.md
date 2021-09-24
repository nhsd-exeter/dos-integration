# Contributing

## Table of contents

- [Contributing](#contributing)
  - [Table of contents](#table-of-contents)
  - [Development Environment](#development-environment)
    - [Prerequisites](#prerequisites)
    - [Configuration](#configuration)
  - [Version Control](#version-control)
    - [Git configuration](#git-configuration)
    - [Signing your Git commits](#signing-your-git-commits)
    - [Git usage](#git-usage)
    - [Git commit message](#git-commit-message)
    - [Git hooks](#git-hooks)
    - [Git tags](#git-tags)
  - [Pull request (merge request)](#pull-request-merge-request)
  - [Code review](#code-review)
  - [Unit tests](#unit-tests)

## Development Environment

### Prerequisites

The following software packages must be installed on your MacBook before proceeding

- [Xcode Command Line Tools](https://apps.apple.com/gb/app/xcode/id497799835?mt=12)
- [Brew](https://brew.sh/)
- [GNU make](https://formulae.brew.sh/formula/make)

Before proceeding, please make sure that your macOS operating system provisioned with the `curl -L bit.ly/make-devops-macos-setup | bash` command.

### Configuration

From within the root directory of your project, please run the following command

    make macos-setup

The above make target is equivalent to the `curl` command given earlier and it ensures that your MacBook is configured correctly for development and the setup is consistent across the whole team. In a nutshell it will

- Update all the installed software packages
- Install any missing essential, additional and corporate software packages
- Configure shell (zsh), terminal (iTerm2) and IDE (Visual Studio Code) along with its extensions

This gives a head start and enables anyone complying with that configuration to focus on development straight away. After the command runs successfully, please restart your iTerm2 and Visual Studio Code sessions to fully apply the changes.

## Version Control

### Git configuration

The commands below will configure your Git command-line client globally. Please, update your username (<span style="color:red">Your Name</span>) and email address (<span style="color:red">your.name@nhs.net</span>) below.

    git config --global user.name "Your Name" # Use your full name here
    git config --global user.email "your.name@nhs.net" # Use your email address here
    git config branch.autosetupmerge false
    git config branch.autosetuprebase always
    git config commit.gpgsign true
    git config core.autocrlf input
    git config core.filemode true
    git config core.hidedotfiles false
    git config core.ignorecase false
    git config pull.rebase true
    git config push.default current
    git config push.followTags true
    git config rebase.autoStash true
    git config remote.origin.prune true

### Signing your Git commits

Signing Git commits is a good practice and ensures the correct web of trust has been established for the distributed version control management.

Generate a new pair of GPG keys. Please, change the passphrase (<span style="color:red">pleaseChooseYourKeyPassphrase</span>) below and save it in your password manager.

    USER_NAME="Your Name"
    USER_EMAIL="your.name@nhs.net"
    file=$(echo $USER_EMAIL | sed "s/[^[:alpha:]]/-/g")

    cat > $file.gpg-key.script <<EOF
        %echo Generating a GPG key
        Key-Type: default
        Key-Length: 4096
        Subkey-Type: default
        Subkey-Length: 4096
        Name-Real: $USER_NAME
        Name-Email: $USER_EMAIL
        Expire-Date: 0
        Passphrase: pleaseChooseYourKeyPassphrase
        %commit
        %echo done
    EOF
    gpg --batch --generate-key $file.gpg-key.script && rm $file.gpg-key.script
    # or do it manually by running `gpg --full-gen-key`

Make note of the ID and save the keys.

    gpg --list-secret-keys --keyid-format LONG $USER_EMAIL

You should see a similar output to this:

    sec   rsa4096/AAAAAAAAAAAAAAA 2000-01-01 [SC]
          XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    uid                 [ unknown] Your Name <your.name@nhs.net>
    ssb   rsa4096/BBBBBBBBBBBBBBBB 2000-01-01 [E]

Export your keys.

    ID=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    gpg --armor --export $ID > $file.gpg-key.pub
    gpg --armor --export-secret-keys $ID > $file.gpg-key

Import already existing private key.

    gpg --import $file.gpg-key

Remove keys from the GPG agent if no longer needed.

    gpg --delete-secret-keys $ID
    gpg --delete-keys $ID

Configure Git to use the new key.

    git config --global user.signingkey $ID
    git config --global commit.gpgsign true

Upload the public key to your GitHub and GitLab accounts using the links below.

- [GitHub](https://github.com/settings/keys) - Make sure your email address is verified
- [GitLab](https://gitlab.mgmt.texasplatform.uk/profile/gpg_keys)

### Git usage

Principles to follow

- A direct merge to the canonical branch is not allowed and can only be done by creating a pull request (merge request)
- If not stated otherwise the only long-lived branch is master, i.e. canonical branch
- Any new branch should be created from master
- The preferred short-lived branch name format is `task/JIRA-XXX_Descriptive_branch_name`
- The preferred hotfix branch name format is `bugfix/JIRA-XXX_Descriptive_branch_name`
- All commits must be cryptographically signed
- Commits should be made often and pushed to the remote
- Use rebase to get the latest commits from the master while working with a short-lived or a bugfix branch
- Squash commits when appropriate
- Merge commits are not allowed

Working on a new task

    git checkout -b task/JIRA-XXX_Descriptive_branch_name
    # Make your changes here...
    git add .
    git commit -S -m "Meaningful description of change"
    git push --set-upstream origin task/JIRA-XXX_Descriptive_branch_name

Branch naming convention should follow the pattern of `^(task|bugfix)/[A-Z]{2,5}-([0-9]{1,5}|X{1,5})_[A-Z][a-z]+_[A-Za-z0-9]+_[A-Za-z0-9_]+$`.

There are other branch naming patterns allowed with a specific purpose in mind. For a comprehensive list, please see the [init.mk](../build/automation/init.mk) or [git.test.mk](../build/automation/lib/git.mk) files.

- `task/Update_automation_scripts` - used to update the Make DevOps scripts and created automatically when running `make devops-update`
- `task/Update_dependencies` - update versions or/and content of external dependencies
- `task/Update_documentation` - update documentation, e.g. diagrams, ADR entries, API documentation
- `task/Update_tests` - update tests usually done as an automated task, e.g. API contracts
- `task/Update_versions` - update versions of packages, synonym of the `task/Update_dependencies` branch
- `task/Refactor` - any type of short-lived refactoring that may not have a corresponding entry in the backlog
- `spike/JIRA-XXX_Descriptive_branch_name` - exploratory development work
- `automation/JIRA-XXX_Descriptive_branch_name` - improvements to the automation scripts and processes within the project
- `test/JIRA-XXX_Descriptive_branch_name` - tests must be part of the development work, an exception might be a higher-level test implementation, e.g. smoke test
- `release/`, `migration/` and `devops/` branch prefixes should not be used in the normal circumstances

Contributing to an already existing branch

    git checkout task/JIRA-XXX_Descriptive_branch_name
    git pull
    # Make your changes here...
    git add .
    git commit -S -m "Meaningful description of change"
    git push

Rebasing a branch onto master

    git checkout task/JIRA-XXX_Descriptive_branch_name
    git rebase -i HEAD~X                                # Squash X number of commits, all into one
    # When prompted change commit type to `squash` for all the commits except the top one
    # On the following screen replace pre-inserted comments by a single summary
    git push --force-with-lease

    git checkout master
    git pull
    git checkout task/JIRA-XXX_Descriptive_branch_name
    git rebase master
    # Resolve conflicts
    git add .
    git rebase --continue
    git push --force-with-lease

Merging a branch to master - this should be done only in an exceptional circumstance as the proper process is to raise an MR

    git checkout master
    git pull --prune                                    # Make sure master is up-to-date
    git checkout task/JIRA-XXX_Descriptive_branch_name
    git pull                                            # Make sure the task branch is up-to-date

    git rebase -i HEAD~X                                # Squash X number of commits, all into one
    # When prompted change commit type to `squash` for all the commits except the top one
    # On the following screen replace pre-inserted comments by a single summary

    git rebase master                                   # Rebase the task branch on top of master
    git checkout master                                 # Switch to master branch
    git merge -ff task/JIRA-XXX_Descriptive_branch_name # Fast-forward merge
    git push                                            # Push master to remote

    git push -d origin task/JIRA-XXX_Descriptive_branch_name   # Remove remote branch
    git branch -d task/JIRA-XXX_Descriptive_branch_name        # Remove local branch

If JIRA is currently not in use to track project changes, please drop any reference to it and omit `JIRA-XXX` in your commands.

### Git commit message

- Separate subject from body with a blank line
- Do not end the subject line with a punctuation mark
- Capitalise the subject line and each paragraph
- Use the imperative mood in the subject line
- Wrap lines at 72 characters
- Use the body to explain what and why you have done something, which should be done as part of a PR/MR description

Example:

    Short (72 chars or less) summary

    More detailed explanatory text. Wrap it to 72 characters. The blank
    line separating the summary from the body is critical (unless you omit
    the body entirely).

    Write your commit message in the imperative: "Fix bug" and not "Fixed
    bug" or "Fixes bug." This convention matches up with commit messages
    generated by commands like git merge and git revert.

    Further paragraphs come after blank lines.

    - Bullet points are okay, too.
    - Typically a hyphen or asterisk is used for the bullet, followed by a
      single space. Use a hanging indent.

### Git hooks

Git hooks are located in `build/automation/etc/githooks/scripts` and executed automatically on each commit. They are as follows:

- [branch-name-pre-commit.sh](../build/automation/etc/githooks/scripts/branch-name-pre-commit.sh)
- [editorconfig-pre-commit.sh](../build/automation/etc/githooks/scripts/editorconfig-pre-commit.sh)
- [git-message-commit-msg.sh](../build/automation/etc/githooks/scripts/git-message-commit-msg.sh)
- [git-secret-pre-commit.sh](../build/automation/etc/githooks/scripts/git-secret-pre-commit.sh)
- [python-code-pre-commit.sh](../build/automation/etc/githooks/scripts/python-code-pre-commit.sh)
- [terraform-format-pre-commit.sh](../build/automation/etc/githooks/scripts/terraform-format-pre-commit.sh)

### Git tags

Aim at driving more complex deployment workflows by tags with an exception of the master branch where the continuous deployment to a development environment should be enabled by default.

## Pull request (merge request)

- Set the title to `JIRA-XXX Descriptive branch name`, where `JIRA-XXX` is the ticket reference number
- Ensure all commits will be squashed and the source branch will be removed once the request is accepted
- Notify the team on Slack to give your colleagues opportunity to review changes and share the knowledge
- If the change has not been pair or mob programmed it must follow the code review process and be approved by at least one peer, all discussions must be resolved
- A merge to master must be squashed and rebased on top, preserving the list of all commit messages

## Code review

Please, refer to the [Clean Code](https://learning.oreilly.com/library/view/clean-code/9780136083238/), especially chapter 17 and [Clean Architecture](https://learning.oreilly.com/library/view/clean-architecture-a/9780134494272/) books by Robert C. Martin while performing peer code reviews.

## Unit tests

When writing or updating unit tests (whether you use Python, Java, Go or shell), please always structure them using the 3 A's approach of 'Arrange', 'Act', and 'Assert'. For example:

    @Test
    public void listServicesNullReturn() {

      // Arrange
      List<String> criteria = new ArrayList<>();
      criteria.add("Null");
      when(repository.findBy(criteria)).thenReturn(null);

      // Act
      List<Service> list = service.list(criteria);

      // Assert
      assertEquals(0, list.size());
    }
