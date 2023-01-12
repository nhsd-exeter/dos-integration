Feature: F006. Opening times

  @complete @pharmacy_no_log_searches
  Scenario: F006SXX1. Confirm actual opening times change for specified date and time is captured by DoS
    Given a basic service is created
    And the change event is "open" on date "Dec 25 2028"
    When the Changed Event is sent for processing with "valid" api key
    Then the DoS service has been updated with the specified date and time is captured by DoS
    And the service history is updated with the "added" specified opening times

  @complete @pharmacy_no_log_searches
  Scenario: F006SXX2. Confirm actual opening times change for standard date and time is captured by Dos
    Given a basic service is created
    And the change event is "open" on "tuesday"
    When the Changed Event is sent for processing with "valid" api key
    Then the DoS service has been updated with the standard days and times is captured by DoS
    And the service history is updated with the "modified" standard opening times

  @complete @pharmacy_no_log_searches
  Scenario: F006SXX3. Pharmacy with one break in opening times
    Given a basic service is created
    And the Changed Event has "1" break in opening times
    When the Changed Event is sent for processing with "valid" api key
    Then opening times with a break are updated in DoS

  @complete @pharmacy_no_log_searches
  Scenario: F006SXX4. Pharmacy with two breaks in opening times
    Given a basic service is created
    And the Changed Event has "2" break in opening times
    When the Changed Event is sent for processing with "valid" api key
    Then opening times with two breaks are updated in DoS

  # Refactor to read values from DB to confirm change
  @complete @pharmacy_cloudwatch_queries
  Scenario: F006SXX5. Pharmacy with one off opening date set to closed
    Given a basic service is created
    And the change event is "closed" on date "Dec 25 2025"
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda does not show "report_key" with message "INVALID_OPEN_TIMES"

  # Refactor to read values from DB to confirm change
  @complete @pharmacy_cloudwatch_queries
  Scenario: F006SXX6. A Pharmacy with one off opening date set to open
    Given a basic service is created
    And the change event is "open" on date "Dec 25 2025"
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda does not show "report_key" with message "INVALID_OPEN_TIMES"

  # Refactor to read values from DB to confirm change
  @complete @pharmacy_cloudwatch_queries
  Scenario: F006SXX7. Close pharmacy on bank holiday
    Given a basic service is created
    And the change event is "closed" on date "Jan 1 2025"
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda does not show "report_key" with message "INVALID_OPEN_TIMES"

  @complete @pharmacy_no_log_searches
  Scenario: F006SXX8. Confirm recently added specified opening date can be removed from Dos
    Given a basic service is created
    And the change event is "open" on date "Jan 01 2025"
    When the Changed Event is sent for processing with "valid" api key
    Then DoS is open on "Jan 01 2025"
    Given the change event has no specified opening dates
    When the Changed Event is sent for processing with "valid" api key
    Then there is no longer a specified opening on "Jan 01 2025"
    And the service history is updated with the "removed" specified opening times

  @complete @pharmacy_no_log_searches
  Scenario: F006SXX9. A recently closed pharmacy on a standard day can be opened
    Given a basic service is created
    And the change event is "closed" on "Monday"
    When the Changed Event is sent for processing with "valid" api key
    Then the pharmacy is confirmed "closed" on "Monday"
    And the service history is updated with the "removed" standard opening times
    Given the change event is "open" on "Monday"
    When the Changed Event is sent for processing with "valid" api key
    Then the pharmacy is confirmed "open" on "Monday"
    And the service history is updated with the "modified" standard opening times

  @complete @pharmacy_no_log_searches
  Scenario: F006SX10. A recently opened pharmacy on a standard day can be closed
    Given a basic service is created
    And the change event is "open" on "Tuesday"
    When the Changed Event is sent for processing with "valid" api key
    Then the pharmacy is confirmed "open" on "Tuesday"
    Given the change event is "closed" on "Tuesday"
    When the Changed Event is sent for processing with "valid" api key
    Then the pharmacy is confirmed "closed" on "Tuesday"
    And the service history is updated with the "removed" standard opening times

  @complete @pharmacy_cloudwatch_queries
  Scenario: F006SX11. Same dual general opening times
    Given an entry is created in the services table
    And the service is "open" on "Monday"
    And the service is "open" on "Monday"
    And the entry is committed to the services table
    When the Changed Event is sent for processing with "valid" api key
    Then the attributes for invalid opening times report is identified in the logs

  @complete @pharmacy_cloudwatch_queries
  Scenario: F006SX12. Additional date changes open to closed
    Given an entry is created in the services table
    And the service is "open" on date "Jan 01 2025"
    And the entry is committed to the services table
    And the change event is "closed" on date "Jan 01 2025"
    When the Changed Event is sent for processing with "valid" api key
    Then DoS is closed on "Jan 01 2025"

  @complete @pharmacy_cloudwatch_queries
  Scenario: F006SX13. Additional date changes closed to open
    Given an entry is created in the services table
    And the service is "closed" on date "Jan 01 2025"
    And the entry is committed to the services table
    And the change event is "open" on date "Jan 01 2025"
    When the Changed Event is sent for processing with "valid" api key
    Then DoS is open on "Jan 01 2025"
