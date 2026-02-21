# Notification System

## Overview

Notifications are Buddi's primary proactive communication channel during the trip. They need to be valuable enough that the traveler looks forward to them, while restrained enough that they never feel intrusive. Getting this balance right is crucial to the user experience.

## Notification Types

### 1. Morning Briefing
**Priority:** Normal
**Timing:** Configurable, default 7:00 AM local
**Frequency:** Daily during active trip
**Content:** Summary of the day with condition assessment

```
Journey Buddi — Day 7 ☀️
🟢 Great day for whale watching and coastal walks in Kaikoura! 
Conditions are excellent. Tap for your full briefing →
```

### 2. Evening Preview
**Priority:** Low
**Timing:** Configurable, default 8:00 PM local
**Frequency:** Daily during active trip
**Content:** Brief preview of tomorrow + packing reminder

```
Journey Buddi — Tomorrow's Preview 🌙
Tomorrow you're heading to Abel Tasman for kayaking! 
🎒 Pack: swimsuit, quick-dry clothes, water shoes, sunscreen
⏰ Depart by 7:30 AM for the 8:45 AM kayak launch
```

### 3. Swap Suggestion
**Priority:** High
**Timing:** Evening before or early morning of affected day
**Frequency:** Only when conditions warrant (typically 0-3 times per trip)
**Content:** Clear swap proposal with reasoning

```
Journey Buddi — Itinerary Suggestion 🔄
Tomorrow's Tongariro Crossing conditions look poor (65km/h wind, rain).
I have a better plan — tap to see my suggestion →
```

### 4. Condition Alert
**Priority:** Urgent (safety) or High (quality)
**Timing:** As soon as detected
**Frequency:** Only for significant changes
**Content:** What changed and what to do

```
🟡 Weather Update for Today
Afternoon rain now expected from 2 PM (was clear earlier). 
Your Peninsula Walkway is best done this morning instead. 
Tap for adjusted timing →
```

### 5. Activity Reminder
**Priority:** Normal
**Timing:** 1-2 hours before suggested departure time
**Frequency:** Per-activity during the day
**Content:** Departure reminder with key prep items

```
Journey Buddi ⏰
Time to head to Whale Watch Kaikoura! 
Depart by 8:30 AM for your 9:15 AM tour.
Don't forget: warm layer, sunscreen, motion sickness tablet (take now!)
```

### 6. Opportunity Alert
**Priority:** Low
**Timing:** When a special condition is detected
**Frequency:** Rare (0-2 per trip)
**Content:** Spontaneous suggestion based on exceptional conditions

```
Journey Buddi ✨
Clear skies tonight + high aurora activity forecast (Kp 5)!
You might see the Southern Lights from your location. 
Best viewing: 10 PM-2 AM, look south. Get away from town lights.
Nearest dark sky spot: 15 min drive to [location] →
```

### 7. Pre-Trip Reminder
**Priority:** Normal
**Timing:** 3 days, 1 day before trip start
**Frequency:** 2 notifications total
**Content:** Trip preparation checklist

```
Journey Buddi — 3 Days to Go! 🎉
Your New Zealand adventure starts Thursday! 
Here's your pre-departure checklist →
```

## Notification Strategy

### Frequency Caps

| Time Period | Max Notifications | Exception |
|------------|-------------------|-----------|
| Per hour | 1 | Safety alerts bypass |
| Per day | 4 | Safety alerts bypass |
| Per trip | ~3 notifications/day average | Varies by trip intensity |

### Quiet Hours

Default: 9:00 PM — 6:30 AM local time
User configurable
Only safety alerts bypass quiet hours

### Notification Grouping

When multiple pieces of information are available at the same time, bundle them into a single notification rather than sending separate ones:

```
Instead of 3 separate notifications:
❌ "Weather update for tomorrow"
❌ "Pack list for tomorrow"  
❌ "Departure time suggestion"

Send 1 bundled notification:
✅ "Tomorrow's briefing is ready — weather, packing, and timing inside →"
```

### Smart Delivery Timing

- Don't send notifications while the user is likely driving (check if in transit between locations based on itinerary timing)
- Prefer notification delivery during meal times or downtime between activities
- If the user hasn't opened the app in 24+ hours during an active trip, send a gentle check-in

### User Preferences

Users can configure:
- Morning briefing time
- Evening preview time
- Notification categories (enable/disable each type)
- Quiet hours
- Alert sensitivity (all vs. important only vs. critical only)
- Sound/vibration preferences

## Push Notification Implementation

### Web (PWA)
- Web Push API via service worker
- Request notification permission during onboarding
- Fall back to in-app notifications if push denied

### Mobile (Future)
- Native push notifications via APNs (iOS) and FCM (Android)
- Rich notifications with images (condition icons, map thumbnails)
- Action buttons in notifications ("Accept swap", "View briefing")

## Notification Copy Guidelines

### Tone
- Warm, personal, like a text from a friend
- First person: "I noticed..." "I'd suggest..."
- Brief — the notification is a teaser, details are in-app
- Use emoji sparingly but naturally (weather icons, activity icons)

### Length
- Title: 5-8 words
- Body: 2-3 short lines maximum
- Always end with a call to action ("Tap to see..." or "→")

### Personalization
- Use the user's trip context: "Your whale watching tomorrow" not "Whale watching"
- Reference the specific location: "in Kaikoura" not "at your next destination"
- Time-aware: "This morning" not "Today AM"

## Anti-Patterns

### Never Do This
- Send notifications about conditions 5+ days away (too uncertain)
- Nag about the same swap suggestion after user declined
- Send purely promotional or engagement-bait notifications
- Use alarmist language for non-safety conditions ("ALERT: clouds expected!")
- Interrupt with low-value information during activity hours
- Send a notification that has no actionable content
- Stack multiple notifications in rapid succession

### Always Do This
- Lead with the most important information
- Give the user enough context to decide if they need to open the app
- Respect the user's notification preferences absolutely
- Include a clear next action
- Be honest about uncertainty in forecasts
