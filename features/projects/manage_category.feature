Feature: Manage Categories for a Project
  As a user, I want to add and remove categories associated with a project
  So that I can organize projects by category.

  Background:
    Given the API is running
    And I have an authenticated user
    And a project named "<Project Name>" already exists

  Scenario Outline: Successfully adding a category to a project (Normal Flow)
    When I send a POST request to "/projects/<Project ID>/categories" with a category name "<Category Name>"
    Then the response status should be 201
    And the response should contain the category ID and name "<Category Name>"

    Examples:
      | Project Name     | Project ID | Category Name   |
      | Work Tasks      | 1          | Productivity    |
      | Home Renovation | 2          | Home Improvement |

  Scenario Outline: Attempting to add a category to a non-existent project (Error Flow)
    When I send a POST request to "/projects/<Invalid Project ID>/categories" with a category name "<Category Name>"
    Then the response status should be 404
    And the response should contain an error message "Project not found"

    Examples:
      | Invalid Project ID | Category Name   |
      | 999               | Productivity    |
      | 1000              | Home Improvement |

  Scenario Outline: Successfully removing a category from a project (Normal Flow)
    Given the project contains a category "<Category Name>"
    When I send a DELETE request to "/projects/<Project ID>/categories/<Category ID>"
    Then the response status should be 200
    And the response should confirm the category was removed

    Examples:
      | Project Name     | Project ID | Category ID | Category Name   |
      | Work Tasks      | 1          | 201        | Productivity    |
      | Home Renovation | 2          | 202        | Home Improvement |

  Scenario Outline: Attempting to remove a non-existent category (Error Flow)
    When I send a DELETE request to "/projects/<Project ID>/categories/<Invalid Category ID>"
    Then the response status should be 404
    And the response should contain an error message "Category not found"

    Examples:
      | Project ID | Invalid Category ID |
      | 1         | 999                 |
      | 2         | 1000                |
