Feature: Event Reciever

  Scenario: A valid change event sent to event receiver
    Given a valid change event
    When a change event is sent to the event receiver
    Then the response has status code "200" with message "Change Event Accepted"

  Scenario: An invalid change event sent to event receiver (change event doesn't represent event send by API Gateway)
    Given an invalid change event with incorrectly formatted event
    When a change event is sent to the event receiver
    Then the response has status code "500" with error message "Unexpected server error"

  Scenario: An invalid change event sent to event receiver with incorrect service type
    Given an invalid change event with incorrect service type
    When a change event is sent to the event receiver
    Then the response has status code "400" with error message "Unexpected Service Type"

  Scenario: An invalid change event sent to event receiver with incorrect service sub type
    Given an invalid change event with incorrect service sub type
    When a change event is sent to the event receiver
    Then the response has status code "400" with error message "Unexpected Service Sub Type"

  Scenario: An invalid change event sent to event receiver with no ods code
    Given an invalid change event with no ods code
    When a change event is sent to the event receiver
    Then the response has status code "400" with error message "Change Event malformed, validation failed"

  Scenario: An invalid change event sent to event receiver with incorrect length odscode
    Given an invalid change event with incorrect length ods code
    When a change event is sent to the event receiver
    Then the response has status code "400" with error message "ODSCode Wrong Length"

  Scenario: An invalid change event sent to event receiver with incorrect type odscode
    Given an invalid change event with incorrect type ods code
    When a change event is sent to the event receiver
    Then the response has status code "400" with error message "Change Event malformed, validation failed"
