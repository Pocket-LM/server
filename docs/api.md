# Pocket LM Server API Documentation

**Base URL:** `http://localhost:8000/api/v1`

This document provides a complete reference for all the API endpoints available in the Pocket LM server.

---

# Health Check

This document provides details for the health check API endpoint.

## `GET /`

This endpoint is used to verify that the server is running and healthy.

### Request

No request body is required.

### Response

**Success (Status 200)**

```json
{
  "status": "ok"
}
```

---

# Knowledge Capture

This document provides details for the knowledge capture API endpoint.

## `POST /capture`

This endpoint is used to capture knowledge from different sources like a URL, a text selection, or a PDF file.

### Request

The request must be of type `multipart/form-data`.

**Form Fields:**

| Field           | Type         | Description                                                                                             | Required |
| --------------- | ------------ | ------------------------------------------------------------------------------------------------------- | -------- |
| `type`          | `string`     | The type of content to capture. Must be one of `url`, `selection`, or `pdf`.                            | Yes      |
| `knowledge_base`| `string`     | The name of the knowledge base (collection) to save the content to.                                     | Yes      |
| `url`           | `string`     | The URL of the page to capture. Required if `type` is `url` or `selection`.                             | No       |
| `selection`     | `string`     | The selected text to capture. Required if `type` is `selection`.                                        | No       |
| `pdf`           | `file`       | The PDF file to capture. Required if `type` is `pdf`.                                                   | No       |

### Response

**Success (Status 200)**

```json
{
  "status": "success",
  "message": "Content from {type} captured successfully for knowledge base: {knowledge_base}.",
  "data": null
}
```

**Error (Status 4xx/5xx)**

```json
{
  "detail": "Error message describing the issue."
}
```

---

# Collection Management

This document provides details for the collection (knowledge base) management API endpoints.

## `GET /collection`

This endpoint lists all available collections (knowledge bases).

### Request

No request body is required.

### Response

**Success (Status 200)**

```json
{
  "status": "success",
  "message": "Collections retrieved successfully.",
  "data": [
    "collection_name_1",
    "collection_name_2"
  ]
}
```

**Error (Status 4xx/5xx)**

```json
{
  "detail": "Error message describing the issue."
}
```

---

## `POST /collection`

This endpoint creates a new, empty collection (knowledge base).

### Request

The request must be of type `application/json`.

**Body:**

```json
{
  "name": "new_collection_name"
}
```

| Field | Type     | Description                               | Required |
| ----- | -------- | ----------------------------------------- | -------- |
| `name`  | `string` | The name for the new collection.          | Yes      |

### Response

**Success (Status 200)**

```json
{
  "status": "success",
  "message": "Collection '{name}' created successfully.",
  "data": null
}
```

**Error (Status 400 - Already Exists)**

```json
{
  "detail": "Collection with name '{name}' already exists."
}
```

---

## `DELETE /collection`

This endpoint deletes an existing collection and all its associated data.

### Request

The request must be of type `application/json`.

**Body:**

```json
{
  "name": "collection_to_delete"
}
```

| Field | Type     | Description                               | Required |
| ----- | -------- | ----------------------------------------- | -------- |
| `name`  | `string` | The name of the collection to delete.     | Yes      |

### Response

**Success (Status 200)**

```json
{
  "status": "success",
  "message": "Collection '{name}' deleted successfully.",
  "data": null
}
```

**Error (Status 400 - Not Found)**

```json
{
  "detail": "Collection with name '{name}' does not exist."
}
```

---

# Chat

This document provides details for the chat-related API endpoints.

## `GET /chat/history`

This endpoint retrieves the chat history for the current session.

### Request

No request body is required.

### Response

**Success (Status 200)**

```json
{
  "status": "success",
  "message": "Chat history retrieved successfully",
  "data": [
    {
      "messageContent": "Hi, my name is Julian.",
      "type": "human"
    },
    {
      "messageContent": "Hello Julian! How can I help you today?",
      "type": "ai"
    }
  ]
}
```

**Error (Status 4xx/5xx)**

```json
{
  "detail": "Error message describing the issue."
}
```

---

## `POST /chat/message`

This endpoint processes a user's chat message and returns the AI's response.

### Request

The request must be of type `application/json`.

**Body:**

```json
{
  "userQuery": "What is my name?",
  "collectionName": "my_knowledge_base"
}
```

| Field          | Type     | Description                               | Required |
| -------------- | -------- | ----------------------------------------- | -------- |
| `userQuery`    | `string` | The user's message.                       | Yes      |
| `collectionName` | `string` | The name of the collection to use for context. | Yes      |

### Response

**Success (Status 200)**

```json
{
  "status": "success",
  "message": "Message processed successfully",
  "data": {
    "messageContent": "Your name is Julian."
  }
}
```

**Error (Status 4xx/5xx)**

```json
{
  "detail": "Error message describing the issue."
}
```

---

## `DELETE /chat/clear`

This endpoint clears the chat history for the current session.

### Request

No request body is required.

### Response

**Success (Status 200)**

```json
{
  "status": "success",
  "message": "Chat history cleared successfully",
  "data": null
}
```

**Error (Status 4xx/5xx)**

```json
{
  "detail": "Error message describing the issue."
}
```