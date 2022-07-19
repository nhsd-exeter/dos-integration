Feature: F001. Ensure valid change events are converted and sent to DOS

  @complete @pharmacy_smoke_test @pharmacy_no_log_searches
  Scenario: F001S001. A valid change event is processed and accepted by DOS
    Given a "pharmacy" Changed Event is aligned with Dos
    And the field "Postcode" is set to "CT1 1AA"
    When the Changed Event is sent for processing with "valid" api key
    Then the Change Request is accepted by Dos

  @complete @dev @pharmacy_cloudwatch_queries
  Scenario: F001S002. A Changed event with aligned data does not create a CR
    Given a "pharmacy" Changed Event is aligned with Dos
    When the Changed Event is sent for processing with "valid" api key
    Then the Event "processor" shows field "message" with message "No changes identified"

@complete @pharmacy_no_log_searches
  Scenario Outline: F001S003. A valid change event with changed field is processed and captured by DOS
    Given a Changed Event with changed "<field>" is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the Change Request is accepted by Dos
    And the Change Request with changed "<field>" is captured by Dos

    Examples:
      | field    |
      | phone_no |
      | website  |
      | address  |

  @complete @dentist_no_log_searches @dentist_smoke_test
  Scenario: F001S004. A valid Dentist change event is processed into DOS
    Given a "dentist" Changed Event is aligned with Dos
    When the Changed Event is sent for processing with "valid" api key
    Then the Change Request is accepted by Dos
    And the Dentist changes with service type id is captured by Dos

  @complete @pharmacy_smoke_test @pharmacy_no_log_searches
  Scenario Outline: F001S005. A valid change with field removal is processed by dos
    Given a Changed Event to unset "<field>"
    When the Changed Event is sent for processing with "valid" api key
    Then the Change Request is accepted by DoS with "<field>" deleted

    Examples:
      | field   |
      | website |
      | phone   |

  @complete @pharmacy_no_log_searches
  Scenario Outline: F001S006. No CR created when CE phone website value is null and public name value set
    Given a Changed Event with a "<value>" value for "<field>"
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Event with changed "<field>" is not captured by Dos

    Examples:
      | field             | value        |
      | phone_no          | None         |
      | phone_no | ''   |
      | website  | None |
      | website           | ''           |
      | organisation_name | New Pharmacy |

  @complete @pharmacy_cloudwatch_queries
  Scenario: F001S007. A duplicate sequence number is allowed
    Given an ODS has an entry in dynamodb
    When the Changed Event is sent for processing with a duplicate sequence id
    Then the Changed Event is stored in dynamo db
    And the Event "processor" shows field "message" with message "Added record to dynamodb"

@complete @pharmacy_no_log_searches
  Scenario Outline: F001S008 Changed Event with URL variations is formatted and accepted by Dos
    Given a Changed Event with changed "<url>" variations is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the Change Request with formatted "<expected_url>" is captured by Dos

    Examples: Web address variations
      | url                                              | expected_url                                     |
      | https://www.Test.com                             | https://www.test.com                             |
      | https://www.TEST.Com                             | https://www.test.com                             |
      | https://www.Test.com/TEST                        | https://www.test.com/TEST                        |
      | http://www.TestChemist.co.uk                     | http://www.testchemist.co.uk                     |
      | https://Testchemist.co.Uk                        | https://testchemist.co.uk                        |
      | https://Www.testpharmacy.co.uk                   | https://www.testpharmacy.co.uk                   |
      | https://www.rowlandspharmacy.co.uk/test?foo=test | https://www.rowlandspharmacy.co.uk/test?foo=test |

@complete @pharmacy_no_log_searches
  Scenario Outline: F001S009 Changed Event with address line variations is title cased and accepted by Dos
    Given a Changed Event with "<address>" is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the Change Request with title cased "<expected_address>" is captured by Dos

    Examples: Address variations
      | address             | expected_address    |
      | 5 TESTER WAY        | 5 Tester Way        |
      | 1 Test STREET       | 1 Test Street       |
      | new test street     | New Test Street     |
      | Tester's new street | Testers New Street  |
      | new & test avenue   | New and Test Avenue |
      | 49a test avenue | 49A Test Avenue |
