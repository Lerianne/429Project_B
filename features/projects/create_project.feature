Feature: Create a new project
  As a user, I want to create a new project
  So that I can organize my tasks efficiently.

  Background:
    Given the API is running
    And I have an authenticated user

  Scenario Outline: Successfully creating a new project (Normal Flow)
    When I send a POST request to "/projects" with a project name "<Project Name>"
    Then the response status should be 201
    And the response should contain the project ID and name "<Project Name>"

    Examples:
      | Project Name    |
      | Work Tasks      |
      | Home Renovation |

  Scenario Outline: Creating a project with an optional description (Alternate Flow)
    When I send a POST request to "/projects" with a project name "<Project Name>" and description "<Description>"
    Then the response status should be 201
    And the response should contain the project ID, name "<Project Name>", and description "<Description>"

    Examples:
      | Project Name    | Description            |
      | Fitness Plan    | Weekly workout plan   |
      | Grocery List    | Shopping items list   |

  Scenario Outline: Attempting to create a duplicate project (Error Flow)
    Given a project named "<Project Name>" already exists
    When I send a POST request to "/projects" with the same project name "<Project Name>"
    Then the response status should be 409
    And the response should contain an error message "Project already exists"

    Examples:
      | Project Name    |
      | Work Tasks      |
      | Home Renovation |
