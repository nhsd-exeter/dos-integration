Feature: F001. Ensure valid change events are converted and sent to DOS

@complete @pharmacy_smoke_test @pharmacy_no_log_searches
  Scenario: F001S001. A valid change event is processed and accepted by DOS
    Given a "pharmacy" Changed Event is aligned with Dos
    And the field "Postcode" is set to "CT1 1AA"
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Request is accepted by Dos
    Then the Changed Event is stored in dynamo db

@complete @dev @pharmacy_cloudwatch_queries
  Scenario: F001S002. All received Changed Events are archived in Dynamo DB
    Given a "pharmacy" Changed Event is aligned with Dos
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Event is stored in dynamo db

@complete @dev @pharmacy_cloudwatch_queries
  Scenario: F001S003. A Changed event with aligned data does not create a CR
    Given a "pharmacy" Changed Event is aligned with Dos
    When the Changed Event is sent for processing with "valid" api key
    Then the Event "processor" shows field "message" with message "No changes identified"
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
    Given a "pharmacy" Changed Event is aligned with Dos
    And the field "ContactValue" is set to "https:\/\/www.rowlandspharmacy.co.uk\/test?foo=test"
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Request with special characters is accepted by DOS
    And the Changed Event is stored in dynamo db

@complete @dentist_no_log_searches @dentist_smoke_test
  Scenario: F001S008. A valid Dentist change event is processed into DOS
    Given a "dentist" Changed Event is aligned with Dos
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Request is accepted by Dos
    And the Dentist changes with service type id is captured by Dos

@complete @pharmacy_smoke_test @pharmacy_no_log_searches
  Scenario: F001S009. A valid change with website removal is processed by dos
    Given a Changed Event to unset "website"
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Request is accepted by DoS with "website" deleted
    And the Changed Event is stored in dynamo db

@complete @pharmacy_smoke_test @pharmacy_no_log_searches
  Scenario: F001S010. A valid change with phone removal is processed by dos
    Given a Changed Event to unset "phone"
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Request is accepted by Dos with "phone" deleted
    And the Changed Event is stored in dynamo db

@complete @dev @pharmacy_cloudwatch_queries
  Scenario: F001S011. No CR created with a None value as phone data
    Given a Changed Event with a "None" value for "phone_no"
    When the Changed Event is sent for processing with "valid" api key
    Then the Event "processor" shows field "message" with message "No changes identified"

@complete @dev @pharmacy_cloudwatch_queries
  Scenario: F001S012. No CR created with empty phone data
    Given a Changed Event with a "''" value for "phone_no"
    When the Changed Event is sent for processing with "valid" api key
    Then the Event "processor" shows field "message" with message "No changes identified"

@complete @dev @pharmacy_cloudwatch_queries
  Scenario: F001S013. No CR created with a None value as website data
    Given a Changed Event with a "None" value for "website"
    When the Changed Event is sent for processing with "valid" api key
    Then the Event "processor" shows field "message" with message "No changes identified"

@complete @dev @pharmacy_cloudwatch_queries
  Scenario: F001S014. No CR created with empty website data
    Given a Changed Event with a "''" value for "website"
    When the Changed Event is sent for processing with "valid" api key
    Then the Event "processor" shows field "message" with message "No changes identified"

@complete @dev @pharmacy_no_log_searches
  Scenario: F001S015. No CR created with a change of public name data
    Given a Changed Event with value "New Pharmacy" for "organisation_name"
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Event with changed "public_name" is not captured by Dos
