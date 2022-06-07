DEV_OHMYZSH_DIR := ~/.dotfiles/oh-my-zsh

macos-setup devops-setup: ### Provision and configure your macOS - optional: REINSTALL=true
	rm -f $(SETUP_COMPLETE_FLAG_FILE)
	make _macos-disable-gatekeeper
	make \
		macos-prepare \
		macos-update \
		macos-install-essential \
		macos-install-additional \
		macos-install-corporate \
		macos-config \
		macos-fix
	make _macos-enable-gatekeeper
	touch $(SETUP_COMPLETE_FLAG_FILE)

macos-prepare:: ### Prepare for installation and configuration of the development dependencies
	networksetup -setdnsservers Wi-Fi 8.8.8.8 ||:
	sudo chown -R $$(id -u) $$(brew --prefix)/*

macos-update:: ### Update all currently installed development dependencies
	softwareupdate --all --install --force ||:
	xcode-select --install 2> /dev/null ||:
	which mas > /dev/null 2>&1 || brew install mas
	sudo xcodebuild -license accept ||:; mas list | grep Xcode || ( mas install $$(mas search Xcode | head -n 1 | awk '{ print $$1 }') && mas upgrade $$(mas list | grep Xcode | awk '{ print $$1 }') ) ||:
	[ $(SYSTEM_ARCH_NAME) == arm64 ] && sudo softwareupdate --install-rosetta --agree-to-license ||:
	brew update
	brew upgrade ||:
	brew tap buo/cask-upgrade
	brew cu --all --yes ||:

macos-install-essential:: ### Install essential development dependencies - optional: REINSTALL=true
	export HOMEBREW_NO_AUTO_UPDATE=1
	install="install"
	if [[ "$$REINSTALL" =~ ^(true|yes|y|on|1|TRUE|YES|Y|ON)$$ ]]; then
		install="reinstall --force"
	fi
	brew tap adoptopenjdk/openjdk ||:
	brew tap blendle/blendle ||:
	brew tap buo/cask-upgrade ||:
	brew tap homebrew/cask-fonts ||:
	brew tap homebrew/cask-versions ||:
	brew tap johanhaleby/kubetail ||:
	brew $$install ack ||:
	brew $$install amazon-ecs-cli ||:
	brew $$install aws-iam-authenticator ||:
	brew $$install awscli ||:
	brew $$install bash ||:
	brew $$install coreutils ||:
	brew $$install ctop ||:
	brew $$install dive ||:
	brew $$install findutils ||:
	brew $$install gawk ||:
	brew $$install git ||:
	brew $$install git-crypt ||:
	brew $$install git-secrets ||:
	brew $$install gnu-sed ||:
	brew $$install gnu-tar ||:
	brew $$install gnutls ||:
	brew $$install go ||:
	brew $$install google-authenticator-libpam ||:
	brew $$install google-java-format ||:
	brew $$install gpg ||:
	brew $$install gradle ||:
	brew $$install graphviz ||:
	brew $$install grep ||:
	brew $$install helm ||:
	brew $$install httpie ||:
	brew $$install jc ||:
	brew $$install jenv ||:
	brew $$install jq ||:
	brew $$install kns ||:
	brew $$install kubetail ||:
	brew $$install kustomize ||:
	brew $$install make ||:
	brew $$install mas ||:
	brew $$install minikube ||:
	brew $$install nvm ||:
	brew $$install openssl ||:
	brew $$install pyenv ||:
	brew $$install pyenv-virtualenv ||:
	brew $$install pyenv-which-ext ||:
	brew $$install python@$(PYTHON_VERSION_MAJOR).$(PYTHON_VERSION_MINOR) ||:
	brew $$install readline ||:
	brew $$install remotemobprogramming/brew/mob ||:
	brew $$install shellcheck ||:
	brew $$install sqlite3 ||:
	brew $$install tmux ||:
	brew $$install tree ||:
	brew $$install warrensbox/tap/tfswitch || brew uninstall --force terrafrom && brew reinstall --force warrensbox/tap/tfswitch ||:
	brew $$install xz ||:
	brew $$install yq ||:
	brew $$install zlib ||:
	brew $$install zsh ||:
	brew $$install zsh-autosuggestions ||:
	brew $$install zsh-completions ||:
	brew $$install zsh-syntax-highlighting ||:
	brew $$install --cask adoptopenjdk$(JAVA_VERSION) ||:
	brew $$install --cask docker ||:
	brew $$install --cask font-hack-nerd-font ||:
	brew $$install --cask iterm2 ||:
	brew $$install --cask visual-studio-code && which code > /dev/null 2>&1 || brew reinstall --cask --force visual-studio-code ||:
	# maven depends on java
	brew $$install maven ||:
	# Serverless
	curl -o- -L https://slss.io/install | bash ||:

macos-install-additional:: ### Install additional development dependencies - optional: REINSTALL=true
	export HOMEBREW_NO_AUTO_UPDATE=1
	install="install"
	if [[ "$$REINSTALL" =~ ^(true|yes|y|on|1|TRUE|YES|Y|ON)$$ ]]; then
		install="reinstall --force"
	fi
	brew tap weaveworks/tap ||:
	brew $$install github/gh/gh ||:
	brew $$install --cask atom ||:
	brew $$install --cask dbeaver-community ||:
	brew $$install --cask drawio ||:
	brew $$install --cask firefox-developer-edition ||:
	brew $$install --cask gimp ||:
	brew $$install --cask gitkraken ||:
	brew $$install --cask google-chrome ||:
	brew $$install --cask keepingyouawake ||:
	brew $$install --cask nosql-workbench ||:
	brew $$install --cask postman ||:
	brew $$install --cask sourcetree ||:
	brew $$install --cask spectacle ||:
	brew $$install --cask tunnelblick ||:
	# Protoman
	protoman_ver=$$(curl -s https://github.com/spluxx/Protoman/releases | grep "releases/tag" | grep -o "[0-9]*\.[0-9]*\(\.[0-9]*\)\?" | sort -V -r | head -n 1)
	curl -fsSL https://github.com/spluxx/Protoman/releases/download/v$${protoman_ver}/Protoman-$${protoman_ver}.dmg -o /tmp/Protoman-$${protoman_ver}.dmg
	sudo hdiutil attach /tmp/Protoman-$${protoman_ver}.dmg
	cd "/Volumes/Protoman $${protoman_ver}"
	sudo cp -rf Protoman.app /Applications
	cd -
	sudo hdiutil detach "/Volumes/Protoman $${protoman_ver}"
	rm -rf /tmp/Protoman-$${protoman_ver}.dmg
	#brew $$install --cask microsoft-remote-desktop-beta ||:
	# # Pinned package: vagrant
	# brew reinstall --cask --force \
	# 	https://raw.githubusercontent.com/Homebrew/homebrew-cask/ae2a540ffee555491ccbb2cefa4296c76355ef9f/Casks/vagrant.rb ||:
	brew $$install --cask vagrant ||:
	# # Pinned package: virtualbox
	# brew reinstall --cask --force \
	# 	https://raw.githubusercontent.com/Homebrew/homebrew-cask/33de1ad39862b4d31528e62f931480c1ba8a90f8/Casks/virtualbox.rb ||:
	brew $$install --cask virtualbox ||:
	# # Pinned package: virtualbox-extension-pack
	# brew reinstall --cask --force \
	# 	https://raw.githubusercontent.com/Homebrew/homebrew-cask/5a0a2b2322e35ec867f6633ca985ee485255f0b1/Casks/virtualbox-extension-pack.rb ||:
	brew $$install --cask virtualbox-extension-pack ||:
	# AWS SSM Session Manager
	curl -fsSL https://s3.amazonaws.com/session-manager-downloads/plugin/latest/mac/sessionmanager-bundle.zip -o /tmp/sessionmanager-bundle.zip
	unzip -o /tmp/sessionmanager-bundle.zip -d /tmp
	sudo /tmp/sessionmanager-bundle/install -i /usr/local/sessionmanagerplugin -b /usr/local/bin/session-manager-plugin ||:
	rm -rf /tmp/sessionmanager-bundle*

macos-install-corporate:: ### Install corporate dependencies - optional: REINSTALL=true
	export HOMEBREW_NO_AUTO_UPDATE=1
	install="install"
	if [[ "$$REINSTALL" =~ ^(true|yes|y|on|1|TRUE|YES|Y|ON)$$ ]]; then
		install="reinstall --force"
	fi
	brew $$install --cask microsoft-office ||:
	brew $$install --cask microsoft-teams ||:
	brew $$install --cask slack ||:
	brew $$install --cask vmware-horizon-client ||:
	brew $$install --cask avast-security ||: # https://support.avast.com/en-gb/article/Install-Mac-Security/

macos-install-recommended:: ### Install recommended dependencies - optional: REINSTALL=true
	export HOMEBREW_NO_AUTO_UPDATE=1
	install="install"
	if [[ "$$REINSTALL" =~ ^(true|yes|y|on|1|TRUE|YES|Y|ON)$$ ]]; then
		install="reinstall --force"
	fi
	brew $$install alt-tab ||:
	brew $$install hiddenbar ||:
	brew $$install --cask appcleaner ||:
	brew $$install --cask dcommander ||:
	brew $$install --cask dropbox ||:
	brew $$install --cask enpass ||:
	brew $$install --cask google-drive ||:
	brew $$install --cask hammerspoon ||:
	brew $$install --cask istat-menus ||:
	brew $$install --cask karabiner-elements ||:
	brew $$install --cask nordvpn ||:
	brew $$install --cask raindropio ||:
	brew $$install --cask tripmode ||:
	brew $$install --cask vlc ||:
	brew $$install --cask wifi-explorer ||:
	mas list | grep MindNode || ( mas install $$(mas search MindNode | head -n 1 | awk '{ print $$1 }') && mas upgrade $$(mas list | grep MindNode | awk '{ print $$1 }') ) ||:

macos-config:: ### Configure development dependencies
	make \
		_macos-config-mac \
		_macos-config-zsh \
		_macos-config-oh-my-zsh \
		_macos-config-command-line \
		_macos-config-git \
		_macos-config-iterm2 \
		_macos-config-visual-studio-code \
		_macos-config-firefox
	make macos-info

macos-fix:: ### Fix development dependencies
	:

macos-info:: ### Show "Setting up your macOS using Make DevOps" manual
	info=$(LIB_DIR)/macos/README.md
	html=$(TMP_DIR)/make-devops-doc-$(shell echo $$info | md5sum | cut -c1-7).html
	perl $(BIN_DIR)/markdown --html4tags $$info > $$html
	cp -f $$html ~/Desktop/Setting\ up\ your\ macOS\ using\ Make\ DevOps.html
	open -a "Safari" ~/Desktop/Setting\ up\ your\ macOS\ using\ Make\ DevOps.html

# ==============================================================================

_macos-config-mac:
	sudo defaults write /Library/Preferences/com.apple.alf globalstate -int 1
	networksetup -setdnsservers Wi-Fi 8.8.8.8
	defaults write -g com.apple.trackpad.scaling -float 5.0
	defaults write -g com.apple.mouse.scaling -float 5.0
	# defaults write -g com.apple.mouse.scaling -1 # Disable mouse scaling
	defaults write -g InitialKeyRepeat -int 15
	defaults write -g KeyRepeat -int 2
	sudo mdutil -i off /
	# Errors for Big Sur ->
	sudo launchctl unload -w /System/Library/LaunchDaemons/com.apple.metadata.mds.plist
	# Add images as attachments in Mail
	defaults write com.apple.mail DisableInlineAttachmentViewing -bool yes

_macos-config-zsh:
	cat /etc/shells | grep $$(brew --prefix)/bin/zsh > /dev/null 2>&1 || sudo sh -c "echo $$(brew --prefix)/bin/zsh >> /etc/shells"
	chsh -s $$(brew --prefix)/bin/zsh

_macos-config-oh-my-zsh:
	# Backup oh-my-zsh plugin files
	mkdir -p ~/tmp/make-devops-plugins && cp -f $(DEV_OHMYZSH_DIR)/plugins/$(DEVOPS_PROJECT_NAME)/aws-platform*.zsh ~/tmp/make-devops-plugins 2> /dev/null ||:
	rm -rf $(DEV_OHMYZSH_DIR)
	ZSH=$(DEV_OHMYZSH_DIR) sh -c "$$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)" "" --unattended ||:
	git clone https://github.com/romkatv/powerlevel10k.git $(DEV_OHMYZSH_DIR)/custom/themes/powerlevel10k ||:
	rm -rf \
		$(DEV_OHMYZSH_DIR)/plugins/zsh-autosuggestions \
		$(DEV_OHMYZSH_DIR)/plugins/zsh-syntax-highlighting
	git clone https://github.com/zsh-users/zsh-autosuggestions.git $(DEV_OHMYZSH_DIR)/plugins/zsh-autosuggestions
	git clone https://github.com/zsh-users/zsh-syntax-highlighting.git $(DEV_OHMYZSH_DIR)/plugins/zsh-syntax-highlighting
	cp ~/.zshrc ~/.zshrc.bak.$$(date -u +"%Y%m%d%H%M%S") ||:
	find ~/ -maxdepth 1 -type f -mtime +3 -name '.zshrc.bak.*' -execdir rm -- '{}' \;
	cat ~/.zshrc | grep -Ev '^plugins=(.*)' > ~/.zshrc.tmp && mv ~/.zshrc.tmp ~/.zshrc
	make file-remove-content FILE=~/.zshrc CONTENT="\nsource (.)*/oh-my-zsh.sh\n"
	make file-remove-content FILE=~/.zshrc CONTENT="\n# BEGIN: Custom configuration(.)*# END: Custom configuration\n"
	echo -e "\n# BEGIN: Custom configuration" >> ~/.zshrc
	echo "export PATH=\$$HOME/bin:$(PATH_HOMEBREW):$(PATH_SYSTEM)" >> ~/.zshrc
	echo "plugins=(" >> ~/.zshrc
	echo "    git" >> ~/.zshrc
	echo "    docker" >> ~/.zshrc
	# echo "    pyenv" >> ~/.zshrc
	# echo "    jenv" >> ~/.zshrc
	# echo "    nvm" >> ~/.zshrc
	echo "    gpg-agent" >> ~/.zshrc
	echo "    common-aliases" >> ~/.zshrc
	# echo "    zsh-autosuggestions" >> ~/.zshrc
	# echo "    zsh-syntax-highlighting" >> ~/.zshrc
	echo "    $(DEVOPS_PROJECT_NAME)" >> ~/.zshrc
	echo ")" >> ~/.zshrc
	echo 'function tx-status { [ -n "$$TEXAS_SESSION_EXPIRY_TIME" ] && [ "$$(echo $$TEXAS_SESSION_EXPIRY_TIME | sed s/\[-_:\]//g)" -gt $$(date -u +"%Y%m%d%H%M%S") ] && ( [ -n "$$TEXAS_PROFILE" ] && echo $$TEXAS_PROFILE || echo $$TEXAS_ACCOUNT ) ||: }' >> ~/.zshrc
	echo "POWERLEVEL9K_CUSTOM_TEXAS=tx-status" >> ~/.zshrc
	echo "POWERLEVEL9K_CUSTOM_TEXAS_BACKGROUND=balck" >> ~/.zshrc
	echo "POWERLEVEL9K_CUSTOM_TEXAS_FOREGROUND=yellow" >> ~/.zshrc
	echo "POWERLEVEL9K_NODE_VERSION_PROJECT_ONLY=true" >> ~/.zshrc
	echo "POWERLEVEL9K_MODE=nerdfont-complete" >> ~/.zshrc
	echo "POWERLEVEL9K_LEFT_PROMPT_ELEMENTS=(dir vcs)" >> ~/.zshrc
	echo "POWERLEVEL9K_SHORTEN_DIR_LENGTH=3" >> ~/.zshrc
	# echo "POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS=(status nvm pyenv jenv custom_texas background_jobs time)" >> ~/.zshrc
	echo "POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS=(status custom_texas background_jobs time)" >> ~/.zshrc
	echo "POWERLEVEL9K_PROMPT_ON_NEWLINE=true" >> ~/.zshrc
	echo "POWERLEVEL9K_DISABLE_CONFIGURATION_WIZARD=true" >> ~/.zshrc
	echo "ZSH_THEME=powerlevel10k/powerlevel10k" >> ~/.zshrc
	echo "source \$$ZSH/oh-my-zsh.sh" >> ~/.zshrc
	echo "# END: Custom configuration" >> ~/.zshrc
	# Restore oh-my-zsh plugin files
	mkdir -p $(DEV_OHMYZSH_DIR)/plugins/$(DEVOPS_PROJECT_NAME) && cp -f ~/tmp/make-devops-plugins/aws-platform*.zsh $(DEV_OHMYZSH_DIR)/plugins/$(DEVOPS_PROJECT_NAME) 2> /dev/null ||: && rm -rf ~/tmp/make-devops-plugins
	make \
		_macos-config-oh-my-zsh-make-devops \
		_macos-config-oh-my-zsh-aws

_macos-config-oh-my-zsh-make-devops:
	mkdir -p $(DEV_OHMYZSH_DIR)/plugins/$(DEVOPS_PROJECT_NAME)
	(
		echo
		echo "# Completion"
		echo "zstyle ':completion:*:make:*:targets' call-command true"
		echo "zstyle ':completion:*:make:*' tag-order targets variables"
		echo "zstyle ':completion:*' group-name ''"
		echo "zstyle ':completion:*:descriptions' format '%B%d%b'"
		echo
		echo "# Alises"
		echo "for file in \$$HOME/usr/*-aliases; do source \$$file; done"
		echo
		echo "# Variables"
		echo "export PATH=\$$HOME/bin:$(PATH_HOMEBREW):$(PATH_SYSTEM)"
		echo "export GPG_TTY=\$$(tty)"
		echo "export KUBECONFIG=~/.kube/configs/lk8s-nonprod-kubeconfig 2> /dev/null"
		echo
		echo "# env: Python"
		echo "export PYENV_ROOT=$$HOME/.pyenv"
		echo "export PATH=\$$PYENV_ROOT/bin:\$$PATH"
		echo "export MYPY_CACHE_DIR=\$$HOME/.mypy_cache"
		echo "eval \"\$$(pyenv init --path)\""
		echo "eval \"\$$(pyenv init -)\""
		echo "eval \"\$$(pyenv virtualenv-init -)\""
		echo "# env: Go"
		echo ". $$HOME/.gvm/scripts/gvm"
		echo "# env: Java"
		echo "export JAVA_HOME=\$$(/usr/libexec/java_home -v$(JAVA_VERSION))"
		echo "eval \"\$$(jenv init -)\""
		echo "# env: Node"
		echo "export NVM_DIR=\$$HOME/.nvm"
		echo ". \$$(brew --prefix)/opt/nvm/nvm.sh"
		# echo ". \$$(brew --prefix)/opt/nvm/etc/bash_completion.d/nvm"
		# echo "autoload -U add-zsh-hook"
		# echo "load-nvmrc() {"
		# echo "  ("
		# echo "  local node_version=\"\$$(nvm version)\""
		# echo "  local nvmrc_path=\"\$$(nvm_find_nvmrc)\""
		# echo "  if [ -n \"\$$nvmrc_path\" ]; then"
		# echo "    local nvmrc_node_version=\$$(nvm version \"\$$(cat \"\$${nvmrc_path}\")\")"
		# echo "    if [ \"\$$nvmrc_node_version\" = \"N/A\" ]; then"
		# echo "      nvm install"
		# echo "    elif [ \"\$$nvmrc_node_version\" != \"\$$node_version\" ]; then"
		# echo "      nvm use"
		# echo "    fi"
		# echo "  elif [ \"\$$node_version\" != \"\$$(nvm version default)\" ]; then"
		# echo "    echo \"Reverting to nvm default version\""
		# echo "    nvm use default"
		# echo "  fi"
		# echo "  ) > /dev/null 2>&1"
		# echo "}"
		# echo "add-zsh-hook chpwd load-nvmrc"
		# echo "load-nvmrc"
		echo "# env: Serverless"
		echo "export PATH=\"$$HOME/.serverless/bin:\$$PATH\""
		echo
		echo "export EDITOR=\"code --wait\""
		echo
		echo "# AWS platform"
		echo ". $(DEV_OHMYZSH_DIR)/plugins/$(DEVOPS_PROJECT_NAME)/aws-platform.zsh"
		echo
	) > $(DEV_OHMYZSH_DIR)/plugins/$(DEVOPS_PROJECT_NAME)/$(DEVOPS_PROJECT_NAME).plugin.zsh

_macos-config-oh-my-zsh-aws:
	if [ ! -f $(DEV_OHMYZSH_DIR)/plugins/$(DEVOPS_PROJECT_NAME)/aws-platform.zsh ]; then
		make aws-accounts-create-template-config-file-v1
	fi

_macos-config-command-line:
	sudo chown -R $$(id -u) $$(brew --prefix)/*
	make \
		python-install \
		java-install
	# configure Go
	curl -sSL https://raw.githubusercontent.com/moovweb/gvm/master/binscripts/gvm-installer | bash ||:
	# configure Terraform
	tfswitch $(TERRAFORM_VERSION)
	# configure shell
	mkdir -p ~/{.aws,.kube/configs,.ssh,bin,etc,tmp,usr,projects}
	[ ! -f ~/.aws/config ] && echo -e "[default]\noutput = json\nregion = eu-west-2\n\n# TODO: Add AWS accounts\n" > ~/.aws/config
	[ ! -f ~/.aws/credentials ] && echo -e "[default]\naws_access_key_id = xxx\naws_secret_access_key = xxx\n\n# TODO: Add AWS credentials" > ~/.aws/credentials
	cp $(BIN_DIR)/* ~/bin
	cp $(USR_DIR)/* ~/usr
	make _devops-project-clean DIR=
	chmod 700 ~/.ssh
	rm -f ~/.zcompdump*

_macos-config-git:
	git config --global branch.autosetupmerge false
	git config --global branch.autosetuprebase always
	git config --global commit.gpgsign true
	git config --global core.autocrlf input
	git config --global core.filemode true
	git config --global core.hidedotfiles false
	git config --global core.ignorecase false
	git config --global pull.rebase true
	git config --global push.default current
	git config --global push.followTags true
	git config --global rebase.autoStash true
	git config --global remote.origin.prune true

_macos-config-iterm2:
	curl -fsSL https://raw.githubusercontent.com/stefaniuk/dotfiles/master/lib/resources/iterm/com.googlecode.iterm2.plist -o /tmp/com.googlecode.iterm2.plist
	defaults import com.googlecode.iterm2 /tmp/com.googlecode.iterm2.plist
	rm /tmp/com.googlecode.iterm2.plist

_macos-config-visual-studio-code:
	#
	# *** Install extensions ***
	#
	# PHP
	code --force --install-extension bmewburn.vscode-intelephense-client ||: # PHP support
	code --force --install-extension xdebug.php-debug ||: # PHP support
	#
	code --force --install-extension alefragnani.bookmarks ||:
	code --force --install-extension alefragnani.project-manager ||:
	code --force --install-extension alexkrechik.cucumberautocomplete ||:
	code --force --install-extension amazonwebservices.aws-toolkit-vscode ||:
	code --force --install-extension ban.spellright ||:
	code --force --install-extension christian-kohler.npm-intellisense ||:
	code --force --install-extension christian-kohler.path-intellisense ||:
	code --force --install-extension davidanson.vscode-markdownlint ||:
	code --force --install-extension dbaeumer.vscode-eslint ||:
	code --force --install-extension donjayamanne.githistory ||:
	code --force --install-extension dsznajder.es7-react-js-snippets ||:
	code --force --install-extension eamodio.gitlens ||:
	code --force --install-extension editorconfig.editorconfig ||:
	code --force --install-extension eg2.vscode-npm-script ||:
	code --force --install-extension emeraldwalk.runonsave ||:
	code --force --install-extension esbenp.prettier-vscode ||:
	code --force --install-extension ffaraone.pyfilesgen ||:
	code --force --install-extension formulahendry.code-runner ||:
	code --force --install-extension fosshaas.fontsize-shortcuts ||:
	code --force --install-extension gabrielbb.vscode-lombok ||:
	code --force --install-extension github.vscode-pull-request-github
	code --force --install-extension gruntfuggly.todo-tree ||:
	code --force --install-extension hashicorp.terraform ||:
	code --force --install-extension hediet.vscode-drawio ||:
	code --force --install-extension humao.rest-client ||:
	code --force --install-extension jebbs.plantuml ||:
	code --force --install-extension johnpapa.vscode-peacock ||:
	code --force --install-extension mhutchie.git-graph ||:
	code --force --install-extension mrmlnc.vscode-apache ||:
	code --force --install-extension ms-azuretools.vscode-docker ||:
	code --force --install-extension ms-python.python ||:
	code --force --install-extension ms-python.vscode-pylance ||:
	code --force --install-extension ms-toolsai.jupyter ||:
	code --force --install-extension ms-vsliveshare.vsliveshare-pack ||:
	code --force --install-extension msjsdiag.debugger-for-chrome ||:
	code --force --install-extension msjsdiag.vscode-react-native ||:
	code --force --install-extension mushan.vscode-paste-image ||:
	code --force --install-extension nicolasvuillamy.vscode-groovy-lint ||:
	code --force --install-extension oderwat.indent-rainbow ||:
	code --force --install-extension pivotal.vscode-spring-boot ||:
	code --force --install-extension redhat.java ||:
	code --force --install-extension redhat.vscode-yaml ||:
	code --force --install-extension shengchen.vscode-checkstyle ||:
	code --force --install-extension sonarsource.sonarlint-vscode ||:
	code --force --install-extension streetsidesoftware.code-spell-checker ||:
	code --force --install-extension techer.open-in-browser ||:
	code --force --install-extension timonwong.shellcheck ||:
	code --force --install-extension tomoki1207.pdf ||:
	code --force --install-extension visualstudioexptteam.vscodeintellicode ||:
	code --force --install-extension vscjava.vscode-java-pack ||:
	code --force --install-extension vscjava.vscode-spring-boot-dashboard ||:
	code --force --install-extension vscjava.vscode-spring-initializr ||:
	code --force --install-extension vscode-icons-team.vscode-icons ||:
	code --force --install-extension vsls-contrib.codetour ||:
	code --force --install-extension vsls-contrib.gistfs ||:
	code --force --install-extension wayou.vscode-todo-highlight ||:
	code --force --install-extension xabikos.javascriptsnippets ||:
	code --force --install-extension yzhang.dictionary-completion ||:
	code --force --install-extension yzhang.markdown-all-in-one ||:
	#
	# *** Install themes ***
	#
	code --force --install-extension ahmadawais.shades-of-purple ||:
	code --force --install-extension akamud.vscode-theme-onedark ||:
	code --force --install-extension arcticicestudio.nord-visual-studio-code ||:
	code --force --install-extension dracula-theme.theme-dracula ||:
	code --force --install-extension equinusocio.vsc-material-theme ||:
	code --force --install-extension ginfuru.ginfuru-better-solarized-dark-theme ||:
	code --force --install-extension johnpapa.winteriscoming ||:
	code --force --install-extension liviuschera.noctis ||:
	code --force --install-extension ryanolsonx.solarized ||:
	code --force --install-extension sdras.night-owl ||:
	code --force --install-extension smlombardi.slime ||:
	code --force --install-extension vangware.dark-plus-material ||:
	code --force --install-extension wesbos.theme-cobalt2 ||:
	code --force --install-extension zhuangtongfa.material-theme ||:
	# List them all
	code --list-extensions --show-versions
	# Copy user key bindings
	cp ~/Library/Application\ Support/Code/User/keybindings.json ~/Library/Application\ Support/Code/User/keybindings.json.bak.$$(date -u +"%Y%m%d%H%M%S") 2> /dev/null ||:
	find ~/Library/Application\ Support/Code/User -maxdepth 1 -type f -mtime +7 -name 'keybindings.json.bak.*' -execdir rm -- '{}' \;
	cp -fv $(PROJECT_DIR)/build/automation/lib/macos/vscode-keybindings.json ~/Library/Application\ Support/Code/User/keybindings.json

_macos-config-firefox:
	# function firefox_install_extension {
	# 	url=$$1
	# 	file=$$2
	# 	(
	# 		cd ~/tmp
	# 		curl -L $$url --output $$file
	# 		mv $$file $$file.zip
	# 		mkdir -p $$file
	# 		mv $$file.zip $$file
	# 		cd $$file
	# 		unzip $$file.zip
	# 		id=$$(jq -r '.applications.gecko.id' manifest.json)
	# 		profile=$$(ls -1 ~/Library/Application\ Support/Firefox/Profiles/ | grep dev-edition-default)
	# 		cp $$file.zip ~/Library/Application\ Support/Firefox/Profiles/$$profile/extensions/$$id.xpi
	# 		cd ~/tmp
	# 		rm -rf $$file
	# 	)
	# }
	# firefox_install_extension \
	# 	https://addons.mozilla.org/firefox/downloads/file/3478747/react_developer_tools-4.4.0-fx.xpi \
	# 	react_developer_tools.xpi ||:
	# firefox_install_extension \
	# 	https://addons.mozilla.org/firefox/downloads/file/1509811/redux_devtools-2.17.1-fx.xpi \
	# 	redux_devtools.xpi ||:

_macos-disable-gatekeeper:
	sudo spctl --master-disable 2> /dev/null # Works only on an Intel-based silicon

_macos-enable-gatekeeper:
	sudo spctl --master-enable 2> /dev/null # Works only on an Intel-based silicon

# ==============================================================================

.SILENT: \
	macos-config \
	macos-info \
	macos-install-additional \
	macos-install-corporate \
	macos-install-essential \
	macos-prepare \
	macos-setup \
	macos-update
