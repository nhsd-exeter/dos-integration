Feature: F005. Support Functions

  @complete @dev
  Scenario: F005S001. An unprocessed Changed Event is replayed in DI
    Given a Changed Event is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Event is stored in dynamo db
    And the stored Changed Event is reprocessed in DI
    And the reprocessed Changed Event is sent to Dos
