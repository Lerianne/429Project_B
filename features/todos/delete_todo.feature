Feature: Delete a to-do item
  As a user, I want to delete a to-do item
  So that I can remove tasks I no longer need.

  Background:
    Given the API is running

  Scenario Outline: Successfully deleting a to-do item (Normal Flow)
    Given a to-do item with ID "<To-Do ID>" exists
    When I send a DELETE request to "/todos/<To-Do ID>"
    Then the response status should be 200
    And the to-do item "<To-Do ID>" should no longer exist

    Examples:
      | To-Do ID |
      | 1        |
      | 2        |

  Scenario Outline: Deleting a to-do item linked to a project or category (Alternate Flow)
    Given a to-do item with ID "<To-Do ID>" exists and is linked to a project or category
    When I send a DELETE request to "/todos/<To-Do ID>"
    Then the response status should be 200
    And the to-do item "<To-Do ID>" and its relationships should be removed

    Examples:
      | To-Do ID |
      | 3        |
      | 4        |

  Scenario Outline: Attempting to delete a completed to-do item (Error Flow)
    Given a to-do item with ID "<To-Do ID>" exists and is marked as completed
    When I send a DELETE request to "/todos/<To-Do ID>"
    Then the response status should be 403
    And the response should contain an error message "Completed to-dos cannot be deleted"

    Examples:
      | To-Do ID |
      | 5        |
      | 6        |