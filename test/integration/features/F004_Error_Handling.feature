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

@complete @dev
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

  @complete @dev
  Scenario: F004S005. Sequence number is not present in headers
    Given an ODS has an entry in dynamodb
    When the Changed Event is sent for processing with no sequence id
    Then the change request has status code "400"

  @complete @dev
  Scenario: F004S006. Sequence number is duplicate of current
    Given an ODS has an entry in dynamodb
    When the Changed Event is sent for processing with a duplicate sequence id
    Then the processed Changed Request is sent to Dos
    And the Changed Event is stored in dynamo db

  @complete @dev
  Scenario: F004S007. Alphanumeric sequence number gets 400 Bad Request
    Given an ODS has an entry in dynamodb
    When the Changed Event is sent for processing with sequence id ABCD1
    Then the change request has status code "400"

  @complete @dev
  Scenario Outline: F004S008. Scenario Outline for sequence id tests
    Given an ODS has an entry in dynamodb
    When the Changed Event is sent for processing with sequence id <seqid>
    Then the event processor logs should record a sequence error

    Examples: These are both lower than the default sequence-id values
    | seqid |
    |  1    |
    | -1234 |
