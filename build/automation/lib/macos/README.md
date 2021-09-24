# Setting up your macOS using [Make DevOps](https://github.com/nhsd-exeter/make-devops)

## Next steps

- Restart your macOS
- Fully enable the `Avast Security` antivirus software
- Open the `Docker Desktop` application and make sure it always starts when you log in and has sufficient resources allocated. e.g. at least 4GB memory and 4 CPUs, about 100GB of storage space
- Use the `Spectacle` and `KeepingYouAwake` applications to improve the ergonomics
- Go to System Preferences > Security & Privacy > Privacy > Accessibility > [ Add iTerm to the list ]
- Go to System Preferences > Security & Privacy > Privacy > Full Disk Access > [ Add iTerm to the list ]
- If you can no longer open Java-based applications (e.g. DBeaver) due to the JDK execution error, follow the steps below
  1. Run from the command-line `sudo spctl --master-disable` to disable the Gatekeeper
  2. Open the application again (e.g. DBeaver), which now should open normally
  3. Run from the command-line `sudo spctl --master-enable` to enable the Gatekeeper again
- Always check if your operating system is up-to-date an in the latest major version
- Clone git projects to the `~/projects` directory
- Your AWS profiles are stored in `~/.aws/config`, check it
- Your AWS credentials are stored in `~/.aws/credentials`, check it
- Run `make devops-setup-aws-accounts` or edit `~/.dotfiles/oh-my-zsh/plugins/make-devops/aws-platform.zsh` to set correct AWS platform variables, i.e. `AWS_ACCOUNT_ID_LIVE_PARENT`, `AWS_ACCOUNT_ID_MGMT`, `AWS_ACCOUNT_ID_NONPROD`, `AWS_ACCOUNT_ID_PROD`
- Place the Kubernetes NONPROD configuration as `~/.kube/configs/lk8s-nonprod-kubeconfig` file and the `KUBECONFIG` environment variable will be set automatically when your shell session reloads
- Follow [this](https://github.com/nhsd-exeter/make-devops/blob/master/documentation/CONTRIBUTING.md#signing-your-git-commits) manual to set up signing your Git commits
- From now on use `iTerm` as your terminal, `Visual Studio Code` as your IDE and `Firefox` for web development. These tools have been configured to support development in
  - Node
  - Python
  - Java
  - Go
- Run the `curl -L bit.ly/make-devops | bash` script at least once a month to make sure your macOS is up-to-date

## Useful commands

- `tns` - Toggle natural scrolling
- `tx-mfa` - Prompt for new AWS MFA session, use `tx-mfa-clear` to clear it
- `tx-ssm-connect` - Prompt for new AWS SSM session
- `nvm` (Node), `pyenv` (Python), `jenv` (Java), `gvm` (Go) to set up and switch virtual environments
- Git
  - `gs` (git status --short)
  - `gd` (git diff)
  - `gd+` (git diff --cached)
  - `ga` (git add)
  - `gc` (git commit --gpg-sign -m)
  - `gl` / `gl+` (git log --graph --oneline --decorate / git log --graph --oneline --decorate --stat)
  - `gpu` (git push)
  - `gf` (git fetch --prune)
  - `gp` (git pull --prune)
  - `gcm` (git checkout master)
  - `gco` (git checkout)
- Docker
  - `dim` (docker images)
  - `dps` (docker ps --all)
  - `drc` (docker rm --volumes --force \$(docker ps --all --quiet) 2> /dev/null)

## Starting from scratch

- Turn off and then on your MacBook and immediately press and hold
  - Command-R to enter the macOS Recovery mode for a MacBook with an Intel-based processor
  - The power button until you see "Loading startup options" then via Options enter the macOS Recovery mode for a MacBook with an M1 processor
- Within the Disk Utility application erase the Internal disk and set it to "APFS (Case-sensitive, Encrypted)", with the disk name "System"
- Reinstall the operating system
- If you are presented with the following message "You may not install to this volume because it has a disk password" go back to the Disk Utility application and use "APFS (Case-sensitive)" configuration instead. The disk encryption will be set up later
- Create the administrator account
- Create a developer account with the administrative privileges
- Log in as the developer and register your Apple ID
- If disk encryption hasn't been set up yet, now is the time - go to the System Preferences > Security & Privacy > FileVault > [ Turn On FileVault ]
- Perform all system updates
- Go to System Preferences > Software Update > [ Tick all the checkboxes ]
- Go to System Preferences > Sharing > Computer Name > [ Set name to macos-xxxxxx ]
- Run Make DevOps script by executing `curl -L bit.ly/make-devops | bash` in the Terminal. This script may ask you to install the following packages
  - Xcode Command Line Tools
  - Homebrew
  - GNU Make
- If the network connectivity fails in random places, especially while installing or updating the Homebrew package manager, try to set your DNS server to 8.8.8.8 which may solve the issue. This may be the case for the UK-based Virgin Media broadband provider.
- Please, follow the instructions provided by the script and execute them from the command-line to satisfy the dependencies
- Go to System Preferences > Security & Privacy > General > [ Enable software ] - you may need to re-run installation of the failed software

---

> _A copy of this page has been saved to your desktop._
