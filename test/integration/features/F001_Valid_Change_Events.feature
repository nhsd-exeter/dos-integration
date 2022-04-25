Feature: F001. Ensure valid change events are converted and sent to DOS

@complete @smoke @pharmacy_no_log_searches
  Scenario: F001S001. A valid change event is processed and accepted by DOS
    Given a Changed Event is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Request is accepted by Dos
    And the Changed Event is stored in dynamo db

@complete @dev @pharmacy_cloudwatch_queries
  Scenario: F001S002. All received Changed Events are archived in Dynamo DB
    Given a Changed Event is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Event is stored in dynamo db

@complete @dev @pharmacy_cloudwatch_queries
  Scenario: F001S003. A Changed event with aligned data does not create a CR
    Given a Changed Event is aligned with Dos
    When the Changed Event is sent for processing with "valid" api key
    Then no Changed request is created
    And the Changed Event is stored in dynamo db

@complete @pharmacy_no_log_searches
  Scenario: F001S004. A valid change event with changed Phone number is processed and captured by DOS
    Given a Changed Event with changed "phone_no" is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Request is accepted by Dos
    And the Changed Request with changed "phone_no" is captured by Dos

@complete @pharmacy_no_log_searches
  Scenario: F001S005. A valid change event with changed website is processed and captured by DOS
    Given a Changed Event with changed "website" is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Request is accepted by Dos
    And the Changed Request with changed "website" is captured by Dos

@complete @pharmacy_no_log_searches
  Scenario: F001S006. A valid change event with changed address is processed and captured by DOS
    Given a Changed Event with changed "address" is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Request is accepted by Dos
    And the Changed Request with changed address is captured by Dos

@complete @dev @pharmacy_cloudwatch_queries
  Scenario: F001S007. A valid change event with special characters is processed by DOS
    Given a Changed Event is valid
    And the website field contains special characters
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Request with special characters is accepted by DOS
    And the Changed Event is stored in dynamo db

@complete @dentist_no_log_searches @smoke
  Scenario: F001S008. A valid Dentist change event is processed into DOS
    Given a Dentist Changed Event is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Request is accepted by Dos
    And the Dentist changes with service type id is captured by Dos

@complete @dev @pharmacy_cloudwatch_queries
  Scenario Outline: F001S009. No CR created without phone data
    Given a Changed Event with no value "<data>" for "<contact_field>"
    When the Changed Event is sent for processing with "valid" api key
    Then the Event "processor" does not show "message" with message "phone is not equal"

    Examples: With the contact fields being empty in DOS, these phone inputs from NHS Uk CE should not trigger a CR
      | contact_field | data |
      | phone_no | None |

@complete @dev @pharmacy_cloudwatch_queries
  Scenario Outline: F001S010. No CR created without website data
    Given a Changed Event with no value "<data>" for "<contact_field>"
    When the Changed Event is sent for processing with "valid" api key
    Then the Event "processor" does not show "message" with message "website is not equal"

    Examples: With the website contact fields being empty in DOS, these inputs from NHS Uk CE should not trigger a CR
      | contact_field | data |
      | website | None |
