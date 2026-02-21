# Real-Time System

## Overview

Journey Buddi has several real-time requirements that go beyond traditional request-response HTTP. This document covers the WebSocket architecture for chat streaming, the background task system for condition monitoring and briefing generation, and the push notification delivery system.

## WebSocket Architecture

### Chat Streaming

The AI chat uses WebSockets to stream responses token-by-token, creating a natural "typing" effect.

**Connection lifecycle:**
```
1. Client opens WebSocket: ws://api/v1/ws/chat/{conversation_id}
2. Server authenticates via JWT in query parameter or first message
3. Connection established — bidirectional messaging begins
4. Client sends user messages
5. Server streams AI responses (token by token)
6. Connection kept alive with heartbeats (every 30s)
7. Client disconnects or connection times out (5 min idle)
```

**Server-side implementation (FastAPI):**
```python
@app.websocket("/api/v1/ws/chat/{conversation_id}")
async def chat_websocket(websocket: WebSocket, conversation_id: str):
    await websocket.accept()
    
    # Authenticate
    user = await authenticate_ws(websocket)
    
    try:
        while True:
            # Receive user message
            data = await websocket.receive_json()
            
            # Process through AI agent
            async for token in ai_agent.stream_response(
                conversation_id=conversation_id,
                user_message=data,
                user_profile=user.profile
            ):
                await websocket.send_json({
                    "type": "stream_token",
                    "token": token
                })
            
            # Send completion signal with structured data
            await websocket.send_json({
                "type": "stream_end",
                "structured_data": ai_agent.get_structured_output()
            })
    except WebSocketDisconnect:
        # Clean up
        pass
```

### Connection Management

- **Reconnection**: Client should auto-reconnect on disconnect with exponential backoff
- **Session recovery**: On reconnect, client sends last received message ID to avoid duplicates
- **Concurrent connections**: Only one active WebSocket per conversation per user
- **Timeout**: Connections idle >5 minutes are closed server-side

## Background Task System

### Celery Configuration

```python
celery_app = Celery(
    'journey_buddi',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
    task_routes={
        'tasks.briefing.*': {'queue': 'briefings'},
        'tasks.monitoring.*': {'queue': 'monitoring'},
        'tasks.notifications.*': {'queue': 'notifications'},
    }
)
```

### Scheduled Tasks

```python
celery_app.conf.beat_schedule = {
    'condition-refresh': {
        'task': 'tasks.monitoring.refresh_conditions',
        'schedule': 3600.0,  # Every hour
    },
    'check-briefing-schedule': {
        'task': 'tasks.briefing.check_and_generate',
        'schedule': 300.0,  # Every 5 minutes (checks user timezones)
    },
    'condition-alert-check': {
        'task': 'tasks.monitoring.check_alerts',
        'schedule': 1800.0,  # Every 30 minutes
    },
}
```

### Task Definitions

**Morning Briefing Generation:**
```python
@celery_app.task(bind=True, max_retries=3)
def generate_morning_briefing(self, trip_id: str, day_number: int):
    """Generate and deliver the morning briefing for a trip day."""
    try:
        # 1. Load trip and itinerary data
        trip = get_trip(trip_id)
        day = get_itinerary_day(trip_id, day_number)
        
        # 2. Fetch fresh conditions
        conditions = fetch_conditions(day.activities)
        
        # 3. Score each activity
        assessments = score_activities(day.activities, conditions)
        
        # 4. Check for swap opportunities if needed
        swap = None
        if any(a.score < 50 for a in assessments):
            swap = evaluate_swaps(trip_id, day_number)
        
        # 5. Generate briefing via AI
        briefing = ai_generate_briefing(
            day=day,
            conditions=conditions,
            assessments=assessments,
            swap=swap,
            user_profile=trip.user.profile
        )
        
        # 6. Store briefing
        store_briefing(trip_id, day_number, briefing)
        
        # 7. Send notification
        send_push_notification(
            user_id=trip.user_id,
            title=f"Day {day_number} Briefing",
            body=briefing.summary_line,
            data={"trip_id": trip_id, "day": day_number}
        )
    except Exception as exc:
        self.retry(exc=exc, countdown=60)
```

**Condition Monitoring:**
```python
@celery_app.task
def refresh_conditions():
    """Refresh condition data for all active trips."""
    active_trips = get_active_trips()
    
    for trip in active_trips:
        # Get locations for next 5 days
        upcoming_days = get_upcoming_days(trip.id, days_ahead=5)
        locations = extract_unique_locations(upcoming_days)
        
        for location in locations:
            # Fetch and cache weather data
            weather = fetch_weather(location, days_ahead=5)
            cache_conditions(location, weather)
            
            # Fetch tide data if coastal
            if is_coastal(location):
                tides = fetch_tides(location, days_ahead=5)
                cache_conditions(location, tides, type='tides')
```

**Alert Checking:**
```python
@celery_app.task
def check_alerts():
    """Check for significant condition changes on active trips."""
    active_trips = get_active_trips()
    
    for trip in active_trips:
        today = get_today_plan(trip.id)
        
        for activity in today.activities:
            previous = get_cached_assessment(activity.id)
            current = assess_conditions(activity)
            
            if significant_change(previous, current):
                if current.assessment in ['poor', 'unsafe']:
                    # Trigger alert
                    trigger_condition_alert(trip.id, activity, current)
                elif current.assessment == 'excellent' and previous.assessment in ['fair', 'poor']:
                    # Conditions improved — opportunity!
                    trigger_opportunity_alert(trip.id, activity, current)
```

## Push Notification System

### Web Push (PWA)

**Registration flow:**
1. Client requests notification permission
2. Browser generates a push subscription (endpoint + keys)
3. Client sends subscription to server
4. Server stores subscription for the user
5. When notification needed, server sends push via subscription endpoint

**Server-side push (using pywebpush):**
```python
from pywebpush import webpush

def send_push_notification(user_id: str, title: str, body: str, data: dict = None):
    subscription = get_user_push_subscription(user_id)
    if not subscription:
        return  # User hasn't enabled push
    
    payload = {
        "title": title,
        "body": body,
        "icon": "/icons/buddi-icon-192.png",
        "badge": "/icons/buddi-badge-72.png",
        "data": data or {},
        "tag": f"buddi-{data.get('type', 'general')}",
    }
    
    webpush(
        subscription_info=subscription,
        data=json.dumps(payload),
        vapid_private_key=VAPID_PRIVATE_KEY,
        vapid_claims={"sub": "mailto:notifications@journeybuddi.com"}
    )
```

### Notification Scheduling

Notifications are scheduled based on user timezone and preferences:

```python
def schedule_briefing_notification(trip_id: str, day_number: int):
    trip = get_trip(trip_id)
    user = get_user(trip.user_id)
    
    # Get user's preferred briefing time in their timezone
    briefing_time = user.profile['notification_preferences']['morning_briefing_time']
    user_tz = get_trip_timezone(trip)
    
    # Convert to UTC for scheduling
    local_time = datetime.combine(
        get_day_date(trip_id, day_number),
        time.fromisoformat(briefing_time)
    )
    utc_time = local_time.astimezone(timezone.utc)
    
    # Schedule Celery task
    generate_morning_briefing.apply_async(
        args=[trip_id, day_number],
        eta=utc_time - timedelta(minutes=5)  # Generate 5 min early
    )
```

## Event System (Internal)

For loose coupling between services, internal events are published through a simple event bus:

```python
class EventBus:
    async def publish(self, event_type: str, data: dict):
        """Publish event to registered handlers."""
        
    async def subscribe(self, event_type: str, handler: Callable):
        """Register handler for event type."""

# Events:
# trip.created
# trip.activated
# trip.completed
# itinerary.generated
# itinerary.updated
# swap.suggested
# swap.accepted
# swap.declined
# conditions.changed
# briefing.generated
# notification.sent
```

This is implemented in-process for MVP (simple pub/sub). Can be migrated to a proper message broker (RabbitMQ, Redis Streams) when scaling.

## Data Freshness Summary

| Data | Source | Refresh Rate | Cache TTL |
|------|--------|-------------|-----------|
| Weather (current) | Weather API | 1 hour | 30 min |
| Weather (forecast) | Weather API | 3 hours | 1 hour |
| Tides | Tides API | Daily | 12 hours |
| Solar (sunrise/set) | Solar API | Daily | 24 hours |
| Aurora (Kp index) | NOAA | 3 hours | 1 hour |
| Itinerary | Database | Real-time | N/A |
| User profile | Database | Real-time | N/A |
| Knowledge base | Vector store | Static | N/A |
