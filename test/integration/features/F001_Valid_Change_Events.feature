Feature: F001. Ensure valid change events are converted and sent to DOS

  @complete @smoke @no_log_searches
  Scenario: F001S001. A valid change event is processed and accepted by DOS
    Given a Changed Event is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Request is accepted by Dos
    And the Changed Event is stored in dynamo db

  @complete @dev @cloudwatch_queries
  Scenario: F001S002. All received Changed Events are archived in Dynamo DB
    Given a Changed Event is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Event is stored in dynamo db

  @complete @dev @cloudwatch_queries
  Scenario: F001S003. A Changed event with aligned data does not create a CR
    Given a Changed Event is aligned with Dos
    When the Changed Event is sent for processing with "valid" api key
    Then no Changed request is created
    And the Changed Event is stored in dynamo db

  @complete @no_log_searches
  Scenario: F001S004. A valid change event with changed Phone number is processed and captured by DOS
    Given a Changed Event with changed "phone_no" is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Request is accepted by Dos
    And the Changed Request with changed "phone_no" is captured by Dos

  @complete @no_log_searches
  Scenario: F001S005. A valid change event with changed website is processed and captured by DOS
    Given a Changed Event with changed "website" is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Request is accepted by Dos
    And the Changed Request with changed "website" is captured by Dos

  @complete @no_log_searches
  Scenario: F001S006. A valid change event with changed address is processed and captured by DOS
    Given a Changed Event with changed "address" is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Request is accepted by Dos
    And the Changed Request with changed address is captured by Dos

  @complete @dev @cloudwatch_queries
  Scenario: F001S007. A valid change event with special characters is processed by DOS
    Given a Changed Event is valid
    And the website field contains special characters
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Request with special characters is accepted by DOS
    And the Changed Event is stored in dynamo db

@complete @no_log_searches @smoke
  Scenario: F001S008. A valid Dentist change event is processed into DOS
    Given a Dentist Changed Event is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Request is accepted by Dos
    And the Dentist changes with service type id is captured by Dos

@complete @splunk
  Scenario: F001S009. Dentist Hidden reports to Splunk
    Given a Dentist Changed Event is valid
    And the Changed Event has ODS Code "V00393a"
    When the OrganisationStatus is defined as "Hidden"
    And the Changed Event is sent for processing with "valid" api key
    Then the Event Processor logs to splunk with report key "HIDDEN_OR_CLOSED"

@complete @splunk
  Scenario: F001S010. Dentist Invalid Postcode reports to Splunk
    Given a Dentist Changed Event is valid
    And the Changed Event has ODS Code "V00393a"
    When the postcode is invalid
    And the Changed Event is sent for processing with "valid" api key
    Then the Event Processor logs to splunk with report key "INVALID_POSTCODE"

@complete @splunk
  Scenario: F001S011. Dentist Invalid Opening Times reports to Splunk
    Given a Dentist Changed Event is valid
    And the Changed Event has ODS Code "V00393a"
    And a Changed Event where OpeningTimeType is NOT defined correctly
    When the Changed Event is sent for processing with "valid" api key
    Then the Event Processor logs to splunk with report key "INVALID_OPEN_TIMES"

@complete @splunk
  Scenario: F001S012. Dentist Unmatched Service Type reports to Splunk
    Given a Dentist Changed Event is valid
    And the Changed Event has ODS Code "FQG8101"
    When the Changed Event is sent for processing with "valid" api key
    Then the Event Processor logs to splunk with report key "UNMATCHED_SERVICE_TYPE"

@complete @splunk
  Scenario: F001S013. Dentist Unmatched Service reports to Splunk
    Given a Dentist Changed Event is valid
    And the Changed Event has ODS Code "V00393b"
    When the Changed Event is sent for processing with "valid" api key
    Then the Event Processor logs to splunk with report key "UNMATCHED_PHARMACY"
