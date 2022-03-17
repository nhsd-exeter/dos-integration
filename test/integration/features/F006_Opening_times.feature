Feature: F006. Opening times

@complete
  Scenario: F006S001. Confirm actual opening times change for specified date and time is captured by Dos
    Given a specified opening time Changed Event is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the processed Changed Request is sent to Dos
    And the Changed Request with changed specified date and time is captured by Dos

@complete
  Scenario: F006S002. Confirm actual opening times change for standard date and time is captured by Dos
    Given a standard opening time Changed Event is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the processed Changed Request is sent to Dos
    And the Changed Request with changed standard day time is captured by Dos

  @complete @dev
  Scenario: F006S003. Pharmacy with one break in opening times
    Given a Changed Event is valid
    And the Changed Event has one break in opening times
    When the Changed Event is sent for processing with "valid" api key
    Then the processed Changed Request is sent to Dos
    And the opening times changes are marked as valid

  @complete @dev
  Scenario: F006S004. Pharmacy with two breaks in opening times
    Given a Changed Event is valid
    And the Changed Event has two breaks in opening times
    When the Changed Event is sent for processing with "valid" api key
    Then the processed Changed Request is sent to Dos
    And the opening times changes are marked as valid

  @complete @dev
  Scenario: F006S005. Pharmacy with one off opening date set to closed
    Given a Changed Event is valid
    And the Changed Event contains a one off opening date thats "Closed"
    When the Changed Event is sent for processing with "valid" api key
    Then the processed Changed Request is sent to Dos
    And the opening times changes are marked as valid

  @complete @dev
  Scenario: F006S006. Pharmacy with one off opening date set to open
    Given a Changed Event is valid
    And the Changed Event contains a one off opening date thats "Open"
    When the Changed Event is sent for processing with "valid" api key
    Then the opening times changes are marked as valid
    And the processed Changed Request is sent to Dos

@complete @dev
  Scenario: F006S007. Close pharmacy on bank holiday
    Given a Changed Event is valid
    And the Changed Event closes the pharmacy on a bank holiday
    When the Changed Event is sent for processing with "valid" api key
    Then the opening times changes are marked as valid
    And the processed Changed Request is sent to Dos

@complete @mik3
  Scenario: F006S008. Confirm recently added specified opening date can be removed from Dos
    Given a specified opening time Changed Event is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the processed Changed Request is sent to Dos
    And the Changed Request with changed specified date and time is captured by Dos
    And the Changed Event is replayed with the specified opening date deleted
    And the deleted specified date is confirmed removed from Dos
