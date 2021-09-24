# Contract Test

## Table of contents

- [Contract Test](#contract-test)
  - [Table of contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Run the test suite from the command-line](#run-the-test-suite-from-the-command-line)
  - [Run the test suite using Postman](#run-the-test-suite-using-postman)

## Introduction

Initially, the contract test suite should consists of two parts

1. Wiremock mappings (service API interface definitions) in the `test/contract/mappings` directory
2. Postman test collection in the `test/contract` directory

## Run the test suite from the command-line

From within the `test/contract` directory which is the sub-project directory we can do the following to execute the test suite

    make start
    make run
    # Update the mappings
    make reload
    make run
    # ...

or simply run it as a single command

    make -s test

## Run the test suite using Postman

- Start up the Wiremock service by running `make start`
- [Import](https://learning.postman.com/docs/getting-started/importing-and-exporting-data/) the Postman collection from the `test/contract` directory
- [Select](https://learning.postman.com/docs/sending-requests/managing-environments/#selecting-an-active-environment) the `Postman` environment (the `Docker` one is only used from the command-line)
- [Run](https://learning.postman.com/docs/running-collections/intro-to-collection-runs/) the test collection
