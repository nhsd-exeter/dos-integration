Feature: F004. Error Handling

  @dev
  Scenario: F004S001. DOS rejects CE and returns SC 400 with invalid Correlation ID and logs error in Splunk
    Given a Changed Event is valid
    And the correlation-id is "Bad Request"
    When the Changed Event is sent for processing with "valid" api key
    Then the Event "sender" shows field "response_text" with message "Fake Bad Request"
    Then the Event "cr_dlq" shows field "report_key" with message "CR_DLQ_HANDLER_RECEIVED_EVENT"
    Then the Event "cr_dlq" shows field "error_msg_http_code" with message "400"
    And the Changed Event is stored in dynamo db

  @dev
  Scenario: F004S002. A CR with invalid Correlation ID gets rejected by events bridge and is NOT sent to DOS
    Given a Changed Event is valid
    And the correlation-id is "Bad Request"
    When the Changed Event is sent for processing with "valid" api key
    Then the Event "cr_dlq" shows field "error_msg" with message "Message Abandoned"
    And the Changed Event is stored in dynamo db

@complete @dev @pharmacy_cloudwatch_queries
  Scenario: F004S003. A Changed Event where Specified opening date is set as closed is captured
    Given a specific Changed Event is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the date for the specified opening time returns an empty list
    And the Changed Event is stored in dynamo db

@complete @dev @pharmacy_cloudwatch_queries
  Scenario: F004S004. A Changed Event where Standard opening day is set as closed is captured
    Given a specific Changed Event is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the day for the standard opening time returns an empty list
    And the Changed Event is stored in dynamo db

@complete @dev @pharmacy_cloudwatch_queries
  Scenario: F004S005. An exception is raised when Sequence number is not present in headers
    Given an ODS has an entry in dynamodb
    When the Changed Event is sent for processing with no sequence id
    Then the change request has status code "400"

@complete @pharmacy_no_log_searches
  Scenario: F004S006. An exception is raised when Sequence number is a duplicate of current
    Given an ODS has an entry in dynamodb
    When the Changed Event is sent for processing with a duplicate sequence id
    Then the Changed Request is accepted by Dos
    And the Changed Event is stored in dynamo db

@complete @dev @pharmacy_cloudwatch_queries
  Scenario: F004S007. An Alphanumeric Sequence number raises a 400 Bad Request exception
    Given an ODS has an entry in dynamodb
    When the Changed Event is sent for processing with sequence id "ABCD1"
    Then the change request has status code "400"

@complete @dev @pharmacy_cloudwatch_queries
  Scenario Outline: F004S008. An exception is raised when Sequence number is less than previous
    Given an ODS has an entry in dynamodb
    When the Changed Event is sent for processing with sequence id "<seqid>"
    Then the Event "processor" shows field "message" with message "Sequence id is smaller than the existing one"

    Examples: These are both lower than the default sequence-id values
      | seqid |
      | 1     |
      | -1234 |

@pharmacy_dentist_off_smoke_test
  Scenario Outline: F004S009. Dentist and Pharmacy org types not accepted
    Given a "<org_type>" Changed Event is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the Event "processor" shows field "message" with message "Validation Error"

    Examples: Organisation types
      | org_type |
      | dentist  |
      | pharmacy |


@complete @pharmacy_dentist_smoke_test
  Scenario Outline: F004S010. Dentist and Pharmacy org types accepted
    Given a "<org_type>" Changed Event is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the processed Changed Request is sent to Dos

    Examples: Organisation types
      | org_type |
      | pharmacy |
      | dentist  |


@dev @dentist_cloudwatch_queries
  Scenario Outline: F004S011. Only the Dentist org type accepted
    Given a "dentist" Changed Event is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the processed Changed Request is sent to Dos


@dev @dentist_cloudwatch_queries
  Scenario Outline: F004S012. Exception is raised when unaccepted Pharmacy org type CE is processed
    Given a "pharmacy" Changed Event is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the Event "processor" shows field "message" with message "Validation Error"


@dev @pharmacy_cloudwatch_queries
  Scenario Outline: F004S013. Only the Pharmacy org type accepted
    Given a "pharmacy" Changed Event is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the processed Changed Request is sent to Dos


@dev @pharmacy_cloudwatch_queries
  Scenario Outline: F004S014. Exception is raised when unaccepted Dentist org type CE is processed
    Given a "dentist" Changed Event is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the Event "processor" shows field "message" with message "Validation Error"
