import requests
from behave import given, when, then

BASE_URL = "http://localhost:4567"

### 🔹 GIVEN STEPS (Preconditions) ###

@given('the to-do list is empty')
def step_clear_todos(context):
    """Ensure the to-do list is empty before running a test"""
    response = requests.get(f"{BASE_URL}/todos")
    if response.status_code == 200:
        todos = response.json().get("todos", [])
        for todo in todos:
            requests.delete(f"{BASE_URL}/todos/{todo['id']}")

@given('a to-do item with ID "{todo_id}" exists')
def step_create_todo_with_id(context, todo_id):
    """Ensure a to-do item exists with a known ID"""
    payload = {"title": f"Test Todo {todo_id}", "description": "Sample description"}
    response = requests.post(f"{BASE_URL}/todos", json=payload)
    assert response.status_code == 201, "Failed to create test to-do"
    context.todo_id = response.json()["id"]  # Store created ID dynamically

@given('no to-do item with ID "{todo_id}" exists')
def step_no_todo_exists(context, todo_id):
    """Ensure a specific to-do item does not exist"""
    requests.delete(f"{BASE_URL}/todos/{todo_id}")

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
    """Attempt to create a to-do item with an invalid field"""
    payload = {invalid_field: "Invalid data"}
    context.response = requests.post(f"{BASE_URL}/todos", json=payload)

@when('I send a GET request to "/todos/{todo_id}"')
def step_get_todo(context, todo_id):
    """Retrieve the specific to-do item created in the test"""
    context.response = requests.get(f"{BASE_URL}/todos/{todo_id}")

@when('I send a DELETE request to "/todos/{todo_id}"')
def step_delete_todo(context, todo_id):
    """Delete the dynamically stored to-do item"""
    context.response = requests.delete(f"{BASE_URL}/todos/{todo_id}")

@when('I send a PUT request to "/todos/{todo_id}" with a new description "{description}"')
def step_update_todo(context, todo_id, description):
    """Update a to-do item's description"""
    payload = {"description": description}
    context.response = requests.put(f"{BASE_URL}/todos/{todo_id}", json=payload)

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
    assert "description" in response_data, "No description field found"
    assert response_data["description"] == "", "Expected empty description"

@then('the error message should indicate an invalid request')
def step_validate_invalid_request(context):
    """Check if the API returns an error for invalid data"""
    response_data = context.response.json()
    assert "error" in response_data, f"Expected error key in response, but got: {response_data}"

@then('the to-do item "{todo_id}" should no longer exist')
def step_validate_todo_deleted(context, todo_id):
    """Ensure the to-do item no longer exists"""
    response = requests.get(f"{BASE_URL}/todos/{todo_id}")
    assert response.status_code == 404, "To-do item still exists after deletion"

@then('the to-do item\'s description should be updated to "{description}"')
def step_validate_todo_updated_description(context, description):
    """Ensure the to-do item's description was updated"""
    response_data = context.response.json()
    assert response_data["description"] == description, \
        f"Expected description '{description}', got '{response_data['description']}'"
