Feature: Production Smoke Test

  Scenario: Smoke Test
    Given I create a new change event matching DoS
    And I update the change event "address"
    And I update the change event "website"
    And I update the change event "phone"
    And I update the change event "standard_opening_times"
    And I update the change event "specified_opening_times"
    When I run the smoke test
    Then I should see an update to DoS
    And I should see an update to the "address" field and service history in DoS
    And I should see an update to the "website" field and service history in DoS
    And I should see an update to the "phone" field and service history in DoS
    And I should see an update to the "standard_opening_times" field and service history in DoS
    And I should see an update to the "specified_opening_times" field and service history in DoS
    Given I want to reset the change event
    When I run the smoke test
    Then I should see an update to DoS
    And I should see data matching the original service in DoS
