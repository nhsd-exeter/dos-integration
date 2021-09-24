file-remove-content: ### Remove multiline content from given file - mandatory: FILE,CONTENT="// BEGIN: Content(.)*// END: Content"
	permissions=$$(stat -c %a $(FILE))
	str=$$(echo "$(CONTENT)" | sed 's/\//\\\//g')
	tmp_file=/tmp/$$(basename -- "$(FILE)").$$
	cat $(FILE) | perl -0777 -pe "s/$$str//gs" > $$tmp_file
	mv -f $$tmp_file $(FILE)
	chmod $$permissions $(FILE)

file-replace-content: ### Replace multiline content from given file - mandatory: FILE,OLD="// BEGIN: Content(.)*// END: Content",NEW=[string]
	permissions=$$(stat -c %a $(FILE))
	str1=$$(echo "$(OLD)" | sed 's/\//\\\//g')
	str2=$$(echo "$(NEW)" | sed 's/\//\\\//g')
	tmp_file=/tmp/$$(basename -- "$(FILE)").$$
	cat $(FILE) | perl -0777 -pe "s/$$str1/$$str2/gs" > $$tmp_file
	mv -f $$tmp_file $(FILE)
	chmod $$permissions $(FILE)

file-replace-variables: ### Replace all placholders in given file - mandatory: FILE; optional: SUFFIX=[variable suffix, defaults to _TO_REPLACE],EXCLUDE_FILE_NAME=true
	suffix=$(or $(SUFFIX), _TO_REPLACE)
	echo "Replace placholders in '$$(echo $(FILE) | sed "s;$(PROJECT_DIR);;g")'"
	# Replace placholders in file content
	for str in $$(cat $(FILE) | grep -Eo "\$$\{[A-Za-z0-9_]*$${suffix}\}|\$$[A-Za-z0-9_]*$${suffix}|[A-Za-z0-9_]*$${suffix}" | sed 's/\$$//g' | sed 's/{//g' | sed 's/}//g' | sort | uniq); do
		key=$$(echo $$str | sed "s/$${suffix}//g")
		value=$$(echo $$(eval echo "\$$$$key"))
		if [ -z "$$value" ]; then
			echo "WARNING: Variable $$key has no value in '$$(echo $(FILE) | sed "s;$(PROJECT_DIR);;g")'"
		else
			# Replace `${VARIABLE_TO_REPLACE}`
			sed -i "s;\$${$${key}$${suffix}};$${value//&/\\&};g" $(FILE)
			# Replace `$VARIABLE_TO_REPLACE`
			sed -i "s;\$$$${key}$${suffix};$${value//&/\\&};g" $(FILE)
			# Replace `VARIABLE_TO_REPLACE`
			sed -i "s;$${key}$${suffix};$${value//&/\\&};g" $(FILE)
		fi
	done
	# Replace placholders in file name
	if [[ ! "$(EXCLUDE_FILE_NAME)" =~ ^(true|yes|y|on|1|TRUE|YES|Y|ON)$$ ]] && [[ $(FILE) == *"$${suffix}"* ]]; then
		file=$(FILE)
		for str in $$(echo $(FILE) | grep -Eo "[A-Za-z0-9_]*$${suffix}" | sort | uniq); do
			key=$$(echo $$str | sed "s/$${suffix}//g")
			value=$$(echo $$(eval echo "\$$$$key"))
			file=$$(echo $$file | sed "s;$${key}$${suffix};$${value};g")
		done
		echo "Rename file '$$(echo $(FILE) | sed "s;$(PROJECT_DIR);;g")' to '$$file'"
		[ -z "$$value" ] && echo "WARNING: Variable $$key has no value for '$(FILE)'" || ( \
			mkdir -p $$(dirname $$file)
			mv -f $(FILE) $$file
		)
	fi

file-replace-variables-in-dir: ### Replace placholders in all files in given directory - mandatory: DIR; optional: SUFFIX=[variable suffix, defaults to _TO_REPLACE],EXCLUDE_FILE_NAME=true
	files=($$(find $(DIR) -type f -exec grep -Il '.' {} \; | xargs -L 1 echo))
	for file in $${files[@]}; do
		make file-replace-variables FILE=$$file SUFFIX=$(SUFFIX) EXCLUDE_FILE_NAME=$(EXCLUDE_FILE_NAME)
	done

file-copy-and-replace: ### Copy file to an alternative location and replace placholders - mandatory: SRC,DEST; optional: `&& trap "rm -f $(DEST)" EXIT`
	cp $(SRC) $(DEST)
	make file-replace-variables FILE=$(DEST)
