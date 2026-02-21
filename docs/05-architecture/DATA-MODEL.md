# Data Model

## Overview

The data model is designed around the core entities of the Journey Buddi system: Users, Trips, Itineraries, Activities, Conversations, and Conditions. PostgreSQL with PostGIS provides the relational backbone with geospatial capabilities.

## Entity Relationship Diagram

```
┌──────────┐     ┌──────────┐     ┌──────────────┐
│   User   │────<│   Trip   │────<│  Itinerary   │
└──────────┘     └──────────┘     └──────┬───────┘
                                         │
                                    ┌────┴─────┐
                                    │          │
                              ┌─────▼──┐  ┌───▼──────┐
                              │  Day   │  │Transport │
                              │        │  │Segment   │
                              └───┬────┘  └──────────┘
                                  │
                            ┌─────▼──────┐
                            │  Activity  │
                            │  Instance  │
                            └─────┬──────┘
                                  │
                            ┌─────▼──────┐
                            │  Activity  │
                            │  Template  │
                            └────────────┘

┌──────────┐     ┌──────────────┐
│   User   │────<│ Conversation │
└──────────┘     └──────┬───────┘
                        │
                   ┌────▼─────┐
                   │ Message  │
                   └──────────┘

┌──────────────┐  ┌──────────────┐
│  Condition   │  │  Attraction  │
│  Record      │  │  (Template)  │
└──────────────┘  └──────────────┘
```

## Core Tables

### users

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE,
    preferences JSONB DEFAULT '{}'::jsonb,
    profile JSONB DEFAULT '{}'::jsonb
);
```

**`profile` JSONB structure:**
```json
{
  "adventure_level": "moderate",
  "fitness_level": "moderate",
  "pace": "balanced",
  "interests": ["wildlife", "mountains", "hiking", "photography"],
  "activity_budget": "medium",
  "notification_preferences": {
    "morning_briefing_time": "07:00",
    "evening_preview_time": "20:00",
    "quiet_hours_start": "21:00",
    "quiet_hours_end": "06:30"
  }
}
```

### trips

```sql
CREATE TABLE trips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    destination VARCHAR(100) NOT NULL,
    destination_region VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'planning',
    -- status: planning, confirmed, active, completed, archived
    start_date DATE,
    end_date DATE,
    entry_point VARCHAR(100),
    exit_point VARCHAR(100),
    transport_plan JSONB DEFAULT '{}'::jsonb,
    planning_state JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_trips_user_id ON trips(user_id);
CREATE INDEX idx_trips_status ON trips(status);
```

### itineraries

```sql
CREATE TABLE itineraries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    version INTEGER NOT NULL DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT true,
    total_days INTEGER NOT NULL,
    summary JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(trip_id, version)
);
```

### itinerary_days

```sql
CREATE TABLE itinerary_days (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    itinerary_id UUID NOT NULL REFERENCES itineraries(id) ON DELETE CASCADE,
    day_number INTEGER NOT NULL,
    date DATE NOT NULL,
    title VARCHAR(255) NOT NULL,
    location_name VARCHAR(255),
    location_point GEOGRAPHY(Point, 4326),
    cluster_name VARCHAR(100),
    day_type VARCHAR(20) NOT NULL DEFAULT 'activity',
    -- day_type: activity, travel, flex, arrival, departure
    transport JSONB DEFAULT '{}'::jsonb,
    accommodation_zone VARCHAR(255),
    notes TEXT,
    buddi_tips TEXT[],
    is_locked BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(itinerary_id, day_number)
);

CREATE INDEX idx_days_itinerary ON itinerary_days(itinerary_id);
CREATE INDEX idx_days_date ON itinerary_days(date);
```

### activity_instances

```sql
CREATE TABLE activity_instances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    day_id UUID NOT NULL REFERENCES itinerary_days(id) ON DELETE CASCADE,
    attraction_id UUID REFERENCES attractions(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    duration_hours DECIMAL(4,2),
    time_of_day VARCHAR(20),
    -- time_of_day: morning, midday, afternoon, evening, flexible
    suggested_start TIME,
    location_name VARCHAR(255),
    location_point GEOGRAPHY(Point, 4326),
    weather_sensitivity VARCHAR(20) DEFAULT 'moderate',
    conditions_needed JSONB DEFAULT '{}'::jsonb,
    packing_notes TEXT[],
    pro_tips TEXT[],
    swap_priority VARCHAR(10) DEFAULT 'medium',
    sort_order INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(20) DEFAULT 'planned',
    -- status: planned, active, completed, skipped, swapped
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_activities_day ON activity_instances(day_id);
```

### attractions

```sql
CREATE TABLE attractions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    destination VARCHAR(100) NOT NULL,
    region VARCHAR(100),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    types TEXT[] NOT NULL,
    location_name VARCHAR(255),
    location_point GEOGRAPHY(Point, 4326),
    difficulty VARCHAR(20),
    cost_level VARCHAR(20),
    duration_min DECIMAL(4,2),
    duration_max DECIMAL(4,2),
    seasonal_availability VARCHAR(50) DEFAULT 'year-round',
    booking_required BOOLEAN DEFAULT false,
    weather_sensitivity VARCHAR(20) DEFAULT 'moderate',
    ideal_conditions JSONB DEFAULT '{}'::jsonb,
    acceptable_conditions JSONB DEFAULT '{}'::jsonb,
    dealbreaker_conditions JSONB DEFAULT '{}'::jsonb,
    logistics JSONB DEFAULT '{}'::jsonb,
    uniqueness_score INTEGER DEFAULT 50,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_attractions_destination ON attractions(destination);
CREATE INDEX idx_attractions_types ON attractions USING GIN(types);
CREATE INDEX idx_attractions_location ON attractions USING GIST(location_point);
```

### conversations

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    trip_id UUID REFERENCES trips(id),
    type VARCHAR(20) NOT NULL DEFAULT 'planning',
    -- type: planning, companion, general
    state JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_conversations_user ON conversations(user_id);
CREATE INDEX idx_conversations_trip ON conversations(trip_id);
```

### messages

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    -- role: user, assistant, system
    content TEXT NOT NULL,
    structured_data JSONB,
    -- For choice selections, card interactions, etc.
    token_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_created ON messages(created_at);
```

### condition_records

```sql
CREATE TABLE condition_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    location_name VARCHAR(255),
    location_point GEOGRAPHY(Point, 4326),
    recorded_at TIMESTAMP WITH TIME ZONE NOT NULL,
    forecast_for TIMESTAMP WITH TIME ZONE NOT NULL,
    source VARCHAR(50) NOT NULL,
    data JSONB NOT NULL,
    -- Contains: temperature, precipitation, wind, cloud_cover, 
    -- visibility, humidity, uv_index, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_conditions_location ON condition_records USING GIST(location_point);
CREATE INDEX idx_conditions_forecast ON condition_records(forecast_for);
CREATE INDEX idx_conditions_source ON condition_records(source);
```

### swap_suggestions

```sql
CREATE TABLE swap_suggestions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID NOT NULL REFERENCES trips(id),
    original_day_id UUID NOT NULL REFERENCES itinerary_days(id),
    swap_day_id UUID NOT NULL REFERENCES itinerary_days(id),
    improvement_score INTEGER NOT NULL,
    disruption_score INTEGER NOT NULL,
    reasoning TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    -- status: pending, accepted, declined, expired
    user_response_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_swaps_trip ON swap_suggestions(trip_id);
```

### daily_briefings

```sql
CREATE TABLE daily_briefings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID NOT NULL REFERENCES trips(id),
    day_id UUID NOT NULL REFERENCES itinerary_days(id),
    content JSONB NOT NULL,
    -- Full structured briefing content
    conditions_snapshot JSONB NOT NULL,
    -- Conditions at time of generation
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    delivered_at TIMESTAMP WITH TIME ZONE,
    viewed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_briefings_trip ON daily_briefings(trip_id);
CREATE INDEX idx_briefings_day ON daily_briefings(day_id);
```

## Geospatial Queries

PostGIS enables efficient spatial queries:

```sql
-- Find attractions within 50km of a point
SELECT * FROM attractions
WHERE ST_DWithin(
    location_point,
    ST_GeogFromText('POINT(172.6362 -43.5321)'),
    50000  -- meters
);

-- Calculate distance between two attractions
SELECT ST_Distance(a1.location_point, a2.location_point)
FROM attractions a1, attractions a2
WHERE a1.slug = 'kaikoura-dolphins' AND a2.slug = 'kaikoura-whales';

-- Find attractions along a route (within 20km of a linestring)
SELECT * FROM attractions
WHERE ST_DWithin(
    location_point,
    ST_GeogFromText('LINESTRING(...)'),
    20000
);
```

## Migration Strategy

Using Alembic for database migrations:

```bash
# Create migration
alembic revision --autogenerate -m "add_attractions_table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

All schema changes go through migrations — never modify the database directly.
