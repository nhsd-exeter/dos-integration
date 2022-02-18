Feature: F002. Invalid change event handling

  @complete @dev
  Scenario: F002S001. Unmatched DOS services exception is logged
    Given a Changed Event with invalid ODSCode is provided
    When the Changed Event is sent for processing with "valid" api key
    Then no matched services were found
    And the unmatched service exception is reported to cloudwatch
    Then the Changed Event is not processed any further
    And the Changed Event is not sent to Dos
    And the Changed Event is stored in dynamo db

  @complete @dev
  Scenario: F002S002. Changed Event with Hidden Organisation status is reported
    Given a Changed Event is valid
    When the OrganisationStatus is defined as "Hidden"
    And the Changed Event is sent for processing with "valid" api key
    Then the hidden or closed exception is reported to cloudwatch
    And the Changed Event is stored in dynamo db

  @complete @dev
  Scenario: F002S003. Changed Event with Closed Organisation status is not processed
    Given a Changed Event is valid
    When the OrganisationStatus is defined as "Closed"
    And the Changed Event is sent for processing with "valid" api key
    Then the Changed Event is not processed any further
    And the Changed Event is stored in dynamo db

  @complete @dev
  Scenario: F002S004. A Changed Event where OrganisationTypeID is NOT PHA is reported and ignored
    Given a Changed Event contains an incorrect OrganisationTypeID
    When the Changed Event is sent for processing with "valid" api key
    Then the exception is reported to cloudwatch
    And the Changed Event is not processed any further
    And the Changed Event is stored in dynamo db

  @complete @dev
  Scenario: F002S005. A Changed Event where OrganisationSubType is NOT Community is reported and ignored
    Given a Changed Event contains an incorrect OrganisationSubtype
    When the Changed Event is sent for processing with "valid" api key
    Then the exception is reported to cloudwatch
    And the Changed Event is not processed any further
    And the Changed Event is stored in dynamo db

  @complete @dev
  Scenario: F002S006. A Changed Event with no postcode LAT Long Values is reported
    Given a Changed Event is valid
    When the postcode has no LAT Long values
    And the Changed Event is sent for processing with "valid" api key
    Then the invalid postcode exception is reported to cloudwatch
    And the Changed Event is stored in dynamo db

  @complete @dev
  Scenario: F002S007. Address changes are discarded when postcode is invalid
    Given a Changed Event is valid
    When the postcode is invalid
    And the Changed Event is sent for processing with "valid" api key
    Then the 'address' from the changes is not included in the change request
    And the 'postcode' from the changes is not included in the change request
    And the Changed Event is stored in dynamo db

  @complete @dev
  Scenario: F002S008. Invalid Opening Times reported where Weekday is not identified
    Given a Changed Event with the Weekday NOT present in the Opening Times data
    When the Changed Event is sent for processing with "valid" api key
    Then the OpeningTimes exception is reported to cloudwatch
    And the Changed Event is stored in dynamo db

  @complete @dev
  Scenario: F002S009. Invalid Opening Times reported where OpeningTimeType is not defined as General or Additional
    Given a Changed Event where OpeningTimeType is NOT defined correctly
    When the Changed Event is sent for processing with "valid" api key
    Then the OpeningTimes exception is reported to cloudwatch
    And the Changed Event is stored in dynamo db

@complete @dev
  Scenario: F002S010. IsOpen is true AND Times is blank
    Given a Changed Event is valid
    When the OpeningTimes Opening and Closing Times data are not defined
    And the Changed Event is sent for processing with "valid" api key
    Then the OpeningTimes exception is reported to cloudwatch
    And the Changed Event is stored in dynamo db

@complete @dev
  Scenario: F002S011. IsOpen is false AND Times NOT blank
    Given a Changed Event with the openingTimes IsOpen status set to false
    When the Changed Event is sent for processing with "valid" api key
    Then the OpeningTimes exception is reported to cloudwatch
    And the Changed Event is stored in dynamo db

  @complete @dev
  Scenario: F002S012. OpeningTimeType is Additional AND AdditionalOpening Date is Blank
    Given a Changed Event is valid
    When the OpeningTimes OpeningTimeType is Additional and AdditionalOpeningDate is not defined
    And the Changed Event is sent for processing with "valid" api key
    Then the OpeningTimes exception is reported to cloudwatch
    And the Changed Event is stored in dynamo db

  @complete @dev
  Scenario: F002S013. An OpeningTime is received for the Day or Date where IsOpen is True and IsOpen is false
    Given a Changed Event is valid
    When an AdditionalOpeningDate contains data with both true and false IsOpen status
    And the Changed Event is sent for processing with "valid" api key
    Then the OpeningTimes exception is reported to cloudwatch
    And the Changed Event is stored in dynamo db

@complete @dev
  Scenario: F002S014. All data required in the Opening times exception report is identifiable in the logs
    Given a Changed Event is valid
    When the OpeningTimes Opening and Closing Times data are not defined
    And the Changed Event is sent for processing with "valid" api key
    Then the attributes for invalid opening times report is identified in the logs
    And the Changed Event is stored in dynamo db
