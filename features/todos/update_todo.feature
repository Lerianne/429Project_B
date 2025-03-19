Feature: Update a to-do item
  As a user, I want to update my to-do item
  So that I can modify its details when needed.

  Background:
    Given the API is running
    And I have an authenticated user

  Scenario Outline: Successfully updating a to-do item's description (Normal Flow)
    Given a to-do item with ID "<To-Do ID>" exists
    When I send a PUT request to "/todos/<To-Do ID>" with a new description "<New Description>"
    Then the response status should be 200
    And the to-do item's description should be updated to "<New Description>"

    Examples:
      | To-Do ID | New Description          |
      | 1        | Buy groceries and fruit  |
      | 2        | Study math for 2 hours   |

  Scenario Outline: Updating only the title of a to-do item (Alternate Flow)
    Given a to-do item with ID "<To-Do ID>" exists
    When I send a POST request to "/todos/<To-Do ID>" with a new title "<New Title>"
    Then the response status should be 200
    And the to-do item's title should be updated to "<New Title>"
    And the description should remain unchanged

    Examples:
      | To-Do ID | New Title         |
      | 3        | Read a new book   |
      | 4        | Finish homework   |

  Scenario Outline: Attempting to update a to-do item with an invalid field (Error Flow)
    Given a to-do item with ID "<To-Do ID>" exists
    When I send a PUT request to "/todos/<To-Do ID>" with an invalid field "<Invalid Field>"
    Then the response status should be 400
    And the response should contain an error message "Could not find field: <Invalid Field>"

    Examples:
      | To-Do ID | Invalid Field    |
      | 5        | DueDate as Text  |
      | 6        | Priority: -1     |

  Scenario Outline: Attempting to update a non-existent to-do item (Error Flow)
    Given no to-do item with ID "<To-Do ID>" exists
    When I send a PUT request to "/todos/<To-Do ID>" with a new title "<New Title>"
    Then the response status should be 404
    And the response should contain an error message "Invalid GUID for <To-Do ID> entity todo"

  Examples:
    | To-Do ID | New Title          |
    | 99       | Plan vacation      |
    | 100      | Organize files     |


