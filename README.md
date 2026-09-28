# Lead Capture API

A backend API built with **pure Python** to capture, validate, persist, and classify potential clients using an LLM.

This project is part of my **Road to Agentic AI**, focused on building the backend fundamentals required to create reliable AI-powered systems and agents.

The goal is to understand what happens behind automation platforms by implementing the core workflow directly with Python.

---

## Architecture

```text
Client
(Postman / cURL)
      │
      ▼
FastAPI
POST /leads
      │
      ▼
Pydantic
Validation
      │
      ▼
SQLite
Persist Lead
      │
      ▼
LLM
Classify Lead
      │
      ▼
SQLite
Save Classification
      │
      ▼
JSON Response
```

### Request flow

1. The client sends lead information through a `POST /leads` request.
2. **FastAPI** receives the HTTP request.
3. **Pydantic** validates the incoming data.
4. The lead is stored in **SQLite**.
5. An **LLM** analyzes and classifies the lead.
6. The classification result is stored in the database.
7. The API returns a JSON response.

---

## Tech Stack

* **Python** — Backend language
* **FastAPI** — REST API framework
* **Pydantic** — Request validation and data schemas
* **SQLAlchemy** — ORM and database interaction
* **SQLite** — Local relational database
* **LLM** — Lead classification
* **Postman / cURL** — API testing
* **python-dotenv** — Environment variable management

---

## Technical Decisions

### Why FastAPI?

FastAPI was chosen because it provides a simple way to build HTTP APIs while working naturally with Python type hints and Pydantic validation.

It also makes it easy to expose endpoints that can later be consumed by other applications, automation workflows, or AI agents.

### Why Pydantic?

Pydantic validates incoming data before it reaches the application logic.

The API uses it to ensure that required fields are present and that incoming values have the expected format and types.

Invalid requests are rejected with a `422 Unprocessable Entity` response.

### Why SQLite?

SQLite was selected because this project focuses on learning backend fundamentals without introducing unnecessary infrastructure.

It provides a real relational database while keeping the project simple and portable.

The architecture can later be migrated to a production database such as PostgreSQL.

### Why SQLAlchemy?

SQLAlchemy provides an abstraction between the Python application and the database.

The application works with Python models and database sessions instead of manually writing SQL for every operation.

This also makes the transition to another relational database easier.

### Why classify the lead with an LLM?

The LLM transforms raw lead information into useful business information.

At this stage, each lead is classified based on its intent as:

* `Hot`
* `Cold`

If the LLM fails during classification, the lead is preserved and assigned a `pending` status instead of being lost.

### Model initialization

The LLM is initialized inside the `classify_lead()` function rather than when the API starts.

This ties model initialization to the operation that actually requires it.

---

## API Endpoint

### `POST /leads`

Creates a new lead, stores it in the database, classifies it using an LLM, and stores the classification result.

### Request

```http
POST /leads
Content-Type: application/json
```

### Required fields

All five fields are required:

* `name`
* `email`
* `phone`
* `request`
* `notes`

The `notes` field must be included in the JSON request, but its value can be an empty string.

### Example request

```json
{
  "name": "Juan",
  "email": "juan@example.com",
  "phone": "8095551234",
  "request": "Website design",
  "notes": "I need a website for my recent business."
}
```

### Request with empty notes

```json
{
  "name": "Juan",
  "email": "juan@example.com",
  "phone": "8095551234",
  "request": "Website design",
  "notes": ""
}
```

Both requests are valid.

---

## Example with cURL for PowerShell

```powershell
$jsonData = @{
    name = "Angeles Medina"
    email = "rjasbd5@gmail.com"
    phone = "4125647789"
    request = "I just want to know how much a website will cost"
    notes = ""
} | ConvertTo-Json

$url = "http://localhost:8000/leads"

curl -Uri $url `
     -Method POST `
     -Body $jsonData `
     -ContentType "application/json"
```

---

## Example Response

```json
{
  "message": "Lead created successfully",
  "id": 1,
  "temperature": "Hot"
}
```

If classification fails, the lead is preserved with:

```text
pending
```

---

## Validation

Pydantic validates the request before it reaches the database.

For example, this request is invalid because `request` is missing:

```json
{
  "name": "Juan",
  "email": "juan@example.com",
  "phone": "8095551234",
  "notes": ""
}
```

FastAPI returns:

```http
422 Unprocessable Entity
```

The same applies if `notes` is omitted because it is a required field.

An invalid email format is also rejected:

```json
{
  "name": "Juan",
  "email": "not-an-email",
  "phone": "8095551234",
  "request": "Website design",
  "notes": ""
}
```

---

## Error Handling

The API handles failures according to the stage where they occur.

| Component            | How it fails                            | What happens today                                             | What should happen                                  |
| -------------------- | --------------------------------------- | -------------------------------------------------------------- | --------------------------------------------------- |
| Pydantic             | Required field missing or invalid data  | Returns `422 Unprocessable Entity` and does not store the lead | Reject invalid input before application logic       |
| SQLite / SQLAlchemy  | Duplicate email                         | Rolls back the transaction and returns `409 Conflict`          | Preserve database integrity and report the conflict |
| LLM                  | Model/API failure during classification | Lead remains stored with `pending` classification              | Prevent AI failures from causing data loss          |
| Database transaction | Database operation fails                | `rollback()` reverts the failed transaction                    | Keep the database session consistent                |

---

## Database Integrity

Each lead is identified by its stored information, including a unique email constraint.

If a lead is submitted using an email that already exists, SQLAlchemy raises an integrity error.

The application handles the error by:

1. Catching the integrity error.
2. Calling `rollback()`.
3. Returning `409 Conflict`.

This prevents the failed transaction from leaving the SQLAlchemy session in an unusable state.

---

## LLM Error Handling

The lead is persisted before the classification process.

If `classify_lead()` successfully communicates with the LLM, the classification is stored as either:

```text
Hot
```

or:

```text
Cold
```

If the LLM fails, the lead remains in SQLite and its classification becomes:

```text
pending
```

This behavior was tested to verify that model failures do not result in lead loss.

---

## HTTP Status Codes

| Status Code                | Meaning                                        | Example in this project                        |
| -------------------------- | ---------------------------------------------- | ---------------------------------------------- |
| `201 Created`              | Resource was successfully created              | Lead successfully created                      |
| `409 Conflict`             | Request conflicts with existing resource/state | Duplicate email                                |
| `422 Unprocessable Entity` | Request does not satisfy validation rules      | Missing required field or invalid field format |

---

## Database

The project uses SQLite with SQLAlchemy to persist leads.

The database stores:

* Original lead information
* LLM classification

Database operations are handled through SQLAlchemy sessions.

Successful transactions use:

```python
db.commit()
```

Failed transactions use:

```python
db.rollback()
```

---

## What I Learned

This project focuses on understanding the backend fundamentals behind AI-powered systems.

Key concepts practiced:

* HTTP requests
* HTTP status codes
* REST API architecture
* FastAPI
* Pydantic validation
* SQLAlchemy
* SQLite
* Database sessions
* ORM models
* Database transactions
* `commit()`
* `rollback()`
* Integrity errors
* Environment variables
* LLM API integration
* Model initialization
* LLM error handling
* JSON request/response structures
* Separation between API, database, and AI logic

---

## Verified Error Scenarios

The following scenarios were implemented and tested:

### Missing required field

Pydantic rejects requests that do not contain all required fields.

**Result:** `422 Unprocessable Entity`

### Duplicate email

Submitting a lead with an email that already exists triggers the database integrity handling.

**Result:** `rollback()` + `409 Conflict`

### LLM classification failure

A model failure does not delete or prevent the lead from being stored.

**Result:** lead preserved with `pending` classification.

### Model initialization

The LLM is initialized inside:

```python
classify_lead()
```

This means it is initialized when classification is actually required rather than when the API starts.

---

## Running the Project

### 1. Clone the repository

```bash
git clone https://github.com/SoyColde/lead_capture_api
cd lead_capture_api
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file:

```env
LLM_API_KEY=your_api_key_here
```

### 5. Start the API

```bash
uvicorn main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

FastAPI interactive documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Project Goal

This project is not just about creating a lead form.

The objective is to understand how to build the **backend layer that AI agents and automation systems depend on**.

The long-term direction is to evolve from simple APIs into systems where AI can:

```text
Receive information
       ↓
Understand it
       ↓
Make a decision
       ↓
Call external systems
       ↓
Perform an action
       ↓
Store the result
       ↓
Continue the workflow
```

This API represents one of the first steps toward building more complex **agentic AI systems**.

---

## Author

**Colde**

ITLA — Artificial Intelligence

**Road to Agentic AI**
