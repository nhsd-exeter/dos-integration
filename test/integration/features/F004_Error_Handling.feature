Feature: F004. Error Handling

  @complete @pharmacy_cloudwatch_queries
  Scenario: F004SXX5. An exception is raised when Sequence number is not present in headers
    Given a basic service is created
    When the Changed Event is sent for processing with no sequence id
    Then the change event response has status code "400"

  @complete @pharmacy_cloudwatch_queries
  Scenario: F004SXX6. An Alphanumeric Sequence number raises a 400 Bad Request exception
    Given a basic service is created
    When the Changed Event is sent for processing with sequence id "ABCD1"
    Then the change event response has status code "400"
    And the Slack channel shows an alert saying "DI 4XX Endpoint Errors" from "SHARED_ENVIRONMENT"

  @complete @pharmacy_cloudwatch_queries
  Scenario Outline: F004SXX7. An exception is raised when Sequence number is less than previous
    Given a basic service is created
    And the ODS has an entry in dynamodb
    And the change event "Address2" is set to "Edited"
    When the Changed Event is sent for processing with sequence id "<seqid>"
    Then the "ingest-change-event" lambda shows field "message" with value "Sequence id is smaller than the existing one"

    Examples: These are both lower than the default sequence-id values
      | seqid |
      | 1     |
      | -1234 |

  @complete @pharmacy_cloudwatch_queries
  Scenario Outline: F004SX14 Exception raised and CR created for Changed Event with invalid URL
    Given a basic service is created
    And the change event "website" is set to "<url>"
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "error_reason" with value "Website is not valid"

    Examples: Invalid Web address variations
      | url                            |
      | https://TESTPHARMACY@GMAIL.COM |
      | test@gmail.com                 |

  @complete @pharmacy_cloudwatch_queries
  Scenario: F004SX15 Verify service sync log data does not overlap
    Given a basic service is created
    And the change event "Address2" is set to "Edited"
    When the Changed Event is sent for processing with "valid" api key
    Given a basic service is created
    And the change event "Address2" is set to "Edited Again"
    When the Changed Event is sent for processing with "valid" api key
    Then service sync log contains no overlapping log data
