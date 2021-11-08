Feature: Event Reciever

  Scenario: A valid change event sent to event receiver
    Given a valid change event
    When a change event is sent to the event receiver
    Then the response has status code "200" with message "Change Event Accepted"
    And the response is logged with status code "200" and message "Change Event Accepted"

  Scenario: An invalid change event sent to event receiver
    Given an invalid change event with incorrectly formatted event
    When a change event is sent to the event receiver
    Then the response has status code "400" with error message "Change Event incorrect format"
    And the response is logged with status code "400" and message "Change Event incorrect format"

  Scenario:
    Given an invalid change event with incorrect service type
    When a change event is sent to the event receiver
    Then the response has status code "400" with error message "Unexpected Service Type"
    And the response is logged with status code "400" and message "Unexpected Service Type"

  Scenario:
    Given an invalid change event with incorrect sub service type
    When a change event is sent to the event receiver
    Then the response has status code "400" with error message "Unexpected Service Sub Type"
    And the response is logged with status code "400" and message "Unexpected Service Sub Type"

  Scenario:
    Given an invalid change event with no ods code
    When a change event is sent to the event receiver
    Then the response has status code "400" with error message "Event malformed, validation failed"
    And the response is logged with status code "400" and message "Event malformed, validation failed"

  Scenario:
    Given an invalid change event with incorrect length ods code
    When a change event is sent to the event receiver
    Then the response has status code "400" with error message "ODSCode Wrong Length"
    And the response is logged with status code "400" and message "ODSCode Wrong Length"

  Scenario:
    Given an invalid change event with incorrect type ods code
    When a change event is sent to the event receiver
    Then the response has status code "400" with error message "Event malformed, validation failed"
    And the response is logged with status code "400" and message "Event malformed, validation failed"
