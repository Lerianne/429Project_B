Feature: Update a project
  As a user, I want to update a project name
  So that I can rename it when necessary.

  Background:
    Given the API is running
    And I have an authenticated user
    And a project "<Old Project Name>" exists

  Scenario Outline: Successfully updating a project name (Normal Flow)
    When I send a PUT request to "/projects/<Project ID>" with a new name "<New Project Name>"
    Then the response status should be 200
    And the project name should be updated to "<New Project Name>"

    Examples:
      | Old Project Name | Project ID | New Project Name |
      | Work Tasks      | 1         | Office Tasks     |
      | Home Renovation | 2         | House Repairs    |

  Scenario Outline: Updating a project name without changing description (Alternate Flow)
    When I send a PUT request to "/projects/<Project ID>" with a new name "<New Project Name>" but the same description "<Description>"
    Then the response status should be 200
    And the response should confirm the project name update while keeping the description

    Examples:
      | Old Project Name | Project ID | New Project Name | Description        |
      | Work Tasks      | 1         | Office Tasks    | Work-related tasks |
      | Home Renovation | 2         | House Repairs  | House improvement  |

  Scenario Outline: Attempting to update a non-existent project (Error Flow)
    When I send a PUT request to "/projects/<Invalid Project ID>" with a new name "<New Project Name>"
    Then the response status should be 404
    And the response should contain an error message "Project not found"

    Examples:
      | Invalid Project ID | New Project Name |
      | 999               | New Office Tasks |
      | 1000              | Garden Upgrade  |
