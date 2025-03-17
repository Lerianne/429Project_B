Feature: Create a new to-do item
  As a user, I want to create a new to-do item
  So that I can track my tasks effectively.

  Background:
    Given the API is running

  Scenario Outline: Successfully creating a new to-do item (Normal Flow)
    When I send a POST request to "/todos" with a title "<Title>" and description "<Description>"
    Then the response status should be 201
    And the response should contain the to-do ID, title "<Title>", and description "<Description>"

    Examples:
      | Title           | Description              |
      | Buy Groceries   | Milk, eggs, and bread   |
      | Study for Exam  | Review math chapters    |

  Scenario Outline: Creating a to-do item without a description (Alternate Flow)
    When I send a POST request to "/todos" with a title "<Title>" and no description
    Then the response status should be 201
    And the response should contain the to-do ID, title "<Title>", and an empty description ""

    Examples:
      | Title          |
      | Morning Workout |
      | Read a Book     |

  Scenario Outline: Attempting to create a to-do item with invalid data (Error Flow)
    When I send a POST request to "/todos" with an invalid field "<Invalid Field>"
    Then the response status should be 400
    And the response should contain an error message "Invalid request"

    Examples:
      | Invalid Field        |
      | Missing Title        |
      | Description as Number |
