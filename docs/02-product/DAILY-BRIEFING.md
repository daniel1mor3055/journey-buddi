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

### 6. Swap Suggestion (if applicable)

Only included when conditions warrant a change. See [ITINERARY-ADAPTATION.md](./ITINERARY-ADAPTATION.md) for the full swap logic.

### 7. Hidden Gem of the Day

A bonus recommendation that isn't in the itinerary but adds magic:

```
✨ HIDDEN GEM

If you're on the Peninsula Walkway around 5 PM, detour to the 
Point Kean viewing platform. The fur seals are most active at 
dusk and you'll often see pups playing in the rock pools. It's 
only 100m off the main trail and most tourists miss it.
```

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
