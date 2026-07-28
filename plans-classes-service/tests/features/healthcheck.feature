Feature: Healthcheck
  Scenario: Health endpoint is checked
    Given Plans Payments service is running
    When Health endpoint is called
    Then We receive a response stating the Plans Payments service is healthy