# Feature: Test Event Sender Features

#   Scenario: A valid change request sent to event sender
#     Given a valid change request endpoint
#     When a "valid" change request is sent to the event sender
#     Then a change request is received "1" times
#     And the change request has status code "200"
#     And the successful response is logged with status code "200"

#   Scenario: An invalid change request sent to event sender
#     Given a valid change request endpoint
#     When a "invalid" change request is sent to the event sender
#     Then a change request is received "1" times
#     And the change request has status code "400"
#     And the failure response is logged with status code "400"

#   Scenario: Proccessed Valid CE are sent to the Sender lambda as CR
#     Given a valid change event endpoint
#     When a "valid" change event with sequence id "101" is sent to the event procesor
#     Then the event sender logs are generated
