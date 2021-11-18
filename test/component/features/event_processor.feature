Feature: Event Processor

Scenario: A change event is passed to the event processor which doesn't equal DoS services
  Given a change event that is for a service is the different from a DoS service
  When the change event is sent to the event processor
  Then the change event that is for a service is the different from a DoS service is logged
  And the change request is produced and logged

Scenario: A change event is passed to the event processor which does equal a DoS service
  Given a change event that is for a service is the same as a DoS service
  When the change event is sent to the event processor
  Then the change event that is for a service is the same as a DoS service
  And no change request is produced

Scenario: A change event is passed to the event processor which contains a service which isn't in DoS
  Given a change event for a service that doesn't exist in DoS
  When the change event is sent to the event processor
  Then the change event for a service that doesn't exist in DoS is logged
  And no change request is produced
