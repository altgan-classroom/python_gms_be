Feature: Healthcheck
  Scenario: Health endpoint is checked
    Given Auth service is running
    When Health endpoint is called
    Then We receive a response stating the Auth service is healthy