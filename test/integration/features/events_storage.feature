# Feature: Dynamo DB Events Store

# Scenario: Change Events are stored in dynamo db
#   Given a valid change event endpoint
#   When a "valid" change event with sequence id "78901" is sent to the event procesor
#   Then the "valid" payload with sequence id "78901" is stored in dynamo db

# Scenario: DynamoDB table stores Change Events with Changes
#   Given I input a Change Event with valid changes to one or more services
#   When it is processed by the Event Processor
#   Then a new entry is added to the DynamoDB tables with Event Data
#   And a sequence ID is recorded
#   And the sequence ID is higher than all other sequence IDs associate with this ODS code.

# Scenario: DynamoDB tables stores Changes Events with no Changes
#   Given I input a valid Change Event with no changes to one or more services
#   When it is processed by the Event Processor
#   Then a new entry is added to the DynamoDB tables with Event Data
#   And a sequence ID is recorded
#   And the sequence ID is higher than all other sequence IDs associate with this ODS code.

# Scenario: Invalid Sequence ID
#   Given I input a valid Change Event with valid changes to one or more services
#   And the Sequence ID is lower than the current latest Sequence ID
#   When it is processed by the Event Processor
#   Then the Change Event is discarded as having an invalid Sequence ID

# Scenario: DynamoDB tables stores invalid Change Events
#   Given I input an invalid Change Event
#   When it is processed by the Event Processor
#   Then a new entry is added to the DynamoDB tables with Event Data
#   And a sequence ID is recorded
