Feature: Manage Todos for a Project
  As a user, I want to add and remove todo items associated with a project
  So that I can track and update tasks within specific projects.

  Background:
    Given the API is running
    And I have an authenticated user
    And a project named "<Project Name>" already exists

  Scenario Outline: Successfully adding a todo to a project (Normal Flow)
    When I send a POST request to "/projects/<Project ID>/tasks" with a todo name "<Todo Name>"
    Then the response status should be 201
    And the response should contain the todo ID and name "<Todo Name>"

    Examples:
      | Project Name    | Project ID | Todo Name     |
      | Work Tasks     | 1          | Submit Report |
      | Home Renovation | 2         | Buy Paint     |

  Scenario Outline: Adding a todo with a due date (Alternate Flow)
    When I send a POST request to "/projects/<Project ID>/tasks" with a todo name "<Todo Name>" and due date "<Due Date>"
    Then the response status should be 201
    And the response should contain the todo ID, name "<Todo Name>", and due date "<Due Date>"

    Examples:
      | Project Name     | Project ID | Todo Name     | Due Date  |
      | Work Tasks      | 1          | Submit Report | 2025-04-01 |
      | Home Renovation | 2          | Buy Paint     | 2025-04-10 |

  Scenario Outline: Attempting to add a todo to a non-existent project (Error Flow)
    When I send a POST request to "/projects/<Invalid Project ID>/tasks" with a todo name "<Todo Name>"
    Then the response status should be 404
    And the response should contain an error message "Project not found"

    Examples:
      | Invalid Project ID | Todo Name     |
      | 999               | Test Task     |
      | 1000              | Fix the Bug   |

  Scenario Outline: Successfully removing a todo from a project (Normal Flow)
    Given the project contains a todo "<Todo Name>"
    When I send a DELETE request to "/projects/<Project ID>/tasks/<Task ID>"
    Then the response status should be 200
    And the response should confirm the todo was removed

    Examples:
      | Project Name     | Project ID | Task ID | Todo Name     |
      | Work Tasks      | 1          | 101     | Submit Report |
      | Home Renovation | 2          | 102     | Buy Paint     |

  Scenario Outline: Attempting to remove a completed todo (Alternate Flow)
    Given the project contains a todo "<Todo Name>"
    And the todo "<Todo Name>" is marked as completed
    When I send a DELETE request to "/projects/<Project ID>/tasks/<Task ID>"
    Then the response status should be 200
    And the response should confirm the todo was removed

    Examples:
      | Project Name     | Project ID | Task ID | Todo Name     |
      | Work Tasks      | 1          | 103     | Revise Report |
      | Home Renovation | 2          | 104     | Buy New Paint |

  Scenario Outline: Attempting to remove a non-existent todo (Error Flow)
    When I send a DELETE request to "/projects/<Project ID>/tasks/<Invalid Task ID>"
    Then the response status should be 404
    And the response should contain an error message "Task not found"

    Examples:
      | Project ID | Invalid Task ID |
      | 1         | 999             |
      | 2         | 1000            |
