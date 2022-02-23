Feature: F004. Error Handling

@dev
  Scenario: F004S001. DOS rejects CE and returns SC 400 with invalid Correlation ID and logs error in Splunk
    Given a Changed Event is valid
    And the correlation-id is "Bad Request"
    When the Changed Event is sent for processing with "valid" api key
    Then the event is sent to the DLQ
    And the DLQ logs the error for Splunk
    And the "cr_dlq" logs show status code "400"
    And the Changed Event is stored in dynamo db

  @dev
  Scenario: F004S002. A CR with invalid Correlation ID gets rejected by events bridge and is NOT sent to DOS
    Given a Changed Event is valid
    And the correlation-id is "Bad Request"
    When the Changed Event is sent for processing with "valid" api key
    Then the "cr_dlq" logs show error message "Message Abandoned"
    And the Changed Event is stored in dynamo db

  # FAILING TESTS.. WAITING ON BUG FIX
  @complete @dev @wip
  Scenario: F004S003. A Changed Event where Specified opening date is set as closed is captured
    Given a specific Changed Event is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the date for the specified opening time returns an empty list
    And the Changed Event is stored in dynamo db

  @complete @dev
  Scenario: F004S004. A Changed Event where Standard opening day is set as closed is captured
    Given a specific Changed Event is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the day for the standard opening time returns an empty list
    And the Changed Event is stored in dynamo db
