Feature: F006. Opening times

  @complete @pharmacy_no_log_searches
  Scenario: F006S001. Confirm actual opening times change for specified date and time is captured by DoS
    Given an opened specified opening time Changed Event is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the DoS service has been updated with the specified date and time is captured by DoS
    And the service history is updated with the "added" specified opening times

  @complete @pharmacy_no_log_searches
  Scenario: F006S002. Confirm actual opening times change for standard date and time is captured by Dos
    Given an opened standard opening time Changed Event is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the DoS service has been updated with the standard days and times is captured by DoS
    And the service history is updated with the "added" standard opening times

  @complete @pharmacy_no_log_searches
  Scenario: F006S003. Pharmacy with one break in opening times
    Given a "pharmacy" Changed Event is aligned with DoS
    And the Changed Event has one break in opening times
    When the Changed Event is sent for processing with "valid" api key
    Then opening times with a break are updated in DoS

  @complete @pharmacy_no_log_searches
  Scenario: F006S004. Pharmacy with two breaks in opening times
    Given a "pharmacy" Changed Event is aligned with DoS
    And the Changed Event has two breaks in opening times
    When the Changed Event is sent for processing with "valid" api key
    Then opening times with two breaks are updated in DoS

  # Refactor to read values from DB to confirm change
  @complete @pharmacy_cloudwatch_queries
  Scenario: F006S005. Pharmacy with one off opening date set to closed
    Given a "pharmacy" Changed Event is aligned with DoS
    And the Changed Event contains a specified opening date that is "Closed"
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda does not show "report_key" with message "INVALID_OPEN_TIMES"

  # Refactor to read values from DB to confirm change
  @complete @pharmacy_cloudwatch_queries
  Scenario: F006S006. A Pharmacy with one off opening date set to open
    Given a "pharmacy" Changed Event is aligned with DoS
    And the Changed Event contains a specified opening date that is "Open"
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda does not show "report_key" with message "INVALID_OPEN_TIMES"

  # Refactor to read values from DB to confirm change
  @complete @pharmacy_cloudwatch_queries
  Scenario: F006S007. Close pharmacy on bank holiday
    Given a "pharmacy" Changed Event is aligned with DoS
    And the Changed Event closes the pharmacy on a bank holiday
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda does not show "report_key" with message "INVALID_OPEN_TIMES"

  @complete @pharmacy_no_log_searches
  Scenario: F006S008. Confirm recently added specified opening date can be removed from Dos
    Given an opened specified opening time Changed Event is valid
    When the Changed Event is sent for processing with "valid" api key
    Then DoS is updated with the new specified opening times
    And the Changed Event is replayed with the specified opening date deleted
    And the deleted specified date is confirmed removed from DoS
    And the service history is updated with the "removed" specified opening times

  @complete @pharmacy_no_log_searches
  Scenario: F006S009. A recently closed pharmacy on a standard day can be opened
    Given a specific Changed Event is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the pharmacy is confirmed "closed" for the standard day in Dos
    And the Changed Event is replayed with the pharmacy now "open"
    And the pharmacy is confirmed "open" for the standard day in Dos

  @complete @pharmacy_no_log_searches
  Scenario: F006S010. A recently opened pharmacy on a standard day can be closed
    Given an opened standard opening time Changed Event is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the pharmacy is confirmed "open" for the standard day in Dos
    And the Changed Event is replayed with the pharmacy now "closed"
    And the pharmacy is confirmed "closed" for the standard day in Dos
    And the service history is updated with the "removed" standard opening times

  @complete @pharmacy_cloudwatch_queries
  Scenario Outline: F006S011. Same dual general opening times
    Given a "pharmacy" Changed Event is aligned with DoS
    And the Changed Event has equal "<opening_type>" values
    When the Changed Event is sent for processing with "valid" api key
    Then the attributes for invalid opening times report is identified in the logs

    Examples:
      | opening_type |
      | General      |
      | Additional   |
