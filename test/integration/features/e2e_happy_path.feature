Feature: E2E Happy Path

  Scenario: Logs pulled from event processor
    Given a valid change event endpoint
    Then the event processor logs are generated
#   And the change request has status code "200"

  Scenario: The status of event processor is confirmed
    Given a valid change event endpoint
    Then the lambda is confirmed active

  Scenario: A "valid" change event sent to event sender
    Given a valid change event endpoint
    When a "valid" change event is sent to the event sender
# Then a change request is received "1" times
#   And the change request has status code "200"

  Scenario: An invalid change event sent to event sender
    Given a valid change event endpoint
    When an "invalid" change event is processed
# Then a change request is received "1" times
#   And the change request has status code "200"

  Scenario: An expected change event sent to event sender
    Given a valid change event endpoint
    When an "expected" change event is sent to the event sender
#   Then a change request is received "1" times
#   And the change request has status code "400"
