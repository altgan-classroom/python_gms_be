Feature: CRUD Operations
  Scenario: User Profile Data Returned
    Given An user profile exists in the database
    When using the GET endpoint for members
    Then We receive a response containing the member information

  Scenario: User Profile Data Created and Returned
    Given User data is POSTED
    When GETTING the created user data
    Then The same posted data is returned