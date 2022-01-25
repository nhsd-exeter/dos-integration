# Feature: Validate Processor Lambda Logs

# Scenario: Logs pulled from event processor
#   Given a valid change event endpoint
#   Then the event processor logs are generated
#   And the change request has status code "200"

# Scenario: An invalid CE does not create a CR
#   Given a valid change event endpoint
#   When an "invalid" change event with sequence id "001" is processed
#   Then the event processor logs are generated

# Scenario: Status of processor lambda is confirmed
#   Given a valid change event endpoint
#   Then the lambda is confirmed active
