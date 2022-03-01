Feature: F001. Ensure valid change events are converted and sent to DOS

@complete @smoke
  Scenario: F001S001. A valid change event is processed and accepted by DOS
    Given a Changed Event is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the processed Changed Request is sent to Dos
    And the Changed Request is accepted by Dos
    And the Changed Event is stored in dynamo db

@complete @dev
  Scenario: F001S002. All received Changed Events are archived in Dynamo DB
    Given a Changed Event is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Event is stored in dynamo db

@complete @dev
  Scenario: F001S003. A Changed event with aligned data does not create a CR
    Given a Changed Event is aligned with Dos
    When the Changed Event is sent for processing with "valid" api key
    Then no Changed request is created
    And the Changed Event is stored in dynamo db

@complete
  Scenario: F001S004. A valid change event with changed Phone number is processed and captured by DOS
    Given a Changed Event with changed "phone_no" is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the processed Changed Request is sent to Dos
    And the Changed Request with changed "phone_no" is captured by Dos

@complete
  Scenario: F001S005. A valid change event with changed website is processed and captured by DOS
    Given a Changed Event with changed "website" is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the processed Changed Request is sent to Dos
    And the Changed Request with changed "website" is captured by Dos

@complete
  Scenario: F001S006. A valid change event with changed address is processed and captured by DOS
    Given a Changed Event with changed "address" is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the processed Changed Request is sent to Dos
    And the Changed Request with changed address is captured by Dos

@complete @kit
  Scenario: F001S007. A valid change event with special characters is processed by DOS
    Given a Changed Event is valid
    And the address field contains special characters
    When the Changed Event is sent for processing with "valid" api key
    Then the processed Changed Request is sent to Dos
    And the Changed Request with changed address is captured by Dos

@complete @kit
  Scenario: F001S008. Pharmacy with one break in opening times
    Given a Changed Event is valid
    And the Changed Event has one break in opening times
    When the Changed Event is sent for processing with "valid" api key
    Then the processed Changed Request is sent to Dos
    And there are no opening times errors recorded

@complete @kit
  Scenario: F001S010. Pharmacy with two breaks in opening times
    Given a Changed Event is valid
    And the Changed Event has two breaks in opening times
    When the Changed Event is sent for processing with "valid" api key
    Then the processed Changed Request is sent to Dos
    And there are no opening times errors recorded

@complete @kit
  Scenario: F001S011. Pharmacy with one off opening date set to closed
    Given a Changed Event is valid
    And the Changed Event contains a one off opening date thats "Closed"
    When the Changed Event is sent for processing with "valid" api key
    Then the processed Changed Request is sent to Dos
    And there are no opening times errors recorded

@complete @kit
  Scenario: F001S012. Pharmacy with one off opening date set to open
    Given a Changed Event is valid
    And the Changed Event contains a one off opening date thats "Open"
    When the Changed Event is sent for processing with "valid" api key
    Then the processed Changed Request is sent to Dos
    And there are no opening times errors recorded
