Feature: Link a to-do item to a project
  As a user, I want to assign a to-do item to a project
  So that I can organize tasks by project.

  Background:
    Given the API is running
    And I have an authenticated user

  Scenario Outline: Successfully linking a to-do item to a project (Normal Flow)
    Given a to-do item with ID "<To-Do ID>" exists
    And a project with ID "<Project ID>" exists
    When I send a POST request to "/todos/<To-Do ID>/tasksof" with project ID "<Project ID>"
    Then the response status should be 201
    And the response should confirm that the to-do item "<To-Do ID>" is linked to project "<Project ID>"

    Examples:
      | To-Do ID | Project ID |
      | 1        | 10         |
      | 2        | 11         |

  Scenario Outline: Assigning multiple to-do items to the same project (Alternate Flow)
    Given a project with ID "<Project ID>" exists
    And two to-do items with IDs "<To-Do ID 1>" and "<To-Do ID 2>" exist
    When I send a POST request to "/todos/<To-Do ID 1>/tasksof" with project ID "<Project ID>"
    And I send a POST request to "/todos/<To-Do ID 2>/tasksof" with project ID "<Project ID>"
    Then both to-do items "<To-Do ID 1>" and "<To-Do ID 2>" should be linked to project "<Project ID>"

    Examples:
      | To-Do ID 1 | To-Do ID 2 | Project ID |
      | 3          | 4          | 12         |
      | 5          | 6          | 13         |

  Scenario Outline: Attempting to link a to-do item to a non-existent project (Error Flow)
    Given a to-do item with ID "<To-Do ID>" exists
    And no project with ID "<Project ID>" exists
    When I send a POST request to "/todos/<To-Do ID>/tasksof" with project ID "<Project ID>"
    Then the response status should be 404
    And the response should contain an error message "Project not found"

    Examples:
      | To-Do ID | Project ID |
      | 7        | 99         |
      | 8        | 100        |
