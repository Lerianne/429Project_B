import requests
import json
from behave import given, when, then

BASE_URL = "http://localhost:4567"

def get_json_response(context):
    """Safely parse JSON response, handling empty responses."""
    try:
        return context.response.json()
    except json.decoder.JSONDecodeError:
        return {}  # Return empty dict if response body is empty

### GIVEN STEPS (Preconditions) ###

@given("the API is running")
def step_check_api_running(context):
    """Ensure the API is available before running tests"""
    response = requests.get(f"{BASE_URL}/projects")
    assert response.status_code == 200, "API is not running or unavailable"

@given("I have an authenticated user")
def step_authenticate_user(context):
    """Mock user authentication"""
    context.headers = {"Authorization": "Bearer test-token"}

@given('a project named "{project_name}" already exists')
def step_project_already_exists(context, project_name):
    """Ensure a project exists before testing duplicate creation"""

    # Fetch all projects
    response = requests.get(f"{BASE_URL}/projects")
    assert response.status_code == 200, "Failed to fetch existing projects"

    try:
        existing_projects = response.json()

        # Ensure correct response structure
        if isinstance(existing_projects, dict) and "projects" in existing_projects:
            existing_projects = existing_projects["projects"]
        else:
            existing_projects = []

        # Check if project already exists
        if any(proj.get("title") == project_name for proj in existing_projects):
            return  # Project already exists, do not create it again

    except json.JSONDecodeError:
        assert False, "Failed to parse JSON response from API"

    # Create project
    payload = {"title": project_name}
    create_response = requests.post(f"{BASE_URL}/projects", json=payload)
    
    # Ensure project creation is successful
    assert create_response.status_code == 201, f"Failed to create project '{project_name}', got {create_response.status_code}"

    # Store project ID for future steps
    context.project_id = create_response.json().get("id")

@given('a project "{project_name}" exists')
def step_ensure_project_exists(context, project_name):
    """Ensure that a project with the given name exists"""
    payload = {"title": project_name}
    response = requests.post(f"{BASE_URL}/projects", json=payload)

    assert response.status_code in [200, 201], f"Failed to create project '{project_name}', got status {response.status_code}"

@given('the project contains a category "{category_name}"')
def step_ensure_project_has_category(context, category_name):
    """Ensure that a category is assigned to a project"""

    # Ensure a project exists in context
    assert hasattr(context, "project_id"), "Project ID is missing. Ensure a project exists before adding a category."

    # Define payload
    payload = {"title": category_name}

    # Debugging: Print project ID before making the request
    print(f"\nDEBUG: Adding category '{category_name}' to project ID '{context.project_id}'\n")

    # Send request to add category
    response = requests.post(f"{BASE_URL}/projects/{context.project_id}/categories", json=payload)

    # Ensure category creation was successful
    assert response.status_code == 201, f"Failed to add category '{category_name}' to project ID '{context.project_id}', got status {response.status_code}"

    # Store category ID for deletion test
    response_data = response.json()
    assert "id" in response_data, "Category creation response missing ID field"
    
    context.category_id = response_data["id"]
    print(f"\nDEBUG: Created category '{category_name}' with ID '{context.category_id}'\n")


@given('the project "{project_name}" contains active todos')
def step_project_contains_active_todos(context, project_name):
    """Ensure that a project contains at least one active todo"""
    
    # Fetch all projects
    project_response = requests.get(f"{BASE_URL}/projects")
    
    # Ensure JSON is parsed correctly
    try:
        projects_data = project_response.json()
    except json.JSONDecodeError:
        assert False, "Failed to parse JSON response from API"

    # Ensure projects_data is a dictionary and contains a "projects" list
    if isinstance(projects_data, dict) and "projects" in projects_data:
        projects = projects_data["projects"]
    else:
        assert False, f"Unexpected API response format: {projects_data}"

    # Ensure the correct format for accessing project attributes
    project = next((p for p in projects if p.get("title") == project_name), None)
    assert project, f"Project '{project_name}' not found"

    # Ensure project ID exists
    project_id = project.get("id")
    assert project_id, f"Project '{project_name}' does not have a valid ID"

    # Add a test todo to the project
    payload = {"title": "Active Task", "completed": False}
    response = requests.post(f"{BASE_URL}/projects/{project_id}/tasks", json=payload)

    assert response.status_code == 201, f"Failed to add an active task to project '{project_name}'"
    context.project_id = project_id

@given('the project contains a todo "{todo_name}"')
def step_ensure_todo_exists(context, todo_name):
    """Ensure a todo with the given name exists"""
    payload = {"title": todo_name}
    response = requests.post(f"{BASE_URL}/todos", json=payload)

    assert response.status_code == 201, f"Failed to create todo '{todo_name}'"


@given('the todo "{todo_name}" is marked as completed')
def step_mark_todo_completed(context, todo_name):
    """Ensure a todo is marked as completed"""

    # Fetch all todos
    todos_response = requests.get(f"{BASE_URL}/todos")

    # Ensure JSON is parsed correctly
    try:
        todos_data = todos_response.json()
    except json.JSONDecodeError:
        assert False, "Failed to parse JSON response from API"

    # Ensure todos_data is a dictionary and contains a "todos" list
    if isinstance(todos_data, dict) and "todos" in todos_data:
        todos = todos_data["todos"]
    else:
        assert False, f"Unexpected API response format: {todos_data}"

    # Ensure the correct format for accessing todo attributes
    todo = next((t for t in todos if t.get("title") == todo_name), None)
    assert todo, f"Todo '{todo_name}' not found"

    # Ensure todo ID exists
    todo_id = todo.get("id")
    assert todo_id, f"Todo '{todo_name}' does not have a valid ID"

    # Mark todo as completed
    payload = {"completed": True}
    response = requests.put(f"{BASE_URL}/todos/{todo_id}", json=payload)

    assert response.status_code == 200, f"Failed to mark todo '{todo_name}' as completed"

### WHEN STEPS (Actions) ###

@when('I send a POST request to "/projects" with a project name "{project_name}"')
@when('I send a POST request to "/projects" with a project name "{project_name}" and description "{description}"')
def step_create_project(context, project_name, description=None):
    """Send POST request to create a new project (handles optional description)"""
    payload = {"title": project_name}
    
    if description:
        payload["description"] = description
    
    context.response = requests.post(f"{BASE_URL}/projects", json=payload)

@when('I send a POST request to "/projects/{project_id}/tasks" with a todo name "{todo_name}"')
def step_create_todo(context, project_id, todo_name):
    """Send POST request to add a todo to a project"""
    payload = {"title": todo_name}
    context.response = requests.post(f"{BASE_URL}/projects/{project_id}/tasks", json=payload)

@when('I send a DELETE request to "/projects/{project_id}/categories/{category_id}"')
def step_delete_category(context, project_id, category_id):
    """Send a DELETE request to remove a category from a project."""
    context.response = requests.delete(f"{BASE_URL}/projects/{project_id}/categories/{category_id}")

@when('I send a DELETE request to "/projects/{project_id}"')
def step_delete_project(context, project_id):
    """Send DELETE request to remove a project"""
    context.response = requests.delete(f"{BASE_URL}/projects/{project_id}")

@when('I send a POST request to "/projects" with the same project name "{project_name}"')
def step_create_duplicate_project(context, project_name):
    """Attempt to create a duplicate project"""
    payload = {"title": project_name}
    context.response = requests.post(f"{BASE_URL}/projects", json=payload)

@when('I send a POST request to "/projects/{project_id}/categories" with a category name "{category_name}"')
def step_add_category_to_project(context, project_id, category_name):
    """Send a POST request to add a category to a project."""
    payload = {"title": category_name}
    context.response = requests.post(f"{BASE_URL}/projects/{project_id}/categories", json=payload)


# @when('I send a POST request to "/projects/{invalid_project_id}/categories" with a category name "{category_name}"')
# def step_add_category_to_nonexistent_project(context, invalid_project_id, category_name):
#     """Attempt to add a category to a non-existent project."""
#     payload = {"title": category_name}
#     context.response = requests.post(f"{BASE_URL}/projects/{invalid_project_id}/categories", json=payload)


# @when('I send a DELETE request to "/projects/{project_id}/categories/{invalid_category_id}"')
# def step_delete_nonexistent_category(context, project_id, invalid_category_id):
#     """Attempt to delete a category that does not exist."""
#     context.response = requests.delete(f"{BASE_URL}/projects/{project_id}/categories/{invalid_category_id}")

@when('I send a PUT request to "/projects/{project_id}" with a new name "{new_name}" but the same description "{description}"')
def step_update_project_name_with_description(context, project_id, new_name, description):
    """Send a PUT request to update a project name while keeping the description."""
    payload = {"title": new_name, "description": description}
    context.response = requests.put(f"{BASE_URL}/projects/{project_id}", json=payload)

@when('I send a PUT request to "/projects/{project_id}" with a new name "{new_name}"')
def step_update_project_name(context, project_id, new_name):
    """Send a PUT request to update a project name."""
    payload = {"title": new_name}
    context.response = requests.put(f"{BASE_URL}/projects/{project_id}", json=payload)

#LEANNES VERSION
#@then('the response should contain an error message "{error_message}"')
#def step_validate_error_message(context, error_message):
#    """Verify error message in the response"""
#    response_data = context.response.json()
    
#    assert "error" in response_data, "Expected error key in response"
#    assert error_message in response_data["error"], f"Expected error message '{error_message}', got '{response_data['error']}'"

#HELENA-> this one passes for me
@then('the response should contain an error message "Invalid request"')
def step_validate_invalid_request(context):
    """Check if the API returns an error for invalid data"""
    response_data = get_json_response(context)

    # Debugging print
    print("\n==== DEBUG: Error Message Check ====")
    print(f"Full Response: {response_data}")
    print("=====================================\n")

    # Check if response contains "errorMessages"
    assert "errorMessages" in response_data, f"Expected 'errorMessages' key, but got: {response_data}"

    # Ensure the error message is related to the missing title
    assert "title : field is mandatory" in response_data["errorMessages"], \
        f"Expected 'title : field is mandatory', but got: {response_data['errorMessages']}"


### THEN STEPS (Validations) ###

@then("the response status should be {status_code:d}")
def step_check_status_code(context, status_code):
    """Validate response status code"""
    assert context.response.status_code == status_code, \
        f"Expected {status_code}, got {context.response.status_code}"

@then('the response should contain the project ID and name "{project_name}"')
def step_validate_response(context, project_name):
    """Verify the response contains correct project details"""
    response_data = get_json_response(context)
    assert "id" in response_data, "Response missing project ID"
    assert response_data["title"] == project_name, \
        f"Expected project name '{project_name}', got '{response_data['title']}'"

@then('the response should confirm the todo was removed')
def step_validate_todo_deletion(context):
    """Ensure the API confirms the todo was removed."""

    # The API response should have a successful status (200 OK or 204 No Content)
    assert context.response.status_code in [200, 204], \
        f"Expected 200 OK or 204 No Content, got {context.response.status_code}"

    # Parse response to check for expected confirmation messages
    response_data = get_json_response(context)

    # If the API provides a success message in the response body
    if response_data:
        assert "success" in response_data or "message" in response_data, \
            f"Expected a confirmation message in response, got: {response_data}"

    print("\nDEBUG: Todo successfully removed.\n")


@then('the response should contain the todo ID and name "{todo_name}"')
def step_validate_todo_creation(context, todo_name):
    """Ensure todo was created successfully"""
    response_data = get_json_response(context)
    assert "id" in response_data, "Response missing todo ID"
    assert response_data["title"] == todo_name, \
        f"Expected todo name '{todo_name}', got '{response_data['title']}'"

@then('the response should confirm the project was removed')
def step_validate_project_deletion(context):
    """Ensure project deletion is successful"""
    assert context.response.status_code == 200, f"Expected 200 OK, got {context.response.status_code}"
    response_data = get_json_response(context)
    assert "success" in response_data or context.response.status_code == 204, "Expected confirmation of deletion"


@then('the response should contain the todo ID, name "{todo_name}", and due date "{due_date}"')
def step_validate_todo_response_with_due_date(context, todo_name, due_date):
    """Verify the response contains correct todo details, including the due date"""
    response_data = get_json_response(context)
    
    assert "id" in response_data, "Response missing todo ID"
    assert response_data["title"] == todo_name, f"Expected todo name '{todo_name}', got '{response_data['title']}'"
    assert response_data["dueDate"] == due_date, f"Expected due date '{due_date}', got '{response_data['dueDate']}'"


@then('the response should contain the project ID, name "{project_name}", and description "{description}"')
def step_validate_project_response_with_description(context, project_name, description):
    """Verify the response contains correct project details, including description"""
    response_data = get_json_response(context)
    
    assert "id" in response_data, "Response missing project ID"
    assert response_data["title"] == project_name, f"Expected project name '{project_name}', got '{response_data['title']}'"
    assert response_data["description"] == description, f"Expected description '{description}', got '{response_data['description']}'"

@then('the response should contain an error message "{expected_message}"')
def step_validate_error_message(context, expected_message):
    """Ensure the response contains the expected error message dynamically."""
    response_data = get_json_response(context)

    # Debugging Output
    print("\n===== DEBUG: API Response for Error =====")
    print(response_data)
    print("========================================\n")

    # Ensure the response contains an error message
    assert "errorMessages" in response_data, "Expected 'errorMessages' key in response"

    # Extract the actual error message
    actual_error_message = (
        response_data["errorMessages"][0] if isinstance(response_data["errorMessages"], list)
        else response_data["errorMessages"]
    )

    # Check if the expected message is in the actual error message
    assert expected_message in actual_error_message, \
        f"Expected error message '{expected_message}', but got '{actual_error_message}'"
    
@then('the response should contain the category ID and name "{category_name}"')
def step_validate_category_creation(context, category_name):
    """Ensure the category was created successfully."""
    response_data = get_json_response(context)
    assert "id" in response_data, "Response missing category ID"
    assert response_data["title"] == category_name, \
        f"Expected category name '{category_name}', got '{response_data['title']}'"

@then('the response should confirm the category was removed')
def step_validate_category_deletion(context):
    """Ensure category deletion is successful."""
    assert context.response.status_code == 200, f"Expected 200 OK, got {context.response.status_code}"

@then('the project name should be updated to "{new_name}"')
def step_validate_project_update(context, new_name):
    """Ensure project name was updated successfully."""
    response_data = get_json_response(context)
    assert response_data["title"] == new_name, \
        f"Expected project name '{new_name}', got '{response_data['title']}'"

@then('the response should confirm the project name update while keeping the description')
def step_validate_project_update_description(context):
    """Ensure project name was updated while keeping the description."""
    response_data = get_json_response(context)
    assert "title" in response_data and "description" in response_data, "Response missing project details"
    assert response_data["description"] is not None, "Description should not be null after update"

