JAVA_VERSION = 16

# TODO: Print Java version in prompt always when `.java-version` file is present, not only if diffrent to global

java-install: ### Install and configure Java - optional: JAVA_VERSION
	eval "$$(jenv init -)"
	jenv enable-plugin export
	jenv add /Library/Java/JavaVirtualMachines/adoptopenjdk-$(JAVA_VERSION).jdk/Contents/Home
	jenv versions # ls -1 /Library/Java/JavaVirtualMachines
	jenv global $(JAVA_VERSION)

java-virtualenv: ### Setup Java virtual environment - optional: JAVA_VERSION
	brew update
	brew install --cask adoptopenjdk$(JAVA_VERSION)
	jenv add /Library/Java/JavaVirtualMachines/adoptopenjdk-$(JAVA_VERSION).jdk/Contents/Home
	jenv local $(JAVA_VERSION)
	sed -i 's;    "java.home":.*;    "java.home": "/Library/Java/JavaVirtualMachines/adoptopenjdk-$(JAVA_VERSION).jdk/Contents/Home",;g' project.code-workspace

java-virtualenv-clean: ### Clean up Java virtual environment
	rm -f .java-version

java-clean: ### Clean up Java project files - mandatory: DIR=[Java project directory]; optional: EXCLUDE=[directory, file or pattern]
	[ -z "$(DIR)" ] && (echo "ERROR: Please, specify the DIR"; exit 1)
	[ -n "$(EXCLUDE)" ] && exclude="grep -vE $(EXCLUDE)" || exclude=cat
	find $(DIR) \( \
		-name ".settings" -o \
		-name "bin" -o \
		-name "build" -o \
		-name "target" -o \
		-name ".classpath" -o \
		-name ".factorypath" -o \
		-name ".project" -o \
		-name "*.iml" \
	\) -print | $$exclude | xargs rm -rfv

java-add-certificate-to-keystore: ### Add certificate to the Java keystore and include it in the project
	sudo keytool -delete -storepass changeit \
		-keystore $(JAVA_HOME)/lib/security/cacerts \
		-alias $(PROJECT_GROUP_SHORT)-$(PROJECT_NAME_SHORT) > /dev/null 2>&1 ||:
	sudo keytool -import -trustcacerts -noprompt -storepass changeit \
		-file $(PROJECT_DIR)/build/automation/etc/certificate/certificate.pem \
		-keystore $(JAVA_HOME)/lib/security/cacerts \
		-alias $(PROJECT_GROUP_SHORT)-$(PROJECT_NAME_SHORT)
	keytool -list -storepass changeit -keystore $(JAVA_HOME)/lib/security/cacerts | grep -A 1 $(PROJECT_GROUP_SHORT)-$(PROJECT_NAME_SHORT)
	if [ ! -f $(ETC_DIR)/keystore.jks ]; then
		cp -fv $(JAVA_HOME)/lib/security/cacerts $(ETC_DIR)/keystore.jks
	fi

java-check-versions: ### Check Java versions alignment
	echo "java library: $(JAVA_VERSION) (current $(DEVOPS_PROJECT_VERSION))"
	echo "java library aws: none"
	echo "java virtual: $$(brew search --cask adoptopenjdk | grep "adoptopenjdk[0-9]*\(\.[0-9]*\(\.[0-9]*\)\?\)\?$$" | grep -o "[0-9]*\(\.[0-9]*\(\.[0-9]*\)\?\)\?$$" | sort -V -r | head -n 1 | sed "s/^[[:space:]]*//g") (latest)"
	echo "java docker: $$(make docker-repo-list-tags REPO=openjdk | grep -w "^[0-9]*\(\.[0-9]*\(\.[0-9]*\)\?\)\?-alpine$$" | sort -V -r | head -n 1 | sed "s/-alpine//g" | sed "s/^[[:space:]]*//g") (latest)"
	echo "java aws: unknown"

.SILENT: \
	java-check-versions
