Feature: Remove a todo from a project
  As a user, I want to remove a todo item from a project
  So that I can update my task list.

  Background:
    Given the API is running
    And I have an authenticated user
    And a project "<Project Name>" exists
    And the project contains a todo "<Todo Name>"

  Scenario Outline: Successfully removing a todo from a project (Normal Flow)
    When I send a DELETE request to "/projects/<Project ID>/tasks/<Task ID>"
    Then the response status should be 200
    And the response should confirm the todo was removed

    Examples:
      | Project Name   | Project ID | Task ID | Todo Name    |
      | Work Tasks    | 1         | 101     | Submit Report |
      | Home Renovation | 2        | 102     | Buy Paint    |

  Scenario Outline: Attempting to remove a completed todo (Alternate Flow)
    Given the todo "<Todo Name>" is marked as completed
    When I send a DELETE request to "/projects/<Project ID>/tasks/<Task ID>"
    Then the response status should be 200
    And the response should confirm the todo was removed

    Examples:
      | Project Name    | Project ID | Task ID | Todo Name     |
      | Work Tasks     | 1         | 103     | Revise Report |
      | Home Renovation | 2        | 104     | Buy New Paint |

  Scenario Outline: Attempting to remove a non-existent todo (Error Flow)
    When I send a DELETE request to "/projects/<Project ID>/tasks/<Invalid Task ID>"
    Then the response status should be 404
    And the response should contain an error message "Task not found"

    Examples:
      | Project ID | Invalid Task ID |
      | 1         | 999             |
      | 2         | 1000            |
