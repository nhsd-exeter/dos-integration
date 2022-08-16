Feature: F001. Ensure valid change events are converted and sent to DOS

  @complete @pharmacy_smoke_test @pharmacy_no_log_searches
  Scenario: F001S001. A valid change event is processed and accepted by DOS
    Given a "pharmacy" Changed Event is aligned with DoS
    And the field "Postcode" is set to "CT1 1AA"
    When the Changed Event is sent for processing with "valid" api key
    Then the "Postcode" is updated within the DoS DB
    And the service history is updated with the "Postcode"
    And the service history shows change type is "modify"

  @complete @dev @pharmacy_cloudwatch_queries
  Scenario: F001S002. A Changed event with aligned data does not save an update to DoS
    Given a "pharmacy" Changed Event is aligned with DoS
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "message" with message "No changes to save"

  @complete @pharmacy_no_log_searches
  Scenario Outline: F001S003. A valid change event with changed field is processed and captured by DOS
    Given a "pharmacy" Changed Event is aligned with DoS
    And the "<field>" is changed and is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the "<field>" is updated within the DoS DB
    And the service history is updated with the "<field>"

    Examples:
      | field    |
      | phone_no |
      | website  |
      | address  |

  # @complete @broken @dentist_no_log_searches @dentist_smoke_test
  # Scenario: F001S004. A valid Dentist change event is processed into DOS
  #   Given a "dentist" Changed Event is aligned with DoS
  #   When the Changed Event is sent for processing with "valid" api key
  #   Then the Change Request is accepted by Dos
  #   And the Dentist changes with service type id is captured by Dos

  @complete @pharmacy_smoke_test @pharmacy_no_log_searches
  Scenario Outline: F001S005. A valid CE without a contact field
    Given a Changed Event to unset "<field>"
    When the Changed Event is sent for processing with "valid" api key
    Then the "<field>" is updated within the DoS DB
    And the service history is updated with the "<field>"

    Examples:
      | field   |
      | website |
      | phone   |

  # This is broken as DoS fields are already null and therefore can't be set to null
  # @complete @broken @pharmacy_no_log_searches @wip
  # Scenario Outline: F001S006. No value means that the field is removed in DoS
  #   Given a Changed Event with a "<value>" value for "<field>"
  #   When the Changed Event is sent for processing with "valid" api key
  #   Then the "<field>" is updated within the DoS DB

  #   Examples:
  #     | field    | value |
  #     | phone_no | None  |
  #     | phone_no | ''    |
  #     | website  | None  |
  #     | website  | ''    |

  @complete @pharmacy_cloudwatch_queries
  Scenario: F001S007. A duplicate sequence number is allowed
    Given an ODS has an entry in dynamodb
    When the Changed Event is sent for processing with a duplicate sequence id
    Then the Changed Event is stored in dynamo db
    And the "service-matcher" lambda shows field "message" with message "Added record to dynamodb"

  @complete @pharmacy_no_log_searches
  Scenario Outline: F001S008 Changed Event with URL variations is formatted and accepted by Dos
    Given a Changed Event with changed "<url>" variations is valid
    When the Changed Event is sent for processing with "valid" api key
    Then DoS has "<expected_url>" in the "<field>" field

    Examples: Web address variations
      | url                                              | expected_url                                     | field   |
      | https://www.Test.com                             | https://www.test.com                             | website |
      | https://www.TEST.Com                             | https://www.test.com                             | website |
      | https://www.Test.com/TEST                        | https://www.test.com/TEST                        | website |
      | http://www.TestChemist.co.uk                     | http://www.testchemist.co.uk                     | website |
      | https://Testchemist.co.Uk                        | https://testchemist.co.uk                        | website |
      | https://Www.testpharmacy.co.uk                   | https://www.testpharmacy.co.uk                   | website |
      | https://www.rowlandspharmacy.co.uk/test?foo=test | https://www.rowlandspharmacy.co.uk/test?foo=test | website |

  @complete @pharmacy_no_log_searches
  Scenario Outline: F001S009 Changed Event with address line variations is title cased and accepted by Dos
    Given a Changed Event with "<address>" is valid
    When the Changed Event is sent for processing with "valid" api key
    Then DoS has "<expected_address>" in the "<field>" field

    Examples: Address variations
      | address             | expected_address    | field   |
      | 5 TESTER WAY        | 5 Tester Way        | address |
      | 1 Test STREET       | 1 Test Street       | address |
      | new test street     | New Test Street     | address |
      | Tester's new street | Testers New Street  | address |
      | new & test avenue   | New and Test Avenue | address |
      | 49a test avenue     | 49A Test Avenue     | address |
