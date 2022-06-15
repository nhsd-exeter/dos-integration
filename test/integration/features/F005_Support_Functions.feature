Feature: F005. Support Functions

@complete @pharmacy_no_log_searches
  Scenario: F005S001. An unprocessed Changed Event is replayed in DI
    Given a "pharmacy" Changed Event is aligned with Dos
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Event is stored in dynamo db
    And the stored Changed Event is reprocessed in DI
