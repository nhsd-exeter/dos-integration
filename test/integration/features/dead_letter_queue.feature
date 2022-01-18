# Feature: Dead Letter Queue tests

#   Scenario: New Message added to DLQ
#     Given I input a Change Event with invalid changes to one or more services
#     When it is received by the Event Processor
#     Then the message is rejected and gets added to the DLQ
#     And the message is removed from the queue
#     And a message is sent to Slack

#   Scenario: Invalid/Valid mix received
#     Given I input a Change Event with invalid changes to one or more services
#     And I input a Change Event with valid changes to one or more services
#     When it is received by the Event Processor
#     Then the first message is rejected and gets added to the DLQ
#     And the first message is removed from the queue
#     And the second message is processed successfully
#     And the second message is not added to the DLQ

#   Scenario: Splunk logs DLQ entries
#     Given I input a Change Event with invalid changes to one or more services
#     When it is received by the Event Processor
#     Then Splunk logs report that the DLQ lambda has been invoked
