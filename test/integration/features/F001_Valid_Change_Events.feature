Feature: F001. Ensure valid change events are converted and sent to DoS

  @complete @general
  Scenario Outline: F001SXX1. Changes are processed for acceptable service types
    Given an entry is created in the services table
    And the service "service_type" is set to "<service_type>"
    And the service "service_status" is set to "<status>"
    And the entry is committed to the services table
    And the change event "Postcode" is set to "CT1 1AA"
    When the Changed Event is sent for processing with "valid" api key
    Then the "Postcode" is updated within the DoS DB
    And the service history is updated with the "Postcode"
    And the service history shows "postalcode" change type is "modify"

    Examples:
      | service_type | status |
      | 13           | 1      |
      | 131          | 1      |
      | 132          | 1      |
      | 134          | 1      |
      | 137          | 1      |
      | 148          | 1      |
      | 149          | 1      |

  @complete @general
  Scenario Outline: F001SXX2. Checking invalid service types and statuses variations are not matched
    Given an entry is created in the services table
    And the service "service_type" is set to "<service_type>"
    And the service "service_status" is set to "<status>"
    And the entry is committed to the services table
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-matcher" lambda shows field "report_key" with value "UNMATCHED_PHARMACY"

    Examples:
      | service_type | status |
      | 19           | 1      |
      | 13           | 2      |
      | 13           | 6      |
      | 13           | 7      |
      | 131          | 2      |
      | 132          | 2      |
      | 134          | 2      |
      | 137          | 2      |
      | 13           | 3      |
      | 131          | 3      |
      | 132          | 3      |
      | 134          | 3      |
      | 137          | 3      |
      | 148          | 2      |
      | 148          | 3      |
      | 149          | 2      |
      | 149          | 3      |
      | 148          | 4      |
      | 149          | 4      |
      | 148          | 5      |
      | 149          | 5      |

  @complete @general
  Scenario: F001SXX3. A Changed event with aligned data does not save an update to DoS
    Given a basic service is created
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "message" with value "No changes to save"
    And the service history is not updated

  @complete @general
  Scenario Outline: F001SXX4. A valid change event with changed field is processed and captured by DOS
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

  @complete @general
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

  @complete @general
  Scenario: F001SXX6. A duplicate sequence number is allowed
    Given a basic service is created
    And the ODS has an entry in dynamodb
    When the Changed Event is sent for processing with a duplicate sequence id
    Then the Changed Event is stored in dynamo db
    And the "ingest-change-event" lambda shows field "message" with value "Added record to dynamodb"

  @complete @general
  Scenario Outline: F001SXX7. Changed Event with URL variations is formatted and accepted by Dos
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

  @complete @general
  Scenario Outline: F001SXX8. Changed Event with address line variations is title cased and accepted by Dos
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

  @complete @general
  Scenario: F001SXX9. Changed Event with updated postcode to verify location changes
    Given a basic service is created
    And the change event "Postcode" is set to "PR4 2BE"
    When the Changed Event is sent for processing with "valid" api key
    Then DoS has "KIRKHAM" in the "town" field
    And DoS has "341832" in the "easting" field
    And DoS has "432011" in the "northing" field
    And DoS has "53.781108" in the "latitude" field
    And DoS has "-2.886537" in the "longitude" field

  @complete @general
  Scenario: F001SX10. Locations update check for postcode change
    Given a basic service is created
    And the change event "Postcode" is set to "PR4 2BE"
    When the Changed Event is sent for processing with "valid" api key
    Then the service table has been updated with locations data

  @complete @general
  Scenario: F001SX11. Locations update check service history
    Given a basic service is created
    And the change event "Postcode" is set to "PR4 2BE"
    When the Changed Event is sent for processing with "valid" api key
    Then the service history table has been updated with locations data

  @complete @general
  Scenario: F001SX12. To check the emails sending
    Given a basic service is created
    And the correlation-id is "email"
    And the change event "Address1" is set to "Test Address"
    And a pending entry exists in the changes table for this service
    When the Changed Event is sent for processing with "valid" api key
    Then the s3 bucket contains an email file matching the service uid
    And the changes table shows change is now rejected

  @complete @opening_times
  Scenario: F001SX13. Past Specified Opening Times on Dos are removed and updated
    Given an entry is created in the services table
    And the service is "open" on date "Dec 25 2020"
    And the entry is committed to the services table
    And the specified opening date is set to "future" date
    When the Changed Event is sent for processing with "valid" api key
    Then the DoS service has been updated with the specified date and time is captured by DoS

  @complete @opening_times
  Scenario: F001SX14. All specified opening times are removed from DoS
    Given an entry is created in the services table
    And the service is "open" on date "Dec 25 2020"
    And the entry is committed to the services table
    And the change event is "open" on date "Jan 10 2020"
    When the Changed Event is sent for processing with "valid" api key
    Then the DoS DB has no open date in "2020"

  @complete @opening_times
  Scenario: F001SX15. Empty Specified opening times results in no change and no error
    Given a basic service is created
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "message" with value "No valid pending changes found"

  @complete @opening_times
  Scenario: F001SX16. Empty CE Specified opening times removes all SP times in DoS
    Given an entry is created in the services table
    And the service is "open" on date "Dec 25 2022"
    And the entry is committed to the services table
    And the specified opening date is set to "no" date
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "message" with value "Deleting all specified opening times"

  @complete @opening_times
  Scenario: F001SX17. CE Specified Opening Times with future dates replaces empty Dos SP times
    Given a basic service is created
    And the specified opening date is set to "future" date
    When the Changed Event is sent for processing with "valid" api key
    Then the DoS service has been updated with the specified date and time is captured by DoS

  @complete @general
  Scenario: F001SX18. No Staff field in CE doesn't cause errors
    Given a basic service is created
    And the change event "Postcode" is set to "CT1 1AA"
    And the change event has no staff field
    When the Changed Event is sent for processing with "valid" api key
    Then the "Postcode" is updated within the DoS DB

  @complete @general
  Scenario: F001SX19. Palliative Care Service with changed data flagged (added)
    Given a basic service is created
    And the change event has a palliative care entry
    When the Changed Event is sent for processing with "valid" api key
    Then palliative care is "added" to the service
    And the service history shows "cmssgsdid" change type is "add"

  @complete @general
  Scenario: F001SX20. Palliative Care Service with changed data flagged (removed)
    Given a basic service is created
    And the service in DoS supports palliative care
    When the Changed Event is sent for processing with "valid" api key
    Then palliative care is "removed" to the service
    And the service history shows "cmssgsdid" change type is "delete"

  @complete @general
  Scenario: F001SX21. Palliative Care Service with unchanged data not flagged
    Given a basic service is created
    And the service in DoS supports palliative care
    And the change event has a palliative care entry
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "message" with value "Palliative Care is equal"
    And the service history is not updated

  @complete @validation
  Scenario Outline: F001SX22. Palliative Care. Non primary pharmacy service no check message
    Given an entry is created in the services table
    And the service "service_type" is set to "<service_type>"
    And the entry is committed to the services table
    And the change event has a palliative care entry
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "message" with value "Not suitable for palliative care comparison"
    And the service history is not updated

    Examples:
      | service_type |
      | 131          |
      | 132          |
      | 134          |
      | 137          |

  @complete @general
  Scenario Outline: F001SX23. Blood Pressure Service with changed data flagged (added)
    Given a pharmacy service is created with type "13"
    And an entry is created in the services table with a derivative odscode
    And the service "service_type" is set to "148"
    And the service "service_status" is set to "<service_status>"
    And the entry is committed to the services table
    And the change event has a blood pressure entry
    And the change event "Postcode" is set to "W1A 1AA"
    When the Changed Event is sent for processing with "valid" api key
    Then DoS has "1" in the "status" field
    And the service history shows "cmsorgstatus" change type is "modify"
    And blood pressure Z Code is added to the service
    And the service history shows "cmssgsdid" change type is "add"
    And the "Postcode" is updated within the DoS DB
    And the service history shows "postalcode" change type is "modify"

    Examples:
      | service_status |
      | 2              |
      | 3              |

  @complete @general
  Scenario Outline: F001SX24. Blood Pressure Service with changed data flagged (removed)
    Given an entry is created in the services table
    And the service "service_type" is set to "148"
    And the service "service_status" is set to "1"
    And the entry is committed to the services table
    When the Changed Event is sent for processing with "valid" api key
    Then DoS has "2" in the "status" field
    And the service history shows "cmsorgstatus" change type is "modify"

  @complete @general
  Scenario Outline: F001SX25. Blood Pressure Service with unchanged data (active)
    Given an entry is created in the services table
    And the service "service_type" is set to "148"
    And the service "service_status" is set to "1"
    And the entry is committed to the services table
    And the change event has a blood pressure entry
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "message" with value "Blood Pressure is equal"
    And the service history is not updated

  @complete @general
  Scenario Outline: F001SX26. Blood Pressure Service not updated (inactive)
    Given a pharmacy service is created with type "13"
    And an entry is created in the services table with a derivative service
    And the service "service_type" is set to "148"
    And the service "service_status" is set to "<service_status>"
    And the entry is committed to the services table
    And the change event "Postcode" is set to "W1A 1AA"
    When the Changed Event is sent for processing with "valid" api key
    Then the "postcode" has not been changed in DoS
    And the service history is not updated

    Examples:
      | service_status |
      | 2              |
      | 3              |

  @complete @validation
  Scenario Outline: F001SX27. Blood Pressure not checked for non blood pressure service
    Given an entry is created in the services table
    And the service "service_type" is set to "<service_type>"
    And the entry is committed to the services table
    And the change event has a blood pressure entry
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "message" with value "Not Suitable for blood pressure comparison"
    And the service history is not updated

    Examples:
      | service_type |
      | 13           |
      | 131          |
      | 132          |
      | 134          |
      | 137          |

  @complete @general
  Scenario Outline: F001SX28. Contraception Service with changed data flagged (added)
    Given a pharmacy service is created with type "13"
    And an entry is created in the services table with a derivative odscode
    And the service "service_type" is set to "149"
    And the service "service_status" is set to "<service_status>"
    And the entry is committed to the services table
    And the change event has a contraception entry
    And the change event "Postcode" is set to "W1A 1AA"
    When the Changed Event is sent for processing with "valid" api key
    Then DoS has "1" in the "status" field
    And the service history shows "cmsorgstatus" change type is "modify"
    And contraception Z Code is added to the service
    And the service history shows "cmssgsdid" change type is "add"
    And the "Postcode" is updated within the DoS DB
    And the service history shows "postalcode" change type is "modify"

    Examples:
      | service_status |
      | 2              |
      | 3              |

  @complete @general
  Scenario Outline: F001SX29. Contraception Service with changed data flagged (removed)
    Given an entry is created in the services table
    And the service "service_type" is set to "149"
    And the service "service_status" is set to "1"
    And the entry is committed to the services table
    When the Changed Event is sent for processing with "valid" api key
    Then DoS has "2" in the "status" field
    And the service history shows "cmsorgstatus" change type is "modify"

  @complete @general
  Scenario Outline: F001SX30. Contraception Service with unchanged data (active)
    Given an entry is created in the services table
    And the service "service_type" is set to "149"
    And the service "service_status" is set to "1"
    And the entry is committed to the services table
    And the change event has a contraception entry
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "message" with value "Contraception is equal"
    And the service history is not updated

  @complete @general
  Scenario Outline: F001SX31. Contraception Service not updated (inactive)
    Given a pharmacy service is created with type "13"
    And an entry is created in the services table with a derivative service
    And the service "service_type" is set to "149"
    And the service "service_status" is set to "<service_status>"
    And the entry is committed to the services table
    And the change event "Postcode" is set to "W1A 1AA"
    When the Changed Event is sent for processing with "valid" api key
    Then the "postcode" has not been changed in DoS
    And the service history is not updated

    Examples:
      | service_status |
      | 2              |
      | 3              |

  @complete @validation
  Scenario Outline: F001SX32. Contraception not checked for non contraception service
    Given an entry is created in the services table
    And the service "service_type" is set to "<service_type>"
    And the entry is committed to the services table
    And the change event has a contraception entry
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "message" with value "Not Suitable for contraception comparison"
    And the service history is not updated

    Examples:
      | service_type |
      | 13           |
      | 131          |
      | 132          |
      | 134          |
      | 137          |

  @complete @validation
  Scenario Outline: F001SX33. Test only active or going to active services appear on the hidden or closed report
    Given a pharmacy service is created with type "13"
    And an entry is created in the services table with a derivative odscode
    And the service "service_type" is set to "<service_type>"
    And the service "service_status" is set to "<service_status>"
    And the entry is committed to the services table
    And the change event "OrganisationStatus" is set to "Closed"
    When the Changed Event is sent for processing with "valid" api key
    Then Hidden or Closed logs does not show closed services or not going to active services
    And the service history is not updated

    Examples:
      | service_type | service_status |
      | 148          | 2              |
      | 148          | 3              |
      | 149          | 2              |
      | 149          | 3              |

  @complete @validation
  Scenario Outline: F001SX34. Blood Pressure not checked for non blood pressure service
    Given an entry is created in the services table
    And the service "service_type" is set to "149"
    And the entry is committed to the services table
    And the change event has a contraception entry
    And the change event has a blood pressure entry
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "message" with value "Not Suitable for blood pressure comparison"
    And the service history is not updated

  @complete @validation
  Scenario: F001SX35. Contraception not checked for non contraception service
    Given an entry is created in the services table
    And the service "service_type" is set to "148"
    And the entry is committed to the services table
    And the change event has a contraception entry
    And the change event has a blood pressure entry
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "message" with value "Not Suitable for contraception comparison"
    And the service history is not updated

  @complete @general
  Scenario Outline: F001SX36. Palliative Care remains unchanged with longer than 5 character odscode
    Given a basic service is created with "<odscode_character_length>" character odscode
    And the service in DoS supports palliative care
    And the change event has a palliative care entry
    When the Changed Event is sent for processing with "valid" api key
    Then palliative care is "applied" to the service
    And the "service-sync" lambda shows field "message" with value "No change / Not suitable for palliative care comparison"
    And the service history is not updated

    Examples:
      | odscode_character_length |
      | 6                        |
      | 8                        |


  @complete @validation
  Scenario Outline: F001SX37. Palliative Care remains unchanged with longer than 5 character odscode
    Given a basic service is created with "<odscode_character_length>" character odscode
    And the service in DoS supports palliative care
    And the change event has no palliative care entry
    When the Changed Event is sent for processing with "valid" api key
    Then palliative care is "applied" to the service
    # We need to revisit to the above line to make it more appropriate
    And the "service-sync" lambda shows field "message" with value "No change / Not suitable for palliative care comparison"
    And the service history is not updated

    Examples:
      | odscode_character_length |
      | 6                        |
      | 8                        |

  @complete @validation
  Scenario Outline: F001SX38. Palliative Care remains unchanged with longer than 5 character odscode
    Given a basic service is created with "<odscode_character_length>" character odscode
    And the change event has a palliative care entry
    When the Changed Event is sent for processing with "valid" api key
    Then palliative care is "not applied" to the service
    And the "service-sync" lambda shows field "message" with value "No change / Not suitable for palliative care comparison"
    And the service history is not updated

    Examples:
      | odscode_character_length |
      | 6                        |
      | 8                        |

  @complete @validation
  Scenario Outline: F001SX39. Palliative Care remains unchanged with longer than 5 character odscode
    Given a basic service is created with "<odscode_character_length>" character odscode
    And the change event has no palliative care entry
    When the Changed Event is sent for processing with "valid" api key
    Then palliative care is "not applied" to the service
    And the "service-sync" lambda shows field "message" with value "No change / Not suitable for palliative care comparison"
    And the service history is not updated

    Examples:
      | odscode_character_length |
      | 6                        |
      | 8                        |
