Feature: F007. Report Logging

  @complete @reporting
  Scenario: F007SX01. Check for Invalid Open Times log
    Given an entry is created in the services table
    And the service is "open" on "Monday"
    And the service is "open" on "Monday"
    And the entry is committed to the services table
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-matcher" lambda shows field "report_key" with value "INVALID_OPEN_TIMES"
    And "nhsuk_odscode" attribute is identified in the "INVALID_OPEN_TIMES" report in "service-matcher" logs
    And "nhsuk_organisation_name" attribute is identified in the "INVALID_OPEN_TIMES" report in "service-matcher" logs
    And "nhsuk_open_times_payload" attribute is identified in the "INVALID_OPEN_TIMES" report in "service-matcher" logs
    And "dos_service_type_name" attribute is identified in the "INVALID_OPEN_TIMES" report in "service-matcher" logs
    And "dos_services" attribute is identified in the "INVALID_OPEN_TIMES" report in "service-matcher" logs

  @complete @reporting
  Scenario Outline: F007SX02. Pharmacy with one off opening date set to closed
    Given a basic service is created
    And the change event is "<open_or_closed>" on date "<date>"
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda does not show "report_key" with value "INVALID_OPEN_TIMES"

    Examples:
      | open_or_closed | date        |
      | closed         | Dec 25 2025 |
      | open           | Dec 25 2025 |

  @complete @reporting
  Scenario: F007SX03 Check for generic change event error log
    Given a basic service is created
    And the change event "website" is set to "test@test.com"
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "report_key" with value "GENERIC_CHANGE_EVENT_ERROR"
    And "ods_code" attribute is identified in the "GENERIC_CHANGE_EVENT_ERROR" report in "service-sync" logs
    And "error_reason" attribute is identified in the "GENERIC_CHANGE_EVENT_ERROR" report in "service-sync" logs
    And "error_info" attribute is identified in the "GENERIC_CHANGE_EVENT_ERROR" report in "service-sync" logs
    And "dos_region" attribute is identified in the "GENERIC_CHANGE_EVENT_ERROR" report in "service-sync" logs

  @complete @reporting
  Scenario: F007SX04 Check for services with generic bank holiday openings log
    Given a basic service is created
    And the change event "ODSCode" is set to "FJQ49"
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "report_key" with value "GENERIC_BANK_HOLIDAY"
    And "nhsuk_odscode" attribute is identified in the "GENERIC_BANK_HOLIDAY" report in "service-sync" logs
    And "nhsuk_organisation_name" attribute is identified in the "GENERIC_BANK_HOLIDAY" report in "service-sync" logs
    And "dos_service_uid" attribute is identified in the "GENERIC_BANK_HOLIDAY" report in "service-sync" logs
    And "dos_service_name" attribute is identified in the "GENERIC_BANK_HOLIDAY" report in "service-sync" logs
    And "dos_service_type_name" attribute is identified in the "GENERIC_BANK_HOLIDAY" report in "service-sync" logs
    And "bank_holiday_opening_times" attribute is identified in the "GENERIC_BANK_HOLIDAY" report in "service-sync" logs
    And "nhsuk_parent_org" attribute is identified in the "GENERIC_BANK_HOLIDAY" report in "service-sync" logs
    And "dos_region" attribute is identified in the "GENERIC_BANK_HOLIDAY" report in "service-sync" logs

  @complete @reporting
  Scenario: F007SX05 Check for Unmatched Pharmacy Report log
    Given a basic service is created
    And the change event "ODSCode" is set to "FXXX1"
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-matcher" lambda shows field "report_key" with value "UNMATCHED_PHARMACY"
    And "nhsuk_odscode" attribute is identified in the "UNMATCHED_PHARMACY" report in "service-matcher" logs
    And "nhsuk_organisation_name" attribute is identified in the "UNMATCHED_PHARMACY" report in "service-matcher" logs
    And "nhsuk_organisation_typeid" attribute is identified in the "UNMATCHED_PHARMACY" report in "service-matcher" logs
    And "nhsuk_organisation_subtype" attribute is identified in the "UNMATCHED_PHARMACY" report in "service-matcher" logs
    And "nhsuk_organisation_status" attribute is identified in the "UNMATCHED_PHARMACY" report in "service-matcher" logs
    And "nhsuk_address1" attribute is identified in the "UNMATCHED_PHARMACY" report in "service-matcher" logs
    And "nhsuk_city" attribute is identified in the "UNMATCHED_PHARMACY" report in "service-matcher" logs
    And "nhsuk_postcode" attribute is identified in the "UNMATCHED_PHARMACY" report in "service-matcher" logs
    And "nhsuk_parent_organisation_name" attribute is identified in the "UNMATCHED_PHARMACY" report in "service-matcher" logs
    And the service history is not updated

  @complete @reporting
  Scenario: F007SX06 Check for Blank Opening Times Report log
    Given an entry is created in the services table
    And the service is "open" on "Monday"
    And the entry is committed to the services table
    And the Changed Event has blank opening times
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "report_key" with value "BLANK_STANDARD_OPENINGS"
    And "nhsuk_odscode" attribute is identified in the "BLANK_STANDARD_OPENINGS" report in "service-sync" logs
    And "dos_service_name" attribute is identified in the "BLANK_STANDARD_OPENINGS" report in "service-sync" logs
    And "dos_region" attribute is identified in the "BLANK_STANDARD_OPENINGS" report in "service-sync" logs
    And "dos_service_uid" attribute is identified in the "BLANK_STANDARD_OPENINGS" report in "service-sync" logs
    And "dos_service_type_name" attribute is identified in the "BLANK_STANDARD_OPENINGS" report in "service-sync" logs
    And the service history is not updated

  @complete @reporting
  Scenario Outline: F007SX07 Check for Hidden Or Closed Report log
    Given a pharmacy service is created with type "<service_type>"
    And the change event "OrganisationStatus" is set to "<OrganisationStatus>"
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-matcher" lambda shows field "message" with value "NHS Service marked as closed or hidden"
    And the "service-matcher" lambda shows field "report_key" with value "HIDDEN_OR_CLOSED"
    And "dos_service_uid" attribute is identified in the "HIDDEN_OR_CLOSED" report in "service-matcher" logs
    And "nhsuk_odscode" attribute is identified in the "HIDDEN_OR_CLOSED" report in "service-matcher" logs
    And "dos_service_name" attribute is identified in the "HIDDEN_OR_CLOSED" report in "service-matcher" logs
    And "nhsuk_service_status" attribute is identified in the "HIDDEN_OR_CLOSED" report in "service-matcher" logs
    And "nhsuk_service_type" attribute is identified in the "HIDDEN_OR_CLOSED" report in "service-matcher" logs
    And "nhsuk_sector" attribute is identified in the "HIDDEN_OR_CLOSED" report in "service-matcher" logs
    And "dos_service_status" attribute is identified in the "HIDDEN_OR_CLOSED" report in "service-matcher" logs
    And "dos_service_type" attribute is identified in the "HIDDEN_OR_CLOSED" report in "service-matcher" logs
    And "dos_region" attribute is identified in the "HIDDEN_OR_CLOSED" report in "service-matcher" logs
    And "nhsuk_parent_organisation_name" attribute is identified in the "HIDDEN_OR_CLOSED" report in "service-matcher" logs
    And the service history is not updated

    Examples:
      | service_type | OrganisationStatus |
      | 13           | Closed             |
      | 13           | Hidden             |

  @complete @reporting
  Scenario: F007SX08 Check for Invalid Postcode Report log
    Given a basic service is created
    And the change event "Postcode" is set to "FAKE"
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "report_key" with value "INVALID_POSTCODE"
    And "nhsuk_odscode" attribute is identified in the "INVALID_POSTCODE" report in "service-sync" logs
    And "nhsuk_organisation_name" attribute is identified in the "INVALID_POSTCODE" report in "service-sync" logs
    And "nhsuk_address1" attribute is identified in the "INVALID_POSTCODE" report in "service-sync" logs
    And "nhsuk_city" attribute is identified in the "INVALID_POSTCODE" report in "service-sync" logs
    And "nhsuk_postcode" attribute is identified in the "INVALID_POSTCODE" report in "service-sync" logs
    And "validation_error_reason" attribute is identified in the "INVALID_POSTCODE" report in "service-sync" logs
    And "dos_service" attribute is identified in the "INVALID_POSTCODE" report in "service-sync" logs
    And "dos_region" attribute is identified in the "INVALID_POSTCODE" report in "service-sync" logs
    And "dos_service_name" attribute is identified in the "INVALID_POSTCODE" report in "service-sync" logs
    And the Slack channel shows an alert saying "Invalid Postcode" from "BLUE_GREEN_ENVIRONMENT"
    And the service history is not updated

  @complete @reporting
  Scenario Outline: F007SX09 Check for missing dos service type
    Given a basic service is created
    And the change event "<service_type>" is set to "True"
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-matcher" lambda shows field "report_key" with value "MISSING_SERVICE_TYPE"
    And "ods_code" attribute is identified in the "MISSING_SERVICE_TYPE" report in "service-matcher" logs
    And "org_type" attribute is identified in the "MISSING_SERVICE_TYPE" report in "service-matcher" logs
    And "org_sub_type" attribute is identified in the "MISSING_SERVICE_TYPE" report in "service-matcher" logs
    And "nhsuk_organisation_status" attribute is identified in the "MISSING_SERVICE_TYPE" report in "service-matcher" logs
    And "dos_missing_service_type" attribute is identified in the "MISSING_SERVICE_TYPE" report in "service-matcher" logs
    And "dos_service_address" attribute is identified in the "MISSING_SERVICE_TYPE" report in "service-matcher" logs
    And "dos_service_postcode" attribute is identified in the "MISSING_SERVICE_TYPE" report in "service-matcher" logs
    And "nhsuk_parent_organisation_name" attribute is identified in the "MISSING_SERVICE_TYPE" report in "service-matcher" logs
    And "dos_region" attribute is identified in the "MISSING_SERVICE_TYPE" report in "service-matcher" logs
    And "reason" attribute is identified in the "MISSING_SERVICE_TYPE" report in "service-matcher" logs

    Examples:
      | service_type   |
      | Blood Pressure |
      | Contraception  |

  @complete @reporting
  Scenario Outline: F007SX10 Check for missing dos service type without bp and contraception
    Given a pharmacy service is created with "6" character odscode and type "<service_type>"
    And the change event has a palliative care entry
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-matcher" lambda shows field "report_key" with value "MISSING_SERVICE_TYPE"
    And "ods_code" attribute is identified in the "MISSING_SERVICE_TYPE" report in "service-matcher" logs
    And "org_type" attribute is identified in the "MISSING_SERVICE_TYPE" report in "service-matcher" logs
    And "org_sub_type" attribute is identified in the "MISSING_SERVICE_TYPE" report in "service-matcher" logs
    And "nhsuk_organisation_status" attribute is identified in the "MISSING_SERVICE_TYPE" report in "service-matcher" logs
    And "dos_missing_service_type" attribute is identified in the "MISSING_SERVICE_TYPE" report in "service-matcher" logs
    And "dos_service_address" attribute is identified in the "MISSING_SERVICE_TYPE" report in "service-matcher" logs
    And "dos_service_postcode" attribute is identified in the "MISSING_SERVICE_TYPE" report in "service-matcher" logs
    And "nhsuk_parent_organisation_name" attribute is identified in the "MISSING_SERVICE_TYPE" report in "service-matcher" logs
    And "dos_region" attribute is identified in the "MISSING_SERVICE_TYPE" report in "service-matcher" logs
    And "reason" attribute is identified in the "MISSING_SERVICE_TYPE" report in "service-matcher" logs

    Examples:
      | service_type |
      | 13           |
      | 131          |
      | 132          |
      | 134          |
      | 137          |
      | 148          |
      | 149          |
