Feature: Retrieve a specific to-do item
  As a user, I want to view a specific to-do item
  So that I can check its details.

  Background:
    Given the API is running
    And I have an authenticated user

  Scenario Outline: Successfully retrieving a to-do item (Normal Flow)
    Given a to-do item with ID "<To-Do ID>" exists
    When I send a GET request to "/todos/<To-Do ID>"
    Then the response status should be 200
    And the response should contain the to-do ID "<To-Do ID>", title, and description

    Examples:
      | To-Do ID |
      | 1        |
      | 2        |

  Scenario Outline: Retrieving a to-do item linked to a project or category (Alternate Flow)
    Given a to-do item with ID "<To-Do ID>" exists and is linked to a project or category
    When I send a GET request to "/todos/<To-Do ID>"
    Then the response status should be 200
    And the response should contain the to-do ID "<To-Do ID>" and related project/category details

    Examples:
      | To-Do ID |
      | 3        |
      | 4        |

  Scenario Outline: Attempting to retrieve a non-existent to-do item (Error Flow)
    Given no to-do item with ID "<To-Do ID>" exists
    When I send a GET request to "/todos/<To-Do ID>"
    Then the response status should be 404
    And the response should contain an error message "To-do not found"

    Examples:
      | To-Do ID |
      | 99       |
      | 100      |
