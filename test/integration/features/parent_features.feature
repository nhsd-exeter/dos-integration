Feature: DOS INTEGRATION E2E TESTS

@complete @dev
  Scenario: A VALID CHANGED EVENT IS PROCESSED AND SENT TO DOS
    Given a Changed Event is valid
    When the Changed Event is sent for processing
    Then the processed Changed Request is sent to Dos

  @complete @dev
  Scenario: UNMATCHED DOS SERVICES EXCEPTION IS LOGGED
    Given a Changed Event with invalid ODSCode is provided
    When the Changed Event is sent for processing
    Then no matched services were found
    And the unmatched service exception is reported to cloudwatch
    Then the Changed Event is not processed any further

@complete @dev
  Scenario: ALL RECEIVED CHANGED EVENT IS ARCHIVED IN DYNAMO DB
    Given a Changed Event is valid
    When the Changed Event is sent for processing
    Then the Changed Event is stored in dynamo db


# @complete @dev @test
# Scenario: ALL RECEIVED CHANGED EVENT IS ARCHIVED IN DYNAMO DB
#   Given a Changed Event is valid

# Then the Changed Event is processed

# When the OrganisationStatus is equal to "Hidden" OR "Closed"

# And there are no changes identified

# Then there is no Change Request produced

# When the postcode is invalid

# Then the Address change is not included in the Change request

# When the postcode does not exist in DoS

# When the postcode has no LAT/Long values

# Then the Postcode is not included in the Change Request


# Scenario: INVALID ODSCODE TESTS
#   Given a change event with invalid ODSCode is provided
#   When the change event is sent to the event processor
#   Then the processor lambda logs are generated

# Scenario: INVALID ORGANISATIONSUBTYPE TESTS
#   Given a change event with invalid OrganisationSubType is provided


# Scenario: Happy Path message to DOS
#   Given I input a valid Change Event
#   When it is received by the EventBridge
#   Then a Change Request is sent to DoS
#   And a confirmation of receipt is logged

# Scenario: Rate Limiting
#   Given I input a valid Change Event (x10)
#   When they are received by the EventBridge
#   Then a maximum of 3 Change Requests a second are sent to Dos
#   And a confirmation of receipt is logged for all

# Scenario: Failed message send to DOS
#   Given I input a valid Change Event
#   When it is rejected by the DOS API Gateway
#   Then the Change Request is retried 'X' times
#   And a maximum of 3 Change Requests a second are sent to DOS
