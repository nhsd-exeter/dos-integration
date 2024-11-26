Feature: F002. Invalid change event Exception handling

  @complete @validation
  Scenario: F002SXX1. A Changed Event where OrganisationTypeID is NOT PHA is reported and ignored
    Given a basic service is created
    And the change event "OrganisationTypeId" is set to "DEN"
    When the Changed Event is sent for processing with "valid" api key
    Then the "ingest-change-event" lambda shows field "message" with value "Validation Error - Unexpected Org Type ID: 'DEN'"
    And the service history is not updated

  @complete @validation
  Scenario: F002SXX2. A Changed Event where OrganisationSubType is NOT Community is reported and ignored
    Given a basic service is created
    And the change event "OrganisationSubType" is set to "com"
    And the change event staff field is populated
    When the Changed Event is sent for processing with "valid" api key
    Then logs show staff data has been redacted
    And error messages do not show Staff data
    And the "ingest-change-event" lambda shows field "message" with value "Validation Error - Unexpected Org Sub Type ID: 'com'"

  @complete @validation
  Scenario: F002SXX3. Address changes are discarded when postcode is invalid
    Given a basic service is created
    And the change event "Postcode" is set to "FAKE"
    And the change event "Website" is set to "https://www.test.com"
    And the change event "Address1" is set to "FAKE2"
    When the Changed Event is sent for processing with "valid" api key
    Then the "address" has not been changed in DoS

  @complete @validation
  Scenario: F002SXX4. Invalid Opening Times reported where Weekday is not identified
    Given a basic service is created
    And the change event has no weekday present in opening times
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "message" with value "Opening times are not valid"

  @complete @general
  Scenario: F002SXX5. Invalid Opening Times reported where OpeningTimeType is not defined as General or Additional
    Given a basic service is created
    And the change event has an invalid openingtimetype
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "message" with value "Opening times are not valid"

  @complete @general
  Scenario: F002SXX6. IsOpen is true AND Times is blank
    Given a basic service is created
    And the change event has undefined opening and closing times
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "message" with value "Opening times are not valid"
    And the service history is not updated

  @complete @general
  Scenario: F002SXX7. IsOpen is false AND Times NOT blank
    Given a basic service is created
    And the change event has opening times open status set to false
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "message" with value "Opening times are not valid"

  @complete @general
  Scenario: F002SXX8. OpeningTimeType is Additional AND AdditionalOpening Date is Blank
    Given a basic service is created
    And the change event has an additional date with no specified date
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "message" with value "Opening times are not valid"

  @complete @validation
  Scenario: F002SXX9. A Changed Event where OrganisationSubType is NOT DistanceSelling is reported and ignored
    Given a basic service is created with type "134"
    And the change event "OrganisationSubType" is set to "Distance Selling"
    When the Changed Event is sent for processing with "valid" api key
    Then the "ingest-change-event" lambda shows field "message" with value "Validation Error - Unexpected Org Sub Type ID: 'Distance Selling'"
    And the service history is not updated
