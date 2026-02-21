# API Design

## Overview

The Journey Buddi API follows RESTful conventions for resource management and WebSocket for real-time communication (chat streaming). All endpoints are versioned under `/api/v1/`.

## Base URL

```
Production:  https://api.journeybuddi.com/api/v1
Development: http://localhost:8000/api/v1
```

## Authentication

All endpoints (except auth) require a valid JWT token in the `Authorization` header:

```
Authorization: Bearer <jwt_token>
```

### Auth Endpoints

```
POST   /api/v1/auth/magic-link     Send magic link email
POST   /api/v1/auth/verify          Verify magic link token, return JWT
POST   /api/v1/auth/refresh          Refresh JWT token
POST   /api/v1/auth/logout           Invalidate session
```

**POST /auth/magic-link**
```json
Request:  { "email": "user@example.com" }
Response: { "message": "Magic link sent", "expires_in": 900 }
```

**POST /auth/verify**
```json
Request:  { "token": "abc123..." }
Response: { 
  "access_token": "jwt...", 
  "user": { "id": "uuid", "email": "user@example.com", "name": null }
}
```

## User Endpoints

```
GET    /api/v1/users/me              Get current user profile
PATCH  /api/v1/users/me              Update user profile/preferences
```

**PATCH /users/me**
```json
Request: {
  "name": "Daniel",
  "profile": {
    "adventure_level": "moderate",
    "fitness_level": "moderate",
    "pace": "balanced",
    "interests": ["wildlife", "mountains", "hiking"],
    "activity_budget": "medium"
  }
}
```

## Trip Endpoints

```
POST   /api/v1/trips                 Create a new trip
GET    /api/v1/trips                 List user's trips
GET    /api/v1/trips/:id             Get trip details
PATCH  /api/v1/trips/:id             Update trip
DELETE /api/v1/trips/:id             Delete trip
POST   /api/v1/trips/:id/activate    Set trip to active (start companion mode)
POST   /api/v1/trips/:id/complete    Mark trip as completed
```

**POST /trips**
```json
Request: {
  "destination": "new-zealand",
  "destination_region": "south-island",
  "start_date": "2026-12-05",
  "end_date": "2026-12-23",
  "entry_point": "christchurch",
  "exit_point": "christchurch"
}
Response: {
  "id": "trip-uuid",
  "status": "planning",
  ...
}
```

## Itinerary Endpoints

```
GET    /api/v1/trips/:tripId/itinerary           Get active itinerary
POST   /api/v1/trips/:tripId/itinerary/generate   Generate itinerary from planning data
PATCH  /api/v1/trips/:tripId/itinerary            Update itinerary
GET    /api/v1/trips/:tripId/itinerary/days        Get all days
GET    /api/v1/trips/:tripId/itinerary/days/:dayNum  Get specific day
PATCH  /api/v1/trips/:tripId/itinerary/days/:dayNum  Update a day
POST   /api/v1/trips/:tripId/itinerary/swap        Apply a day swap
```

**GET /trips/:tripId/itinerary/days/:dayNum**
```json
Response: {
  "day_number": 7,
  "date": "2026-12-11",
  "title": "Kaikoura — Dolphins & Whales",
  "location": { "name": "Kaikoura", "lat": -42.4008, "lon": 173.6810 },
  "day_type": "activity",
  "activities": [
    {
      "id": "act-uuid",
      "name": "Dolphin Swimming",
      "description": "Swim with dusky dolphins...",
      "duration_hours": 3.0,
      "time_of_day": "morning",
      "suggested_start": "09:15",
      "weather_sensitivity": "moderate",
      "conditions": null,
      "status": "planned"
    }
  ],
  "transport": {
    "mode": "campervan",
    "distance_km": 0,
    "notes": "Based in Kaikoura — no driving today"
  },
  "packing_list": null,
  "briefing": null
}
```

## Condition Endpoints

```
GET    /api/v1/conditions/current    Get current conditions for a location
GET    /api/v1/conditions/forecast   Get forecast for a location + date range
GET    /api/v1/conditions/assess     Assess conditions for a specific activity
```

**GET /conditions/assess?activity_id=X&date=2026-12-11**
```json
Response: {
  "activity": "Dolphin Swimming",
  "date": "2026-12-11",
  "overall_score": 85,
  "assessment": "excellent",
  "factors": {
    "wind": { "value": "12 km/h", "score": 90, "note": "Calm, perfect for boat" },
    "sea_state": { "value": "0.5m", "score": 95, "note": "Very calm water" },
    "rain": { "value": "5%", "score": 95, "note": "Dry" },
    "temperature": { "value": "18°C", "score": 80, "note": "Comfortable" }
  }
}
```

## Briefing Endpoints

```
GET    /api/v1/trips/:tripId/briefings              List all briefings
GET    /api/v1/trips/:tripId/briefings/today         Get today's briefing
GET    /api/v1/trips/:tripId/briefings/:dayNum       Get briefing for specific day
POST   /api/v1/trips/:tripId/briefings/:dayNum/regenerate  Force regeneration
```

## Swap Endpoints

```
GET    /api/v1/trips/:tripId/swaps                   List swap suggestions
GET    /api/v1/trips/:tripId/swaps/:id               Get swap details
POST   /api/v1/trips/:tripId/swaps/:id/accept        Accept a swap
POST   /api/v1/trips/:tripId/swaps/:id/decline       Decline a swap
```

## Chat / Conversation Endpoints

### REST Endpoints
```
GET    /api/v1/conversations                         List conversations
POST   /api/v1/conversations                         Create conversation
GET    /api/v1/conversations/:id/messages             Get message history
```

### WebSocket Endpoint
```
WS     /api/v1/ws/chat/:conversationId               Real-time chat
```

**WebSocket Protocol:**

Client → Server:
```json
{
  "type": "message",
  "content": "I'd like to add dolphin swimming",
  "structured_data": null
}
```

```json
{
  "type": "selection",
  "content": null,
  "structured_data": {
    "choice_id": "adventure_level",
    "selected": "moderate"
  }
}
```

Server → Client:
```json
{
  "type": "stream_start",
  "message_id": "msg-uuid"
}
```

```json
{
  "type": "stream_token",
  "message_id": "msg-uuid",
  "token": "Great "
}
```

```json
{
  "type": "stream_end",
  "message_id": "msg-uuid",
  "full_content": "Great choice! Dolphins in Kaikoura...",
  "structured_data": {
    "type": "choice_card",
    "choices": [...]
  }
}
```

## Attraction Endpoints

```
GET    /api/v1/attractions                           List/search attractions
GET    /api/v1/attractions/:slug                     Get attraction details
GET    /api/v1/attractions/:slug/tips                Get pro tips
```

**GET /attractions?destination=new-zealand&types=wildlife&region=south-island**

## Error Handling

All errors follow a consistent format:

```json
{
  "error": {
    "code": "TRIP_NOT_FOUND",
    "message": "Trip with the specified ID was not found",
    "details": {}
  }
}
```

### HTTP Status Codes

| Code | Usage |
|------|-------|
| 200 | Success |
| 201 | Resource created |
| 400 | Invalid request data |
| 401 | Not authenticated |
| 403 | Not authorized |
| 404 | Resource not found |
| 422 | Validation error |
| 429 | Rate limited |
| 500 | Server error |

## Rate Limiting

| Endpoint Type | Limit | Window |
|--------------|-------|--------|
| Auth | 5 requests | 15 minutes |
| REST API | 100 requests | 1 minute |
| WebSocket messages | 30 messages | 1 minute |
| Briefing regeneration | 5 requests | 1 hour |

Rate limit headers included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

## Pagination

List endpoints support cursor-based pagination:

```
GET /api/v1/attractions?cursor=abc123&limit=20

Response: {
  "data": [...],
  "pagination": {
    "next_cursor": "def456",
    "has_more": true,
    "total": 150
  }
}
```
