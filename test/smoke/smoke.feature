Feature: Production Smoke Test

  Scenario: Smoke Test
    Given I create a new change event matching DoS
    And I make changes to the change event
    When I run the smoke test
    Then I should see an update to DoS
    And I should see data matching the updated service in DoS
# Given I want to reset the change event
# When I run the smoke test
# Then I should see an update to DoS
# And I should see data matching the original service in DoS
