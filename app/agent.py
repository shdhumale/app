from google.adk.agents import Agent
import requests
import json
from typing import Any, Dict, List, Optional

#1. Basic Agent
base_agent = Agent(
    model='gemini-2.0-flash-001',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
)


# 2. Basic Agent with Tool
BASE_URL = "https://api.restful-api.dev/objects"

def get_all_objects() -> Optional[List[Dict[str, Any]]]:
    """
    Consumes GET List of all objects: https://api.restful-api.dev/objects
    """
    print("\n--- GET All Objects ---")
    try:
        response = requests.get(BASE_URL)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        data = response.json()
        print(json.dumps(data, indent=2))
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching all objects: {e}")
        return None

def get_objects_by_ids(ids: List[int]) -> Optional[List[Dict[str, Any]]]:
    """
    Consumes GET List of objects by ids: https://api.restful-api.dev/objects?id=3&id=5&id=10
    Args:
        ids (list): A list of integer IDs.
    """
    print(f"\n--- GET Objects by IDs: {ids} ---")
    params = {'id': ids} # Requests handles list parameters correctly for multiple 'id'
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        print(json.dumps(data, indent=2))
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching objects by IDs: {e}")
        return None

def get_single_object(object_id: str) -> Optional[Dict[str, Any]]:
    """
    Consumes GET Single object: https://api.restful-api.dev/objects/7
    Args:
        object_id (str): The ID of the object to retrieve.
    """
    print(f"\n--- GET Single Object: {object_id} ---")
    url = f"{BASE_URL}/{object_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print(json.dumps(data, indent=2))
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching single object {object_id}: {e}")
        return None

def add_object(name: str, data_payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Consumes POST Add object: https://api.restful-api.dev/objects
    Args:
        name (str): The name of the new object.
        data_payload (dict): A dictionary representing the 'data' field of the object.
    """
    print(f"\n--- POST Add Object: {name} ---")
    payload = {
        "name": name,
        "data": data_payload
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(BASE_URL, json=payload, headers=headers)
        response.raise_for_status()
        new_object = response.json()
        print(json.dumps(new_object, indent=2))
        return new_object
    except requests.exceptions.RequestException as e:
        print(f"Error adding object: {e}")
        return None

def update_object(object_id: str, name: str, data_payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Consumes PUT Update object: https://api.restful-api.dev/objects/7
    Args:
        object_id (str): The ID of the object to update.
        name (str): The new name for the object.
        data_payload (dict): The new 'data' field for the object.
    """
    print(f"\n--- PUT Update Object: {object_id} ---")
    url = f"{BASE_URL}/{object_id}"
    payload = {
        "name": name,
        "data": data_payload
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.put(url, json=payload, headers=headers)
        response.raise_for_status()
        updated_object = response.json()
        print(json.dumps(updated_object, indent=2))
        return updated_object
    except requests.exceptions.RequestException as e:
        print(f"Error updating object {object_id}: {e}")
        return None

def partially_update_object(object_id: str, data_to_update: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Consumes PATCH Partially update object: https://api.restful-api.dev/objects/7
    Args:
        object_id (str): The ID of the object to partially update.
        data_to_update (dict): A dictionary containing the fields to update (e.g., {"name": "New Name"}).
    """
    print(f"\n--- PATCH Partially Update Object: {object_id} ---")
    url = f"{BASE_URL}/{object_id}"
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.patch(url, json=data_to_update, headers=headers)
        response.raise_for_status()
        patched_object = response.json()
        print(json.dumps(patched_object, indent=2))
        return patched_object
    except requests.exceptions.RequestException as e:
        print(f"Error partially updating object {object_id}: {e}")
        return None

def delete_object(object_id: str) -> Optional[Dict[str, Any]]:
    """
    Consumes DELETE object: https://api.restful-api.dev/objects/6
    Args:
        object_id (str): The ID of the object to delete.
    """
    print(f"\n--- DELETE Object: {object_id} ---")
    url = f"{BASE_URL}/{object_id}"
    try:
        response = requests.delete(url)
        response.raise_for_status()
        # A successful DELETE often returns 200 OK with a message, or 204 No Content
        # The restful-api.dev returns 200 OK with a success message for DELETE
        data = response.json()
        print(json.dumps(data, indent=2))
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error deleting object {object_id}: {e}")
        return None


tool_agent = Agent(
    name="tool_agent",
    model="gemini-2.0-flash-001",
    description="An agent that can interact with a RESTful API for objects",
    instruction="""
    You are a RestAPI service caller assistant. Call the given tools as per the instruction given by the uses and print the data in json format.
    """,
    tools=[
        get_all_objects,
        get_objects_by_ids,
        get_single_object,
        add_object,
        update_object,
        partially_update_object,
        delete_object,
    ],
)


root_agent=tool_agent