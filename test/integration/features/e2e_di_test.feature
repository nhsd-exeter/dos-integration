Feature: E2E DOS INTEGRATION ON TEST ENV

  @complete
  Scenario: A VALID CHANGED EVENT IS PROCESSED AND ACCEPTED BY DOS
    Given a Changed Event is valid
    When the Changed Event is sent for processing
    Then the processed Changed Request is sent to Dos
    And the Changed Request is accepted by Dos

  @complete
  Scenario: A VALID CHANGED EVENT WITH INVALID ODSCODE IS NOT SENT TO DOS
    Given a Changed Event with invalid ODSCode is provided
    When the Changed Event is sent for processing
    Then the Changed Event is not sent to Dos
