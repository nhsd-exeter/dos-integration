Feature: DOS INTEGRATION E2E TESTS

  @complete @dev
  Scenario: A VALID CHANGED EVENT IS PROCESSED AND SENT TO DOS
    Given a Changed Event is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the processed Changed Request is sent to Dos

  @complete @dev
  Scenario: UNMATCHED DOS SERVICES EXCEPTION IS LOGGED
    Given a Changed Event with invalid ODSCode is provided
    When the Changed Event is sent for processing with "valid" api key
    Then no matched services were found
    And the unmatched service exception is reported to cloudwatch
    Then the Changed Event is not processed any further

  @complete @dev
  Scenario: ALL RECEIVED CHANGED EVENT IS ARCHIVED IN DYNAMO DB
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
    When the OpeningTimes Times data is not defined
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
  Scenario: 400 from DOS results in Splunk error log
    Given a Changed Event is valid
    And the correlation-id is "Bad Request"
    When the Changed Event is sent for processing with "valid" api key
    Then the event is sent to the DLQ
    And the DLQ logs the error for Splunk
    And the "eb_dlq" logs show status code "400"

  @dev
  Scenario: DLQ logs show "message abandoned" error_msg
    Given a Changed Event is valid
    And the correlation-id is "Bad Request"
    When the Changed Event is sent for processing with "valid" api key
    Then the "eb_dlq" logs show error message "Message Abandoned:"


@complete @dev
  Scenario: All data required in the Opening times exception report is identifiable in the logs
    Given a Changed Event is valid
    When the OpeningTimes Times data is not defined
    And the Changed Event is sent for processing with "valid" api key
    Then the attributes for invalid opening times report is identified in the logs


  @complete @dev
  Scenario: A Changed event with aligned data does not create a CR
    Given a Changed Event is aligned with Dos
    When the Changed Event is sent for processing with "valid" api key
    Then no Changed request is created


  @complete @dev
  Scenario: AN UNPROCESSED CHANGED EVENT IS REPLAYED IN DI
    Given a Changed Event is valid
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Event is stored in dynamo db
    And the stored Changed Event is reprocessed in DI
    And the reprocessed Changed Event is sent to Dos
