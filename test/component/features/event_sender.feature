Feature: Event Sender

  Scenario: A valid change request sent to event sender
    Given a valid change request endpoint
    When a "valid" change request is sent to the event sender
    Then a change request is received "1" times
    Then the change request has status code "200"
    Then the response "Success" is logged and has status code "200"

  Scenario: An invalid change request sent to event sender
    Given a valid change request endpoint
    When a "invalid" change request is sent to the event sender
    Then a change request is received "1" times
    Then the change request has status code "400"
    Then the response "Failure" is logged and has status code "400"
