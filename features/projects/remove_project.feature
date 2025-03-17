Feature: Remove a project
  As a user, I want to delete a project
  So that I can remove unnecessary projects.

  Background:
    Given the API is running
    And I have an authenticated user
    And a project "<Project Name>" exists

  Scenario Outline: Successfully deleting a project (Normal Flow)
    When I send a DELETE request to "/projects/<Project ID>"
    Then the response status should be 200
    And the response should confirm the project was removed

    Examples:
      | Project Name    | Project ID |
      | Work Tasks     | 1         |
      | Home Renovation | 2         |

  Scenario Outline: Deleting a project with active todos (Alternate Flow)
    Given the project "<Project Name>" contains active todos
    When I send a DELETE request to "/projects/<Project ID>"
    Then the response status should be 400
    And the response should contain an error message "Cannot delete a project with active todos"

    Examples:
      | Project Name    | Project ID |
      | Work Tasks     | 1         |
      | Home Renovation | 2         |

  Scenario Outline: Attempting to delete a non-existent project (Error Flow)
    When I send a DELETE request to "/projects/<Invalid Project ID>"
    Then the response status should be 404
    And the response should contain an error message "Project not found"

    Examples:
      | Invalid Project ID |
      | 999               |
      | 1000              |
