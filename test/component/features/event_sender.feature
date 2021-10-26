Feature: Event Sender

  Scenario: A valid change request sent to event sender
    Given a valid change request endpoint
    When a change request is sent to the event sender
    Then a change request is received once
    Then the expected change is received
