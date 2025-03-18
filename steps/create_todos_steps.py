import requests
from behave import given, when, then

BASE_URL = "http://localhost:4567"

### 🔹 GIVEN STEPS (Preconditions) ###

@given('the to-do list is empty')
def step_clear_todos(context):
    """Ensure the to-do list is empty before running tests"""
    response = requests.get(f"{BASE_URL}/todos")
    if response.status_code == 200:
        todos = response.json().get("todos", [])
        for todo in todos:
            requests.delete(f"{BASE_URL}/todos/{todo['id']}")

@given('a to-do item exists')
@given('a to-do item with ID "{todo_id}" exists')
def step_create_todo(context, todo_id=None):
    """Ensure a to-do item exists before testing"""
    payload = {"title": f"Test Todo {todo_id or 'default'}", "description": "Sample description"}
    response = requests.post(f"{BASE_URL}/todos", json=payload)
    assert response.status_code == 201, "Failed to create test to-do"
    context.todo_id = response.json()["id"]  # Store created ID dynamically

@given('no to-do item with ID "{todo_id}" exists')
def step_no_todo_exists(context, todo_id):
    """Ensure a to-do item does not exist before testing"""
    
    # Attempt to delete the to-do item (if it exists)
    requests.delete(f"{BASE_URL}/todos/{todo_id}")

    # Verify it was deleted
    response = requests.get(f"{BASE_URL}/todos/{todo_id}")
    assert response.status_code == 404, f"To-do {todo_id} still exists!"

    # ✅ Store the `todo_id` in context for later steps
    context.todo_id = todo_id  # Ensure it's always set

@given('a to-do item with ID "{todo_id}" exists and is marked as completed')
def step_todo_completed(context, todo_id):
    """Ensure a to-do exists and is marked as completed"""

    # Step 1: Create the to-do item
    payload = {"title": f"Test Todo {todo_id}", "doneStatus": False}
    response = requests.post(f"{BASE_URL}/todos", json=payload)
    
    assert response.status_code == 201, f"Failed to create test to-do, Response: {response.text}"

    # Store the created to-do ID
    context.todo_id = response.json()["id"]

    # Step 2: Retrieve the existing to-do item (handle different API response structures)
    todo_response = requests.get(f"{BASE_URL}/todos/{context.todo_id}")
    assert todo_response.status_code == 200, f"Failed to retrieve to-do, Response: {todo_response.text}"

    existing_todo = todo_response.json()

    # Handle cases where the response is wrapped inside "todos" array
    if "todos" in existing_todo and len(existing_todo["todos"]) > 0:
        existing_todo = existing_todo["todos"][0]

    assert "title" in existing_todo, f"API response did not contain 'title': {existing_todo}"

    # Step 3: Mark it as completed (send all necessary fields)
    update_payload = {
        "title": existing_todo["title"],  # Ensure title is included
        "doneStatus": "true"  # Use correct boolean format
    }
    update_response = requests.put(f"{BASE_URL}/todos/{context.todo_id}", json=update_payload)

    print("\n==== DEBUG: Marking To-Do as Completed ====")
    print(f"Sent Payload: {update_payload}")
    print(f"Response Status: {update_response.status_code}")
    print(f"Response Body: {update_response.text}")
    print("=====================================\n")

    assert update_response.status_code == 200, f"Failed to mark to-do as completed, Response: {update_response.text}"

@given('a to-do item with ID "{todo_id}" exists and is linked to a project or category')
def step_todo_linked_to_project_or_category(context, todo_id):
    """Ensure a to-do is linked to a project or category"""
    # Step 1: Create the to-do item
    step_create_todo(context, todo_id)

    # Step 2: Create a project
    project_payload = {"title": f"Test Project {todo_id}"}
    project_response = requests.post(f"{BASE_URL}/projects", json=project_payload)
    assert project_response.status_code == 201, "Failed to create test project"
    project_id = project_response.json()["id"]

    # Step 3: Link to-do to the project
    link_response = requests.post(f"{BASE_URL}/todos/{context.todo_id}/tasksof", json={"id": project_id})
    assert link_response.status_code == 201, f"Failed to link to-do {context.todo_id} to project {project_id}"
    
    # Store project ID in context
    context.project_id = project_id

### 🔹 WHEN STEPS (Actions) ###

@when('I send a POST request to "/todos" with a title "{title}" and description "{description}"')
def step_create_todo_with_values(context, title, description):
    """Create a new to-do item with given title and description"""
    payload = {"title": title, "description": description}
    context.response = requests.post(f"{BASE_URL}/todos", json=payload)

@when('I send a POST request to "/todos" with a title "{title}" and no description')
def step_create_todo_no_description(context, title):
    """Create a to-do item without a description"""
    payload = {"title": title}
    context.response = requests.post(f"{BASE_URL}/todos", json=payload)

@when('I send a POST request to "/todos" with an invalid field "{invalid_field}"')
def step_create_todo_invalid_field(context, invalid_field):
    """Attempt to create a to-do item with invalid data"""

    if invalid_field == "Missing Title":
        payload = {"description": "Valid description"}  # Missing "title"
    elif invalid_field == "Description as Number":
        payload = {"title": "Valid Title", "description": 12345}  # Invalid type
    else:
        payload = {}

    context.response = requests.post(f"{BASE_URL}/todos", json=payload)

    # Print API response for debugging
    print("\n==== DEBUG: Invalid Request Test ====")
    print(f"Sent Payload: {payload}")
    print(f"Response Status: {context.response.status_code}")
    print(f"Response Body: {context.response.text}")
    print("=====================================\n")


@when('I send a GET request to "/todos/{todo_id}"')
def step_get_todo(context, todo_id):
    """Retrieve a specific to-do item"""
    context.response = requests.get(f"{BASE_URL}/todos/{context.todo_id}")

@when('I send a DELETE request to "/todos/{todo_id}"')
def step_delete_todo(context, todo_id):
    """Delete a to-do item"""
    
    # If context.todo_id is set (for existing to-dos), use it
    todo_id_to_delete = getattr(context, "todo_id", todo_id)  # Use context.todo_id if available

    context.response = requests.delete(f"{BASE_URL}/todos/{todo_id_to_delete}")


@when('I send a PUT request to "/todos/{todo_id}" with a new description "{description}"')
def step_update_todo(context, todo_id, description):
    """Update a to-do item's description"""
    payload = {"description": description}
    context.response = requests.put(f"{BASE_URL}/todos/{context.todo_id}", json=payload)

@when('I send a POST request to "/todos/{todo_id}/tasksof" with project ID "{project_id}"')
def step_link_todo_to_project(context, todo_id, project_id):
    """Link a to-do item to a project"""
    payload = {"id": project_id}
    context.response = requests.post(f"{BASE_URL}/todos/{context.todo_id}/tasksof", json=payload)

### 🔹 THEN STEPS (Validations) ###

@then("the response status should be {status_code:d}")
def step_check_status_code(context, status_code):
    """Validate the response status code"""
    assert context.response.status_code == status_code, \
        f"Expected {status_code}, got {context.response.status_code}"

@then('the response should contain the to-do ID, title "{title}", and description "{description}"')
def step_validate_todo_details(context, title, description):
    """Ensure the response contains the correct to-do item details"""
    response_data = context.response.json()
    assert "id" in response_data, "Response missing to-do ID"
    assert response_data["title"] == title, f"Expected title '{title}', got '{response_data['title']}'"
    assert response_data["description"] == description, f"Expected description '{description}', got '{response_data['description']}'"

@then('the response should contain the to-do ID, title "{title}", and an empty description ""')
def step_validate_todo_with_empty_description(context, title):
    """Check that a to-do item was created with an empty description"""
    response_data = context.response.json()
    assert response_data["description"] == "", "Expected empty description"

@then('the response should contain an error message "Completed to-dos cannot be deleted"')
def step_validate_completed_todo_delete_error(context):
    """Ensure API returns a 'cannot delete completed to-do' error"""
    response_data = context.response.json()

    # Check if error message is in "errorMessages" or "error"
    assert "errorMessages" in response_data or "error" in response_data, \
        f"Expected an error key, but got: {response_data}"

    # Check specific error message
    error_messages = response_data.get("errorMessages", []) + [response_data.get("error", "")]
    assert any("Completed to-dos cannot be deleted" in msg for msg in error_messages), \
        f"Unexpected error message: {error_messages}"

@then('the to-do item "{todo_id}" and its relationships should be removed')
def step_validate_todo_relationship_removed(context, todo_id):
    """Ensure the to-do item and its relationships are removed"""
    # Check if to-do still exists
    response = requests.get(f"{BASE_URL}/todos/{context.todo_id}")
    assert response.status_code == 404, f"To-do {context.todo_id} still exists after deletion"

    # Check if the relationship is removed
    response = requests.get(f"{BASE_URL}/projects/{context.project_id}/tasks")
    assert response.status_code == 200, "Failed to retrieve project tasks"
    tasks = response.json().get("todos", [])
    assert not any(task["id"] == context.todo_id for task in tasks), \
        f"To-do {context.todo_id} is still linked to project {context.project_id}"

@then('the to-do item "{todo_id}" should no longer exist')
def step_validate_todo_deleted(context, todo_id):
    """Ensure the to-do item no longer exists"""

    # Use the ID stored in context, or the given one
    todo_id_to_check = getattr(context, "todo_id", todo_id) 

    response = requests.get(f"{BASE_URL}/todos/{todo_id_to_check}")
    assert response.status_code == 404, f"To-do {todo_id_to_check} still exists after deletion"


@then('the to-do item\'s description should be updated to "{description}"')
def step_validate_todo_updated_description(context, description):
    """Ensure the to-do item's description was updated"""
    response_data = context.response.json()
    assert response_data["description"] == description, \
        f"Expected description '{description}', got '{response_data['description']}'"

@then('the to-do item "{todo_id}" should be linked to project "{project_id}"')
def step_validate_todo_linked(context, todo_id, project_id):
    """Check if a to-do item is linked to a project"""
    response = requests.get(f"{BASE_URL}/todos/{context.todo_id}/tasksof")
    assert response.status_code == 200, "Failed to retrieve linked projects"
    response_data = response.json()
    assert any(proj["id"] == project_id for proj in response_data["projects"]), \
        f"To-do item {context.todo_id} is not linked to project {project_id}"
