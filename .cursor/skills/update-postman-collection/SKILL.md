---
name: update-postman-collection
description: Maintains the Journey Buddi Postman collection and environment files. Use when adding, removing, or modifying API endpoints, adding new environment variables, creating new folders/categories, or when the user asks to update, sync, or regenerate the Postman collection.
---

# Update Journey Buddi Postman Collection

## Files

| File | Purpose |
|---|---|
| `postman/Journey_Buddi.postman_collection.json` | Main collection — all requests, folders, auth, test scripts |
| `postman/environments/Journey_Buddi_DEV.postman_environment.json` | Local (`http://localhost:8000`) |
| `postman/environments/Journey_Buddi_STG.postman_environment.json` | Railway staging |
| `postman/environments/Journey_Buddi_PROD.postman_environment.json` | Railway production |

**Always read the collection file before editing.** It is ~1000 lines — read in full.

---

## Collection Conventions (critical — never break these)

### Auth
- **Collection-level auth** is Bearer `{{access_token}}`. All protected routes **inherit** this automatically — do NOT add auth to protected request objects.
- **Public routes** (no JWT needed) must explicitly override: `"auth": { "type": "noauth" }`.
- Current public routes: `GET /health`, `POST /auth/magic-link`, `POST /auth/verify`, `POST /auth/logout`, all `/attractions/*`.

### Variables
All dynamic values use `{{variable_name}}` syntax. Core variables:

| Variable | Source |
|---|---|
| `{{base_url}}` | Environment file — never hardcode URLs |
| `{{access_token}}` | Auto-captured by Verify Magic Link test script |
| `{{trip_id}}` | Auto-captured by Create Trip test script |
| `{{conversation_id}}` | Auto-captured by Create Conversation test script |
| `{{swap_id}}` | Auto-captured by List Swap Suggestions test script |
| `{{attraction_slug}}` | Set manually in environment |
| `{{day_number}}` | Set manually in environment |
| `{{user_email}}` | Set manually in environment |

### Test Scripts (auto-capture pattern)
Responses that return a new resource ID **must** save it to the environment:

```json
"event": [
  {
    "listen": "test",
    "script": {
      "exec": [
        "pm.test('Status 201', () => pm.response.to.have.status(201));",
        "",
        "const body = pm.response.json();",
        "if (body.id) {",
        "  pm.environment.set('some_id', body.id);",
        "  console.log('✅ some_id saved:', body.id);",
        "}"
      ],
      "type": "text/javascript"
    }
  }
]
```

Minimum test for every request:
```json
"event": [
  {
    "listen": "test",
    "script": {
      "exec": ["pm.test('Status 200', () => pm.response.to.have.status(200));"],
      "type": "text/javascript"
    }
  }
]
```

---

## Postman Collection v2.1 — JSON Structure Reference

### Collection skeleton
```json
{
  "info": { "name": "...", "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json" },
  "auth": { "type": "bearer", "bearer": [{ "key": "token", "value": "{{access_token}}", "type": "string" }] },
  "variable": [ { "key": "...", "value": "...", "description": "..." } ],
  "item": [ /* folders */ ]
}
```

### Folder object
```json
{
  "name": "Folder Name",
  "description": "What this group covers.",
  "item": [ /* request objects */ ]
}
```

### Request object (full shape)
```json
{
  "name": "Human-readable name",
  "request": {
    "auth": { "type": "noauth" },        // ONLY for public routes
    "method": "POST",
    "header": [{ "key": "Content-Type", "value": "application/json" }],
    "body": {
      "mode": "raw",
      "raw": "{\n  \"field\": \"value\"\n}",
      "options": { "raw": { "language": "json" } }
    },
    "url": {
      "raw": "{{base_url}}/api/v1/resource/{{variable}}",
      "host": ["{{base_url}}"],
      "path": ["api", "v1", "resource", "{{variable}}"],
      "query": [
        { "key": "param", "value": "value", "description": "..." },
        { "key": "optional", "value": "", "disabled": true }
      ]
    },
    "description": "What this endpoint does, notable errors, notes."
  },
  "event": [ /* test scripts */ ],
  "response": []
}
```

- **Omit `auth`** entirely on protected routes (they inherit from collection).
- **Omit `header`** if no body (GET/DELETE).
- **Omit `body`** on GET/DELETE/no-body POSTs — or set `"mode": "raw", "raw": ""`.
- **Omit `query`** if no query params.
- `"response": []` is always an empty array.

### Environment variable object
```json
{ "key": "var_name", "value": "default_value", "type": "default", "enabled": true, "description": "..." }
```
Use `"type": "secret"` for `access_token` only.

---

## Step-by-Step: Adding a New Endpoint

1. **Identify the folder** — find the matching `item` folder in the collection by `"name"`. If no folder exists, add one (see below).

2. **Build the request object** using the shape above. Key checklist:
   - [ ] Correct HTTP method
   - [ ] URL uses `{{base_url}}` and path variables use `{{variable_name}}`
   - [ ] `"auth": {"type": "noauth"}` if public; omitted if protected
   - [ ] `Content-Type` header only when body is present
   - [ ] Body formatted with `\n` and `  ` indentation (2 spaces) inside the `raw` string
   - [ ] At least one test asserting the expected status code
   - [ ] Auto-capture script if endpoint returns a new resource ID

3. **Append** the request object to the folder's `"item"` array.

4. **If the endpoint uses a new path variable** (e.g., `{{new_id}}`):
   - Add it to the collection `"variable"` array
   - Add it to all 3 environment files

5. **Validate** (see below).

---

## Step-by-Step: Adding a New Folder

Add a new object to the top-level `"item"` array:

```json
{
  "name": "New Domain",
  "description": "Brief description of this API group.",
  "item": []
}
```

Insert in logical order (e.g., after the most related existing folder).

---

## Step-by-Step: Adding a New Environment Variable

When a new variable is needed across environments:

1. Add to collection `"variable"` array (use a sensible default or empty string).
2. Add to **all 3 environment files** — same `key`, environment-appropriate `value`.

Do not add secrets (API keys, passwords) as plain text values in any file. Leave `value` empty and document in `description`.

---

## Step-by-Step: Removing an Endpoint or Folder

1. Delete the request object from the folder's `"item"` array.
2. If the folder is now empty, delete the folder object too.
3. If a variable is now unused, remove it from the collection `"variable"` array and all 3 environment files.

---

## Validation

After every edit, run:

```bash
python3 -c "import json; json.load(open('postman/Journey_Buddi.postman_collection.json')); print('✅ Collection JSON valid')"
python3 -c "import json; [json.load(open(f'postman/environments/Journey_Buddi_{e}.postman_environment.json')) for e in ['DEV','STG','PROD']]; print('✅ All environment files valid')"
```

Run from the `journey-buddi/` project root. Fix any JSON errors before finishing.

---

## Folder Order (maintain this order)

1. Health
2. Auth
3. Users
4. Trips
5. Conversations
6. Attractions
7. Itinerary
8. Conditions
9. Briefings

New domains go at the end unless there is a clear reason to insert them earlier.

---

## Common Mistakes

- **Hardcoding `localhost:8000`** — always use `{{base_url}}`.
- **Adding auth to protected routes** — they inherit; adding it is redundant and misleading.
- **Forgetting `noauth` on public routes** — they will silently send a bearer token header.
- **Missing `Content-Type` header** on POST/PATCH with a body — FastAPI returns 422.
- **Not updating all 3 environment files** when adding a new variable.
- **Invalid JSON** — trailing commas, unescaped quotes in raw strings. Always validate after editing.
