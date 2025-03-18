import requests
import json
from behave import given, when, then

BASE_URL = "http://localhost:4567"

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


@given('the project "{project_name}" contains active todos')
def step_project_contains_active_todos(context, project_name):
    """Ensure that a project contains active todos"""
    project_response = requests.get(f"{BASE_URL}/projects")
    projects = project_response.json()

    project_id = next((p["id"] for p in projects if p["title"] == project_name), None)
    assert project_id, f"Project '{project_name}' not found"

    payload = {"title": "Active Task", "completed": False}
    response = requests.post(f"{BASE_URL}/projects/{project_id}/tasks", json=payload)

    assert response.status_code == 201, "Failed to add an active task to the project"


@given('the project contains a todo "{todo_name}"')
def step_ensure_todo_exists(context, todo_name):
    """Ensure a todo with the given name exists"""
    payload = {"title": todo_name}
    response = requests.post(f"{BASE_URL}/todos", json=payload)

    assert response.status_code == 201, f"Failed to create todo '{todo_name}'"


@given('the todo "{todo_name}" is marked as completed')
def step_mark_todo_completed(context, todo_name):
    """Ensure a todo is marked as completed"""
    todos_response = requests.get(f"{BASE_URL}/todos")
    todos = todos_response.json()

    todo_id = next((t["id"] for t in todos if t["title"] == todo_name), None)
    assert todo_id, f"Todo '{todo_name}' not found"

    payload = {"completed": True}
    response = requests.put(f"{BASE_URL}/todos/{todo_id}", json=payload)

    assert response.status_code == 200, "Failed to mark todo as completed"


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

@when('I send a DELETE request to "/projects/{project_id}"')
def step_delete_project(context, project_id):
    """Send DELETE request to remove a project"""
    context.response = requests.delete(f"{BASE_URL}/projects/{project_id}")

@when('I send a POST request to "/projects" with the same project name "{project_name}"')
def step_create_duplicate_project(context, project_name):
    """Attempt to create a duplicate project"""
    payload = {"title": project_name}
    context.response = requests.post(f"{BASE_URL}/projects", json=payload)

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
    response_data = context.response.json()

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
    response_data = context.response.json()
    assert "id" in response_data, "Response missing project ID"
    assert response_data["title"] == project_name, \
        f"Expected project name '{project_name}', got '{response_data['title']}'"


@then('the response should contain the todo ID and name "{todo_name}"')
def step_validate_todo_creation(context, todo_name):
    """Ensure todo was created successfully"""
    response_data = context.response.json()
    assert "id" in response_data, "Response missing todo ID"
    assert response_data["title"] == todo_name, \
        f"Expected todo name '{todo_name}', got '{response_data['title']}'"

@then('the response should confirm the project was removed')
def step_validate_project_deletion(context):
    """Ensure project deletion is successful"""
    assert context.response.status_code == 200, f"Expected 200 OK, got {context.response.status_code}"
    response_data = context.response.json()
    assert "success" in response_data or context.response.status_code == 204, "Expected confirmation of deletion"


@then('the response should contain the todo ID, name "{todo_name}", and due date "{due_date}"')
def step_validate_todo_response_with_due_date(context, todo_name, due_date):
    """Verify the response contains correct todo details, including the due date"""
    response_data = context.response.json()
    
    assert "id" in response_data, "Response missing todo ID"
    assert response_data["title"] == todo_name, f"Expected todo name '{todo_name}', got '{response_data['title']}'"
    assert response_data["dueDate"] == due_date, f"Expected due date '{due_date}', got '{response_data['dueDate']}'"


@then('the response should contain the project ID, name "{project_name}", and description "{description}"')
def step_validate_project_response_with_description(context, project_name, description):
    """Verify the response contains correct project details, including description"""
    response_data = context.response.json()
    
    assert "id" in response_data, "Response missing project ID"
    assert response_data["title"] == project_name, f"Expected project name '{project_name}', got '{response_data['title']}'"
    assert response_data["description"] == description, f"Expected description '{description}', got '{response_data['description']}'"