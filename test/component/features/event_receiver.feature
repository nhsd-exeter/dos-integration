Feature: Event Reciever

  Scenario: A valid change event sent to event receiver
    Given a valid change event
    When a change event is sent to the event receiver
    Then the change event has status code "200"

  # Scenario: An invalid change event sent to event receiver
  #   Given an invalid change event
  #   When a change event is sent to the event receiver
  #   Then the change event has status code "404"
