Feature: F004. Error Handling

  @dev @broken
  Scenario: F004S001. DOS rejects CE and returns SC 400 with invalid Correlation ID and logs error in Splunk
    Given a "pharmacy" Changed Event is aligned with DoS
    And the correlation-id is "Bad Request"
    When the Changed Event is sent for processing with "valid" api key
    Then the Event "sender" shows field "response_text" with message "Fake Bad Request"
    Then the Event "cr_dlq" shows field "report_key" with message "CR_DLQ_HANDLER_RECEIVED_EVENT"
    Then the Event "cr_dlq" shows field "error_msg_http_code" with message "400"
    And the Changed Event is stored in dynamo db

  # Refactor to read from DB
  @complete @dev @pharmacy_cloudwatch_queries
  Scenario: F004S003. A Changed Event where Specified opening date is set as closed is captured
    Given a specific Changed Event is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the date for the specified opening time returns an empty list

  # Refactor to read from DB
  @complete @dev @pharmacy_cloudwatch_queries
  Scenario: F004S004. A Changed Event where Standard opening day is set as closed is captured
    Given a specific Changed Event is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the day for the standard opening time returns an empty list

  @complete @dev @pharmacy_cloudwatch_queries
  Scenario: F004S005. An exception is raised when Sequence number is not present in headers
    Given an ODS has an entry in dynamodb
    When the Changed Event is sent for processing with no sequence id
    Then the change event response has status code "400"

  @complete @dev @pharmacy_cloudwatch_queries
  Scenario: F004S006. An Alphanumeric Sequence number raises a 400 Bad Request exception
    Given an ODS has an entry in dynamodb
    When the Changed Event is sent for processing with sequence id "ABCD1"
    Then the change event response has status code "400"
    And the Slack channel shows an alert saying "DI 4XX Endpoint Errors" from "SHARED_ENVIRONMENT"

  @complete @dev @pharmacy_cloudwatch_queries
  #This test has issues on a cleared ddb
  Scenario Outline: F004S007. An exception is raised when Sequence number is less than previous
    Given an ODS has an entry in dynamodb
    When the Changed Event is sent for processing with sequence id "<seqid>"
    Then the "ingest-change-event" lambda shows field "message" with message "Sequence id is smaller than the existing one"

    Examples: These are both lower than the default sequence-id values
      | seqid |
      | 1     |
      | -1234 |

  # @pharmacy_dentist_off_smoke_test @broken
  # Scenario Outline: F004S008. Dentist and Pharmacy org types not accepted
  #   Given a "<org_type>" Changed Event is aligned with DoS
  #   When the Changed Event is sent for processing with "valid" api key
  #   Then the Event "processor" shows field "message" with message "Validation Error"

  #   Examples: Organisation types
  #     | org_type |
  #     | dentist  |
  #     | pharmacy |


  # @complete @broken @pharmacy_dentist_smoke_test
  # Scenario Outline: F004S09. Dentist and Pharmacy org types accepted
  #   Given a "<org_type>" Changed Event is aligned with DoS
  #   When the Changed Event is sent for processing with "valid" api key
  #   Then the processed Changed Request is sent to Dos

  #   Examples: Organisation types
  #     | org_type |
  #     | pharmacy |
  #     | dentist  |


  # @complete @broken @dev @dentist_cloudwatch_queries
  # Scenario Outline: F004S010. A Changed Event with Dentist org type is accepted
  #   Given a "dentist" Changed Event is aligned with DoS
  #   When the Changed Event is sent for processing with "valid" api key
  #   Then the processed Changed Request is sent to Dos


  # @dev @dentist_cloudwatch_queries
  # Scenario Outline: F004S011. Exception is raised when unaccepted Pharmacy org type CE is processed
  #   Given a "pharmacy" Changed Event is aligned with DoS
  #   When the Changed Event is sent for processing with "valid" api key
  #   Then the Event "processor" shows field "message" with message "Validation Error"



  @dev @pharmacy_cloudwatch_queries
  Scenario Outline: F004S013. Exception is raised when unaccepted Dentist org type CE is processed
    Given a "dentist" Changed Event is aligned with DoS
    When the Changed Event is sent for processing with "valid" api key
    Then the "ingest-change-event" lambda shows field "message" with message "Validation Error - Unexpected Org Type ID: 'Dentist'"

  @complete @pharmacy_cloudwatch_queries
  Scenario Outline: F004S014 Exception raised and CR created for Changed Event with invalid URL
    Given a Changed Event with changed "<url>" variations is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "error_reason" with message "Website is not valid"

    Examples: Invalid Web address variations
      | url                            |
      | https://TESTPHARMACY@GMAIL.COM |
      | test@gmail.com                 |

  @complete @pharmacy_cloudwatch_queries
  Scenario: F004015 Verify service sync log data does not overlap
    Given a "pharmacy" Changed Event is aligned with DoS
    When the Changed Event is sent for processing with "valid" api key
    Given a "pharmacy" Changed Event is aligned with DoS
    When the Changed Event is sent for processing with "valid" api key
    Then service sync log contains no overlapping log data
