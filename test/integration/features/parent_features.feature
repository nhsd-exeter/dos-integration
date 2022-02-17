Feature: DOS INTEGRATION E2E TESTS

  @complete @dev
  Scenario: A valid Changed Event is processed and sent to DOS
    Given a Changed Event is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the processed Changed Request is sent to Dos

  @complete @dev
  Scenario: Unmatched DOS services exception is logged
    Given a Changed Event with invalid ODSCode is provided
    When the Changed Event is sent for processing with "valid" api key
    Then no matched services were found
    And the unmatched service exception is reported to cloudwatch
    Then the Changed Event is not processed any further

  @complete @dev
  Scenario: All received Changed Event is archived in Dynamo DB
    Given a Changed Event is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Event is stored in dynamo db

  @complete @dev
  Scenario: A Changed Event with no postcode LAT Long Values is reported
    Given a Changed Event is valid
    When the postcode has no LAT Long values
    And the Changed Event is sent for processing with "valid" api key
    Then the invalid postcode exception is reported to cloudwatch

  @complete @dev
  Scenario: A Changed Event where OrganisationTypeID is NOT PHA is reported and ignored
    Given a Changed Event contains an incorrect OrganisationTypeID
    When the Changed Event is sent for processing with "valid" api key
    Then the exception is reported to cloudwatch
    And the Changed Event is not processed any further

  @complete @dev
  Scenario: A Changed Event where OrganisationSubType is NOT Community is reported and ignored
    Given a Changed Event contains an incorrect OrganisationSubtype
    When the Changed Event is sent for processing with "valid" api key
    Then the exception is reported to cloudwatch
    And the Changed Event is not processed any further

  @complete @dev
  Scenario: Changed Event with Hidden Organisation status is reported
    Given a Changed Event is valid
    When the OrganisationStatus is defined as "Hidden"
    And the Changed Event is sent for processing with "valid" api key
    Then the hidden or closed exception is reported to cloudwatch

  @complete @dev
  Scenario: Changed Event with Closed Organisation status is not processed
    Given a Changed Event is valid
    When the OrganisationStatus is defined as "Closed"
    And the Changed Event is sent for processing with "valid" api key
    Then the Changed Event is not processed any further

  @complete @dev
  Scenario: Address changes are discarded when postcode is invalid
    Given a Changed Event is valid
    When the postcode is invalid
    And the Changed Event is sent for processing with "valid" api key
    Then the 'address' from the changes is not included in the change request

  @complete @dev
  Scenario: Postcode not included in Changes when postcode is invalid
    Given a Changed Event is valid
    When the postcode is invalid
    And the Changed Event is sent for processing with "valid" api key
    Then the 'postcode' from the changes is not included in the change request

  @complete @dev
  Scenario: Invalid Opening Times reported where Weekday is not identified
    Given a Changed Event with the Weekday NOT present in the Opening Times data
    When the Changed Event is sent for processing with "valid" api key
    Then the OpeningTimes exception is reported to cloudwatch

  @complete @dev
  Scenario: Invalid Opening Times reported where OpeningTimeType is not defined as General or Additional
    Given a Changed Event where OpeningTimeType is NOT defined correctly
    When the Changed Event is sent for processing with "valid" api key
    Then the OpeningTimes exception is reported to cloudwatch

@complete @dev
  Scenario: IsOpen is true AND Times is blank
    Given a Changed Event is valid
    When the OpeningTimes Opening and Closing Times data are not defined
    And the Changed Event is sent for processing with "valid" api key
    Then the OpeningTimes exception is reported to cloudwatch

@complete @dev
  Scenario: IsOpen is false AND Times in NOT blank
    Given a Changed Event with the openingTimes IsOpen status set to false
    When the Changed Event is sent for processing with "valid" api key
    Then the OpeningTimes exception is reported to cloudwatch

  @complete @dev
  Scenario:  OpeningTimeType is Additional AND AdditionalOpening Date is Blank
    Given a Changed Event is valid
    When the OpeningTimes OpeningTimeType is Additional and AdditionalOpeningDate is not defined
    And the Changed Event is sent for processing with "valid" api key
    Then the OpeningTimes exception is reported to cloudwatch

  @complete @dev
  Scenario: An OpeningTime is received for the Day or Date where IsOpen is True and IsOpen is false
    Given a Changed Event is valid
    When an AdditionalOpeningDate contains data with both true and false IsOpen status
    And the Changed Event is sent for processing with "valid" api key
    Then the OpeningTimes exception is reported to cloudwatch

  @dev
  Scenario: DOS rejects CE and returns SC 400 with invalid Correlation ID and logs error in Splunk
    Given a Changed Event is valid
    And the correlation-id is "Bad Request"
    When the Changed Event is sent for processing with "valid" api key
    Then the event is sent to the DLQ
    And the DLQ logs the error for Splunk
    And the "eb_dlq" logs show status code "400"

  @dev
  Scenario: A CR with invalid Correlation ID gets rejected by events bridge and is NOT sent to DOS
    Given a Changed Event is valid
    And the correlation-id is "Bad Request"
    When the Changed Event is sent for processing with "valid" api key
    Then the "eb_dlq" logs show error message "Message Abandoned"

@complete @dev
  Scenario: All data required in the Opening times exception report is identifiable in the logs
    Given a Changed Event is valid
    When the OpeningTimes Opening and Closing Times data are not defined
    And the Changed Event is sent for processing with "valid" api key
    Then the attributes for invalid opening times report is identified in the logs

  @complete @dev
  Scenario: A Changed event with aligned data does not create a CR
    Given a Change Event is aligned with Dos
    When the Changed Event is sent for processing with "valid" api key
    Then no Changed request is created

  @complete @dev
  Scenario: An unprocessed Changed Event is replayed in DI
    Given a Changed Event is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Event is stored in dynamo db
    And the stored Changed Event is reprocessed in DI
    And the reprocessed Changed Event is sent to Dos
