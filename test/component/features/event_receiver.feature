Feature: Event Reciever

  Scenario: A valid change event sent to event receiver
    Given a valid change event
    When a change event is sent to the event receiver
    Then the change event has status code "200"
    And the response body contains "Change Event Accepted"

  Scenario: An invalid change event sent to event receiver
    Given an invalid change event incorrectly formatted
    When a change event is sent to the event receiver
    Then the change event has status code "400"
    And the response body contains "Invalid Change Event"
