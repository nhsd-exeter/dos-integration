Feature: E2E Happy Path

  @logs_checked
  Scenario: A VALID CHANGED EVENT IS PROCESSED AND ACCEPTED BY DOS
    Given a Changed Event is valid
    When the Changed Event is sent for processing
    Then the Changed Event is processed
    And the Changed Request is accepted by Dos

  @logs_checked
  Scenario: UNMATCHED SERVICE EXCEPTION IS LOGGED
    Given a Changed Event has no matching DoS services
    When the Changed Event is sent for processing
    Then the unmatched service exception is reported to cloudwatch

  @no_logs_checked
  Scenario: ALL RECEIVED CHANGED EVENT ARCHIVED IN DYNAMO
    Given a Changed Event is valid
    When the Changed Event is sent for processing
    Then the Changed Event is stored in dynamo db


# Scenario: VALID TESTS
#   Given a Change Event is valid
#   When the Change Event is sent for processing
#   Then the "processor" logs are generated

# Scenario: INVALID ODSCODE TESTS
#   Given a change event with invalid ODSCode is provided
#   When the change event is sent to the event processor
#   Then the processor lambda logs are generated

# Scenario: INVALID ORGANISATIONSUBTYPE TESTS
#   Given a change event with invalid OrganisationSubType is provided

# Scenario: TEST VALID
#   Given a "valid" change event
#   When a change event with sequence id "777" is sent to the event procesor

# Scenario: TEST INVALID
#   Given an "invalid" change event
#   When a change event with sequence id "777" is sent to the event procesor

# Scenario: Valid Change Events(CE) are processed into Change Requests(CR) by the Procesor lambda
#   Given a valid change event endpoint
#   When a "valid" change event with sequence id "98765" is sent to the event procesor
#   Then the event processor logs are generated
# # # Then a change request is received "1" times
# # #   And the change request has status code "200"

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
