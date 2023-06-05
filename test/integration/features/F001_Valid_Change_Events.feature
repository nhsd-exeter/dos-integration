Feature: F001. Ensure valid change events are converted and sent to DOS

  @complete @pharmacy_no_log_searches
  Scenario: F001SXX1. A valid change event is processed and accepted by DOS
    Given a basic service is created
    And the change event "Postcode" is set to "CT1 1AA"
    When the Changed Event is sent for processing with "valid" api key
    Then the "Postcode" is updated within the DoS DB
    And the service history is updated with the "Postcode"
    And the service history shows "postalcode" change type is "modify"

  @complete @dev @pharmacy_cloudwatch_queries
  Scenario: F001SXX2. A Changed event with aligned data does not save an update to DoS
    Given a basic service is created
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "message" with value "No changes to save"
    And the service history is not updated

  @complete @pharmacy_no_log_searches
  Scenario Outline: F001SXX3. A valid change event with changed field is processed and captured by DOS
    Given a basic service is created
    And the "<field>" is changed and is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the "<field>" is updated within the DoS DB
    And the service history is updated with the "<field>"
    And the service history shows change type is "modify"

    Examples:
      | field    |
      | phone_no |
      | website  |
      | address  |

  @complete @pharmacy_no_log_searches
  Scenario Outline: F001SXX5. A valid CE without a contact field
    Given a basic service is created
    And the "<field>" value has been unset
    When the Changed Event is sent for processing with "valid" api key
    Then the "<field>" is updated within the DoS DB
    And the service history is updated with the "<field>"

    Examples:
      | field   |
      | website |
      | phone   |

  @complete @pharmacy_cloudwatch_queries
  Scenario: F001SXX7. A duplicate sequence number is allowed
    Given a basic service is created
    #This below has been updated
    And the ODS has an entry in dynamodb
    When the Changed Event is sent for processing with a duplicate sequence id
    Then the Changed Event is stored in dynamo db
    And the "ingest-change-event" lambda shows field "message" with value "Added record to dynamodb"

  @complete @pharmacy_no_log_searches
  Scenario Outline: F001SXX8 Changed Event with URL variations is formatted and accepted by Dos
    Given a basic service is created
    And the change event "website" is set to "<url>"
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
  Scenario Outline: F001SXX9 Changed Event with address line variations is title cased and accepted by Dos
    Given a basic service is created
    And the change event "Address1" is set to "<address>"
    When the Changed Event is sent for processing with "valid" api key
    Then DoS has "<expected_address>" in the "<field>" field

    Examples: Address variations
      | address             | expected_address               | field   |
      | 5 TESTER WAY        | 5 Tester Way$Nottingham        | address |
      | 1 Test STREET       | 1 Test Street$Nottingham       | address |
      | new test street     | New Test Street$Nottingham     | address |
      | Tester's new street | Testers New Street$Nottingham  | address |
      | new & test avenue   | New and Test Avenue$Nottingham | address |
      | 49a test avenue     | 49A Test Avenue$Nottingham     | address |


  @complete @pharmacy_no_log_searches
  Scenario: F001SX10 Changed Event with updated postcode to verify location changes
    Given a basic service is created
    And the change event "Postcode" is set to "PR4 2BE"
    When the Changed Event is sent for processing with "valid" api key
    Then DoS has "KIRKHAM" in the "town" field
    And DoS has "341832" in the "easting" field
    And DoS has "432011" in the "northing" field
    And DoS has "53.781108" in the "latitude" field
    And DoS has "-2.886537" in the "longitude" field

  @complete @pharmacy_no_log_searches
  Scenario: F001SX11 Locations update check for postcode change
    Given a basic service is created
    And the change event "Postcode" is set to "PR4 2BE"
    When the Changed Event is sent for processing with "valid" api key
    Then the service table has been updated with locations data

  @complete @pharmacy_no_log_searches
  Scenario: F001SX12 Locations update check service history
    Given a basic service is created
    And the change event "Postcode" is set to "PR4 2BE"
    When the Changed Event is sent for processing with "valid" api key
    Then the service history table has been updated with locations data

  @complete @pharmacy_no_log_searches
  Scenario: F001SX15 To check the emails sending
    Given a basic service is created
    And the correlation-id is "email"
    And the change event "Address1" is set to "Test Address"
    And a pending entry exists in the changes table for this service
    When the Changed Event is sent for processing with "valid" api key
    Then the s3 bucket contains an email file matching the service uid
    And the changes table shows change is now rejected

  @complete @pharmacy_cloudwatch_queries
  Scenario: F001SX16 Past Specified Opening Times on Dos are removed and updated
    Given an entry is created in the services table
    And the service is "open" on date "Dec 25 2020"
    And the entry is committed to the services table
    And the specified opening date is set to "future" date
    When the Changed Event is sent for processing with "valid" api key
    Then the DoS service has been updated with the specified date and time is captured by DoS

  @complete @pharmacy_no_log_searches
  Scenario: F001SX17 All specified opening times are removed from DoS
    Given an entry is created in the services table
    And the service is "open" on date "Dec 25 2020"
    And the entry is committed to the services table
    And the change event is "open" on date "Jan 10 2020"
    When the Changed Event is sent for processing with "valid" api key
    Then the DoS DB has no open date in "2020"

  @complete @pharmacy_cloudwatch_queries
  Scenario: F001SX18 Empty Specified opening times results in no change and no error
    Given a basic service is created
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "message" with value "No valid pending changes found"

  @complete @pharmacy_cloudwatch_queries
  Scenario: F001SX19 Empty CE Specified opening times removes all SP times in DoS
    Given an entry is created in the services table
    And the service is "open" on date "Dec 25 2022"
    And the entry is committed to the services table
    And the specified opening date is set to "no" date
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "message" with value "Deleting all specified opening times"

  @complete @pharmacy_cloudwatch_queries
  Scenario: F001SX20 CE Specified Opening Times with future dates replaces empty Dos SP times
    Given a basic service is created
    And the specified opening date is set to "future" date
    When the Changed Event is sent for processing with "valid" api key
    Then the DoS service has been updated with the specified date and time is captured by DoS

  @complete @pharmacy_cloudwatch_queries
  Scenario: F001SX21. No Staff field in CE doesn't cause errors
    Given a basic service is created
    And the change event "Postcode" is set to "CT1 1AA"
    And the change event has no staff field
    When the Changed Event is sent for processing with "valid" api key
    Then the "Postcode" is updated within the DoS DB

  @complete @pharmacy_cloudwatch_queries
  Scenario: F001SX22. Palliative Care Service with unchanged data not flagged
    Given a basic service is created
    And the service in DoS supports palliative care
    And the change event has a palliative care entry
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "message" with value "Palliative Care is equal"
    And the service history is not updated

  @complete @pharmacy_cloudwatch_queries
  Scenario: F001SX23. Palliative Care Service with changed data flagged (removed)
    Given a basic service is created
    And the service in DoS supports palliative care
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "report_key" with value "PALLIATIVE_CARE_NOT_EQUAL"
    And the service history shows "cmssgsdid" change type is "delete"

  @complete @pharmacy_cloudwatch_queries
  Scenario: F001SX24. Palliative Care Service with changed data flagged (added)
    Given a basic service is created
    And the change event has a palliative care entry
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "report_key" with value "PALLIATIVE_CARE_NOT_EQUAL"
    And the service history shows "cmssgsdid" change type is "add"

  @complete @pharmacy_cloudwatch_queries
  Scenario: F001SX25. Palliative Care. Non primary pharmacy service no check message
    Given an entry is created in the services table
    And the service "service_type" is set to "131"
    And the entry is committed to the services table
    And the change event has a palliative care entry
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "message" with value "Not suitable for palliative care comparison"
    And the service history is not updated
