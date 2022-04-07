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

@complete @no_log_searches
  Scenario: F001S008. A valid Dentist change event is processed into DOS
    Given a Dentist Changed Event is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Request is accepted by Dos
    And the Dentist changes with service type id is captured by Dos

@complete @dev
  Scenario: F001S009. A valid change event with 9 digit dentist code is processed by DOS
    Given a new dentist Changed Event is valid
    And the Changed Event has ODS Code "V0393a000"
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Event finds a matching dentist with ods "V00393a"
    And the Event Sender sends the ods "V00393a"

@complete @dev
  Scenario: F001S010. A valid change event with 10 digit dentist code is processed by DOS
    Given a new dentist Changed Event is valid
    And the Changed Event has ODS Code "V00393a000"
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Event finds a matching dentist with ods "V00393a"
    And the Event Sender sends the ods "V00393a"

@complete @dev
  Scenario: F001S011. A valid change event with 6 digit dentist code is processed by DOS
    Given a new dentist Changed Event is valid
    And the Changed Event has ODS Code "V0393a"
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Event finds a matching dentist with ods "V00393a"
    And the Event Sender sends the ods "V00393a"
