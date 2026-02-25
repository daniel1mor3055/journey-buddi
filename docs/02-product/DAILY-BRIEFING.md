# Daily Briefing — Detailed Specification

## Overview

The daily briefing is the single most important touchpoint between Buddi and the traveler during the trip. Every morning, the traveler receives a comprehensive, actionable summary of their day — conditions, timing, packing, tips, and any suggested changes. It's designed to take 2-3 minutes to read and leave the traveler feeling prepared and confident.

## Briefing Structure

### 1. Day Header

```
Good morning! ☀️ Day 7 of your New Zealand adventure

📍 You're in: Kaikoura
🌡️ Today: 18°C, partly cloudy, light winds from the south
🌅 Sunrise: 6:12 AM | 🌇 Sunset: 8:47 PM
```

### 1.5. Day Condition Banner

A prominent visual banner at the top of every day (visible in both the daily briefing AND the itinerary dashboard) that indicates overall plan quality for the day:

```
┌─────────────────────────────────────────────────┐
│  🟢 GREAT CONDITIONS     Today's plan: 92/100   │
│  All activities looking excellent                │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  🟠 MIXED CONDITIONS     Today's plan: 54/100   │
│  Morning hike OK, but afternoon kayak may suffer │
│  from wind. Tap for alternatives.                │
│  [🔄 See Alternative Plan]                       │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  🔴 POOR CONDITIONS      Today's plan: 28/100   │
│  Heavy rain and wind expected all day.           │
│  This isn't the right day for outdoor activities.│
│  [🔄 Shuffle My Plan]  [💡 Indoor Alternatives] │
└─────────────────────────────────────────────────┘
```

**Banner Rules:**
- Score is a weighted combination of all activity condition scores for the day
- When score is 🟠 or below, a "See Alternative Plan" button appears
- When score is 🔴, a "Shuffle My Plan" button triggers the adaptation engine to present a multi-day shuffle
- The banner also appears on each day card in the itinerary dashboard (compact version — just the emoji and score)

**Forecast Confidence Indicator:**
- For days more than 3 days out, append a confidence note:
  - "Forecast confidence: High ✓" (1-3 days)
  - "Forecast may change — I'll update as we get closer" (4-5 days)
  - "Too early for reliable forecast — conditions could shift significantly" (6+ days)

### 2. Overall Day Assessment

A single sentence that tells the traveler whether today is a "go" day:

```
🟢 "Great day ahead! Conditions are perfect for both your planned activities."

🟡 "Good day overall — whale watching conditions are solid. Afternoon 
    clouds might roll in but won't affect your plans."

🟠 "Mixed conditions today. Your morning hike will be fine but I'd suggest 
    rethinking the afternoon — see my recommendation below."

🔴 "Tough weather day. I have a suggested swap that would save your 
    Tongariro crossing for better conditions — details below."
```

### 3. Activity Breakdown

For each planned activity, a detailed card:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐋 WHALE WATCHING — Kaikoura
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏰ Suggested departure: 8:30 AM (tour at 9:15 AM)
📍 Location: Whale Watch Kaikoura, Whaleway Station Road
🕐 Duration: ~3 hours (including boat time)

Conditions: 🟢 EXCELLENT
  🌊 Sea state: Calm (wave height 0.5m)
  💨 Wind: 12 km/h south — very comfortable on the water
  🌤️ Cloud: Partly cloudy — great visibility for spotting
  
🎒 Pack for this activity:
  • Warm layer (it's cooler on the water even on warm days)
  • Sunscreen + sunglasses (reflection off water)
  • Motion sickness tablets if you're prone (take 30 min before)
  • Camera with zoom lens if you have one
  • Light rain jacket (just in case — spray from the boat)
  
💡 Pro tips:
  • Sit on the LEFT side of the boat heading out — better whale views
  • Sperm whales surface roughly every 45-60 minutes for about 10 min
  • Listen for the crew's instructions on which direction to look
  • The Kaikoura canyon is only 1km offshore — that's why the whales 
    are so close here. Deep water = giant squid = sperm whales
  • If you're lucky, you might see dolphins bow-riding the boat on 
    the way back
    
📝 Good to know:
  • Check in 15 minutes before departure
  • Full refund if no whales spotted (rare — 95% sighting rate)
  • Bathroom on board but it's basic — go before boarding
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4. Timing Overview

A visual timeline of the day:

```
📋 YOUR DAY

  7:00 AM   Wake up, breakfast
  8:30 AM   Depart for Whale Watch
  9:15 AM   🐋 Whale watching tour (3h)
  12:30 PM  Lunch in Kaikoura (try Nin's Bin for crayfish!)
  2:00 PM   🦭 Ohau Point seal colony (30 min, roadside stop)
  2:45 PM   🚶 Kaikoura Peninsula Walkway (2h, coastal walk)
  5:00 PM   Free time / explore town
  7:00 PM   Dinner
  8:00 PM   📍 Tomorrow's preview notification
```

### 4.5. Day Tightness Check

```
📊 DAY SCHEDULE CHECK

  Total activity time: 5.5 hours
  Transport time: 1 hour
  Meals & breaks: 2.5 hours
  Buffer: 1 hour
  ─────────────
  Total: 10 hours | Fill: 67%
  
  🟡 Comfortable — good balance of activity and rest
```

When the day is overpacked (🔴 > 85% fill):
```
📊 DAY SCHEDULE CHECK

  ⚠️ This day is packed tight — 92% fill
  
  If anything runs late or you want spontaneous stops,
  you'll feel rushed. Consider:
  [Remove an activity]  [Move something to tomorrow]
```

### 5. Packing Summary

Consolidated packing list for the entire day (deduplicated from all activities):

```
🎒 TODAY'S PACK LIST
  ✅ Warm layer / fleece
  ✅ Light rain jacket
  ✅ Sunscreen + sunglasses + hat
  ✅ Comfortable walking shoes (Peninsula Walkway is 2h on mixed terrain)
  ✅ Camera with zoom lens
  ✅ Water bottle
  ✅ Motion sickness tablets
  ✅ Cash/card for Nin's Bin (cash recommended, small operation)
```

### 5.5. Accommodation for Tonight

```
🏨 TONIGHT'S STAY

  Type: Holiday Park
  Name: Kaikoura Top 10 Holiday Park
  📍 34 Beach Road, Kaikoura
  📞 +64 3-319 5362
  🗺️ [Open in Google Maps]
  
  Check-in: From 2:00 PM
  Status: ✅ Booked (Ref: KTP-2847)
  
  💡 They have hot tubs with mountain views — 
     perfect after today's activities!
```

When accommodation is NOT booked:
```
🏨 TONIGHT'S STAY

  Zone: Kaikoura area
  Recommended type: Holiday park or motel
  Status: ⚠️ Not yet booked
  
  Buddi's picks:
  1. Kaikoura Top 10 ($55/night, great facilities) [Book]
  2. Alpine-Pacific Motel ($120/night, mountain views) [Book]
  3. Freedom camp at South Bay ($0, basic, oceanfront) [Navigate]
```

### 6. Swap Suggestion (if applicable)

Only included when conditions warrant a change. See [ITINERARY-ADAPTATION.md](./ITINERARY-ADAPTATION.md) for the full swap logic.

When a swap is suggested, the briefing includes not just the rationale but a COMPLETE action plan:

```
🔄 SUGGESTED PLAN CHANGE

  📅 I recommend shuffling your next 3 days:
  
  CURRENT PLAN:              SUGGESTED PLAN:
  Day 7: Kayaking    🔴  →  Day 7: Museum + walk    🟡
  Day 8: Museum      🟡  →  Day 8: Hike             🟢
  Day 9: Hike        🟢  →  Day 9: Kayaking          🟢
  
  WHY: Monday's 35km/h wind makes kayaking unsafe.
  Wednesday has calm 8km/h winds — perfect conditions.
  
  📋 WHAT YOU NEED TO DO:
  ☐ Call Abel Tasman Kayaks to reschedule: 
    📞 +64 3-527 8022 | Ref: ATK-4521
    Move from Mon AM to Wed AM (they have 8:30 AM slots)
  ☐ No hut/hotel changes needed — same area all 3 days
  ☐ Everything else stays the same
  
  ⏰ Time-sensitive: Call today (they fill up for Wednesday)
  
  [✅ Accept & Update]  [❌ Keep Original]  [💬 More Info]
```

### 7. Hidden Gem of the Day

A bonus recommendation that isn't in the itinerary but adds magic:

```
✨ HIDDEN GEM

If you're on the Peninsula Walkway around 5 PM, detour to the 
Point Kean viewing platform. The fur seals are most active at 
dusk and you'll often see pups playing in the rock pools. It's 
only 100m off the main trail and most tourists miss it.
```

### 8. Look-Ahead Preview

A brief preview of the next 3-5 days with condition forecasts:

```
📅 COMING UP

  Tomorrow (Day 8): 🟢 Great — calm morning, perfect for coastal walk
  Day 9: 🟡 Good — light cloud, fine for glacier visit  
  Day 10: 🟠 Watch — rain system approaching, monitoring closely
  Day 11: ⏳ Too early for reliable forecast
  
  💡 If Day 10 rain holds, I have a shuffle plan ready that 
     moves your outdoor hike to Day 12 (looking clear). 
     I'll confirm tomorrow evening.
```

**Accuracy Disclaimer:**
For days beyond the reliable forecast window, include a note that data may change. Different conditions have different accuracy horizons — aurora predictions are only reliable 1-2 days out, while temperature trends are reliable 5-7 days out. The briefing should reflect this nuance rather than treating all forecasts equally.

## Briefing Generation

### Data Sources Required

For each day's briefing, Buddi needs:

1. **Itinerary data**: Today's planned activities, timing, locations
2. **Weather forecast**: Hourly forecast for the activity locations (temperature, precipitation, wind, cloud cover)
3. **Tide data**: If any activities are tide-dependent
4. **Solar data**: Sunrise, sunset, golden hour, UV index
5. **Activity knowledge base**: Pro tips, packing needs, hidden gems for each activity
6. **Historical patterns**: What conditions have been like this week (for trend context)
7. **Lookahead forecast**: Next 3-5 days for swap consideration

### AI Generation Process

1. **Fetch all condition data** for today's locations and activities
2. **Evaluate each activity** against its condition requirements
3. **Generate condition assessment** (green/yellow/orange/red)
4. **Check swap opportunities** if any activity scores orange or red
5. **Compile packing list** from activity requirements + actual conditions
6. **Generate pro tips** contextualized to today's conditions
7. **Assemble briefing** in the structured format
8. **Add hidden gem** relevant to today's area

### Personalization

The briefing adapts to the user's profile:

- **Pace = relaxed**: More emphasis on "take your time" and optional rest periods
- **Photography interest**: Include golden hour times, best angles, lighting conditions
- **High fitness**: Include optional trail extensions or harder variants
- **Budget-conscious**: Highlight free alternatives and cost-saving tips
- **Wildlife interest**: Include wildlife activity patterns specific to today's conditions

## Briefing Delivery

### Primary: Push Notification

```
Journey Buddi — Day 7 ☀️
🟢 Great day ahead! Your whale watching and coastal walk are both 
looking perfect. Tap to see your full briefing.
```

### Secondary: In-App

Full briefing available in the app at any time, with ability to scroll through past days' briefings.

### Timing Configuration

Users can configure:
- Morning briefing time (default: 7:00 AM local)
- Evening preview time (default: 8:00 PM local)
- Do not disturb hours
- Notification preferences (all, important only, none)

## Edge Cases

### Multi-Location Day
When the user travels between areas during the day:
- Show conditions for each location at the relevant time
- Include driving time and conditions between locations
- Note if weather differs significantly between locations

### Rest Day
If it's a designated flex/rest day:
- Light briefing with weather overview
- Suggest optional activities in the area
- "Today's your flex day! Here are some ideas if you feel like exploring, or just enjoy the area at your own pace."

### Weather Washout
If conditions are poor for everything:
- Don't force outdoor alternatives
- Suggest indoor activities, cultural sites, food experiences
- Frame it positively: "Even adventurers need a cozy day. Here's how to make the most of it."
- Update the lookahead for when to reschedule rained-out activities
