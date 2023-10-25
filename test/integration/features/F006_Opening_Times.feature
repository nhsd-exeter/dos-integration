Feature: F006. Opening times

  @complete @no_log_searches
  Scenario: F006SXX1. Confirm actual opening times change for specified date and time is captured by DoS
    Given a basic service is created
    And the change event is "open" on date "Dec 25 2028"
    When the Changed Event is sent for processing with "valid" api key
    Then the DoS service has been updated with the specified date and time is captured by DoS
    And the service history is updated with the "added" specified opening times

  @complete @no_log_searches
  Scenario: F006SXX2. Confirm actual opening times change for standard date and time is captured by Dos
    Given a basic service is created
    And the change event is "open" on "tuesday"
    When the Changed Event is sent for processing with "valid" api key
    Then the DoS service has been updated with the standard days and times is captured by DoS
    And the service history is updated with the "modified" standard opening times

  @complete @no_log_searches
  Scenario: F006SXX3. Pharmacy with one break in opening times
    Given a basic service is created
    And the Changed Event has "1" break in opening times
    When the Changed Event is sent for processing with "valid" api key
    Then opening times with a break are updated in DoS

  @complete @no_log_searches
  Scenario: F006SXX4. Pharmacy with two breaks in opening times
    Given a basic service is created
    And the Changed Event has "2" break in opening times
    When the Changed Event is sent for processing with "valid" api key
    Then opening times with two breaks are updated in DoS

  @complete @no_log_searches
  Scenario: F006SXX6. Confirm recently added specified opening date can be removed from Dos
    Given a basic service is created
    And the change event is "open" on date "Jan 01 2025"
    When the Changed Event is sent for processing with "valid" api key
    Then DoS is open on "Jan 01 2025"
    Given the change event has no specified opening dates
    When the Changed Event is sent for processing with "valid" api key
    Then there is no longer a specified opening on "Jan 01 2025"
    And the service history is updated with the "removed" specified opening times

  @complete @no_log_searches
  Scenario: F006SX7. A recently opened pharmacy on a standard day can be closed
    Given a basic service is created
    And the change event is "open" on "Tuesday"
    When the Changed Event is sent for processing with "valid" api key
    Then the pharmacy is confirmed "open" on "Tuesday"
    Given the change event is "closed" on "Tuesday"
    When the Changed Event is sent for processing with "valid" api key
    Then the pharmacy is confirmed "closed" on "Tuesday"
    And the service history is updated with the "removed" standard opening times

  @complete @cloudwatch_queries
  Scenario: F006SX8. Additional date changes open to closed
    Given an entry is created in the services table
    And the service is "open" on date "Jan 01 2025"
    And the entry is committed to the services table
    And the change event is "closed" on date "Jan 01 2025"
    When the Changed Event is sent for processing with "valid" api key
    Then DoS is closed on "Jan 01 2025"

  @complete @cloudwatch_queries
  Scenario: F006SX9. Additional date changes closed to open
    Given an entry is created in the services table
    And the service is "closed" on date "Jan 01 2025"
    And the entry is committed to the services table
    And the change event is "open" on date "Jan 01 2025"
    When the Changed Event is sent for processing with "valid" api key
    Then DoS is open on "Jan 01 2025"

  @complete @cloudwatch_queries
  Scenario: F006SX10. Additional date changes times changed
    Given an entry is created in the services table
    And the service is "open" on date "Jan 01 2025"
    And the entry is committed to the services table
    And the change event specified opening is "open" from "10:00" to "16:00" on date "Jan 01 2025"
    When the Changed Event is sent for processing with "valid" api key
    Then DoS is open from "10:00" until "16:00" on "Jan 01 2025"
    And the "service-sync" lambda does not show "report_key" with value "BLANK_STANDARD_OPENINGS"
