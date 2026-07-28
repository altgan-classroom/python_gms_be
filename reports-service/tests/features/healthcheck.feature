Feature: Healthcheck
  Scenario: Health endpoint is checked
    Given Reports service is running
    When Health endpoint is called
    Then We receive a response stating the Reports service is healthy