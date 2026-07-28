Feature: Healthcheck
  Scenario: Health endpoint is checked
    Given Members service is running
    When Health endpoint is called
    Then We receive a response stating the Members service is healthy