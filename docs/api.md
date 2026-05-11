# API Documentation

## Overview

The API provides a REST endpoint for the AI agent functionality.

## Endpoint

### POST /run

Processes user input through the AI agent and returns a response.

**URL**: `http://127.0.0.1:8000/run`

**Method**: POST

**Content-Type**: application/json

**Request Body**:
```json
{
  "user_id": "string",
  "text": "string"
}
```

**Response**:
```json
{
  "answer": "string"
}
```

**Status Codes**:
- 200: Success
- 422: Validation error
- 500: Internal server error

**Example**:
```bash
curl -X POST "http://127.0.0.1:8000/run" \
     -H "Content-Type: application/json" \
     -d '{"user_id": "123456", "text": "Hello"}'
```

Response:
```json
{
  "answer": "Hello! How can I help you today?"
}
```

## Implementation Details

- Built with FastAPI
- Asynchronous processing
- Calls agent core with user input
- Returns LLM-generated response
- No authentication required (for development)