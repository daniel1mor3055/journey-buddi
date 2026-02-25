# AI Conversation Flow — Planning Phase

## Design Philosophy

Journey Buddi's planning conversation is designed around three unbreakable principles:

1. **Never ask open-ended questions.** Always present concrete, curated options. The user selects; they don't generate. This reduces cognitive load and ensures Buddi can work with structured input.

2. **Be opinionated but flexible.** Buddi should have a recommendation for everything. "I'd suggest X because Y" — not "what would you prefer?" But the user can always override.

3. **Progressive disclosure.** Don't front-load all decisions. Start broad, narrow gradually. Each step builds on previous answers.

## Conversation Structure

### Opening

```
Buddi: "Hey! I'm Buddi, your travel companion. I'm going to help you 
       build an incredible trip — one that adapts to real conditions so 
       you experience everything at its best.
       
       Let's start with a few quick questions about how you like to travel. 
       This helps me tailor everything to you."
```

### Round 1: Travel DNA (5 quick-choice questions)

Each question is a visual card with 3-4 options. User taps one.

```
Buddi: "When you travel, you're more like..."
       [🌿 The Scenic Explorer — beautiful views, easy pace, soaking it in]
       [🥾 The Active Adventurer — hikes, kayaks, gets out there]
       [🧗 The Thrill Seeker — extreme sports, challenging treks, pushing limits]
```

```
Buddi: "On a typical travel day, you'd prefer..."
       [☕ 1-2 activities, plenty of café time and wandering]
       [⚖️ 2-3 activities with some breathing room]
       [🔥 Dawn to dusk — squeeze every minute]
```

```
Buddi: "Physically, you're comfortable with..."
       [🚶 Easy walks and drives — nothing too strenuous]
       [🥾 Moderate hikes up to 4-5 hours]
       [⛰️ Full-day strenuous hikes, I'm fit]
```

```
Buddi: "For paid activities and experiences, you're thinking..."
       [💚 Mostly free/budget — nature doesn't cost money!]
       [💛 Happy to pay for standout experiences]
       [💎 I want the best, cost isn't the main factor]
```

```
Buddi: "Who's coming along?"
       [🧑 Just me — solo adventure]
       [💑 With my partner]
       [👨‍👩‍👧‍👦 Family with kids]
       [👯 Group of friends]
```

### Round 2: Interests (Multi-Select)

```
Buddi: "Now the fun part! What gets you excited? Pick everything 
       that interests you — I'll find the best options."
       
       [🐬 Wildlife & Marine Life]
       [🏔️ Mountains & Glaciers]  
       [🏖️ Beaches & Coast]
       [🌊 Lakes & Rivers]
       [🌲 Forests & Rainforest]
       [🌋 Volcanoes & Geothermal]
       [⭐ Stargazing & Dark Skies]
       [📸 Photography & Scenery]
       [🚣 Water Sports]
       [🥾 Hiking & Trekking]
       [🏛️ Culture & History]
       [🍷 Food & Wine]
       [🪂 Unique Thrills (bungy, skydive)]
```

### Round 3: Destination & Dates

```
Buddi: "Where are you heading?"
       [🇳🇿 New Zealand]  ← Initially the only option, more added over time
```

```
Buddi: "When are you going?"
       [Calendar picker for start date]
       [End date OR "Flexible — help me decide"]
```

```
Buddi: "Which parts of New Zealand?"
       [🏔️ South Island only — rugged, dramatic, nature-focused]
       [🌿 North Island only — volcanoes, culture, geothermal]
       [🗺️ Both islands — the full experience]
```

```
Buddi: "Where do you fly in and out?"
       [Auckland]  [Christchurch]  [Queenstown]  [Wellington]
       [Different arrival and departure cities]
```

```
Buddi: "How do you feel about driving?"
       [🚗 Keep it short — 1-2 hours max per day]
       [🛣️ 3-4 hours is fine — road trips are part of the fun]
       [🏎️ 5+ hours is OK if it means seeing more]
```

```
Buddi: "Do you have your flights booked? If so, share the details 
       and I'll build Day 1 and your final day around your arrival 
       and departure times."
       [✈️ Yes — let me enter my flight details]
       [📅 Not yet — I'll add them later]
       [🤷 Help me figure out the best flights]
```

### Round 4: Priority Locations

```
Buddi: "Before we dive into specific activities — are there any places 
       or experiences that are absolutely non-negotiable for you?"
       
       [🗺️ Yes — I have some must-dos]
       [🙅 Yes — there are things I want to avoid]
       [🤙 No strong feelings — surprise me, Buddi!]
```

If user has must-dos:

```
Buddi: "Tell me your must-dos! You can type them or pick from these 
       popular ones for New Zealand:"
       
       [🏔️ Milford Sound]  [🌋 Tongariro Crossing]  [⭐ Hobbiton]
       [🦘 Kiwi spotting]  [🧊 Glacier hike]  [🪂 Queenstown bungy]
       [Type your own...]
       
       "These are locked in — I'll build everything around them."
```

### Round 5: Deep Dive — Interest-Specific Options

For each selected interest, Buddi presents destination-specific experiences. This is the longest part of the conversation but the most engaging because the user is seeing concrete, exciting possibilities. When showing specific options, Buddi shows providers across ALL of NZ, not just one location.

**Conversation branching example:**

User selected: Wildlife & Marine Life, Mountains & Glaciers, Hiking & Trekking

```
Buddi: "Let's talk wildlife first! New Zealand is incredible for this. 
       Here's what's possible on the South Island:"
       
       🐬 Swim with dusky dolphins — Kaikoura (95% encounter rate!)
       🐋 Whale watching — Kaikoura (sperm whales year-round)
       🐧 Yellow-eyed penguin colony — Dunedin (rare species!)
       🐧 Blue penguin parade — Oamaru (evening viewing)
       🦭 Fur seal colony — Kaikoura coast (free, roadside!)
       🌌 Glowworm caves — Te Anau (underground boat ride)
       🐦 Albatross colony — Dunedin (only mainland colony in the world)
       
       "Which of these would make your trip? Select all that interest you."
```

After selection:

```
Buddi: "Great choices! A couple of notes:
       
       🐬 Dolphins and 🐋 whales are both in Kaikoura, so we'll plan 
       those together — probably 2 days in the area.
       
       🐧 Both penguin options are on the east coast between Christchurch 
       and Dunedin. The yellow-eyed penguins in Dunedin are rarer and 
       more special — I'd recommend those. But Oamaru's blue penguins are 
       fun too if we pass through. Want both or just one?
       
       🌌 Te Anau glowworms fit perfectly as an evening activity before 
       or after Milford Sound. I'll slot that in."
```

**Provider diversification example — when the user selects an activity type, Buddi shows the best providers across NZ:**

```
Buddi: "Let's find the perfect bungy experience! Here are the best 
       options across New Zealand:
       
       🏆 AJ Hackett Kawarau Bridge — Queenstown
       The ORIGINAL bungy site. 43m over the turquoise Kawarau River.
       ⭐ 4.8 (2,340 reviews) • $205 NZD
       What's special: Historic site, scenic setting, great photos included
       
       🏔️ AJ Hackett Nevis — Queenstown  
       NZ's HIGHEST bungy at 134m. Suspended over a dramatic canyon.
       ⭐ 4.9 (1,890 reviews) • $275 NZD
       What's special: Extreme height, cable car ride to the platform
       
       🌊 Taupō Bungy — Taupō (North Island)
       47m over the stunning Waikato River with cliff-face backdrop.
       ⭐ 4.7 (1,120 reviews) • $189 NZD
       What's special: Beautiful river setting, less crowded than QT
       
       🌲 AJ Hackett Auckland Bridge — Auckland
       40m off the Auckland Harbour Bridge with city views.
       ⭐ 4.5 (980 reviews) • $165 NZD
       What's special: Urban setting, combine with bridge walk
       
       💡 My recommendation: If you're doing bungy once, the Nevis is 
       unmatched — but if you're also skydiving in Queenstown, consider 
       spreading the thrills and doing Taupō Bungy on Day 4 instead.
       
       Which speaks to you? Or should I pick the best fit for your route?"
```

### Round 6: Route Negotiation

```
Buddi: "Here's what I'm thinking for your route. With everything you've 
       selected, a clockwise loop works best:
       
       Christchurch → Kaikoura → Blenheim → Abel Tasman → West Coast 
       → Glaciers → Wanaka → Queenstown → Te Anau/Milford → Dunedin 
       → Oamaru → Christchurch
       
       This minimizes backtracking and groups nearby attractions.
       
       [View on map]
       
       Does this flow feel right, or would you like to adjust the direction?"
```

### Round 7: Pace & Duration

```
Buddi: "Based on your 'balanced' pace preference and everything you've 
       selected, I'd recommend 16-18 days:
       
       • 12 activity days
       • 3 travel/transition days  
       • 2-3 flex days (buffer for weather swaps + spontaneous discovery)
       
       You mentioned your trip is Dec 5-23 — that gives us 18 days, 
       which is perfect!
       
       If you want to trim it to 14 days, I'd suggest dropping [X, Y] 
       or combining [A with B].
       
       [Keep 18 days — let's build it!]
       [I need to trim — show me options]"
```

### Round 8: Transport Discussion

```
Buddi: "Let's talk about getting around. For the South Island, I have 
       a strong recommendation:
       
       🚐 Days 1-12 (Christchurch → West Coast → Queenstown): 
       CAMPERVAN/MOTORHOME
       Why: The South Island's west coast and rural areas have limited 
       accommodation. A campervan gives you freedom to stop anywhere, 
       and many of NZ's best spots have amazing freedom camping sites 
       right on the coast or lakefront. You'll wake up to views that 
       hotel guests pay $500/night for.
       
       🚗 Days 13-18 (Queenstown → Dunedin → Christchurch): 
       RENTAL CAR
       Why: The east coast has more towns and accommodation. You'll want 
       a lighter, more nimble vehicle for the Dunedin hill streets and 
       shorter distances between stops.
       
       [Sounds great — go with that!]
       [I'd prefer car the whole way]
       [I'd prefer campervan the whole way]
       [Tell me more about the trade-offs]"
```

### Round 9: Itinerary Presentation

```
Buddi: "Your trip is ready! Here's your 18-day South Island adventure:
       
       📅 Day 1 (Dec 5): Arrive Christchurch, pick up campervan, 
          explore city gardens, settle in
       📅 Day 2 (Dec 6): Drive to Kaikoura (2.5h), afternoon seal 
          colony walk, evening seafood on the pier
       📅 Day 3 (Dec 7): Morning dolphin swim, afternoon whale watching
       📅 Day 4 (Dec 8): Kaikoura Peninsula walk, drive to Blenheim (2h)
       ...
       
       [View full itinerary]
       [View on map]
       [This looks amazing!]
       [I want to make changes]"
```

## The Autonomous Fallback

Not every question needs a manual answer. For complex decisions where the user would struggle to express preferences, Buddi offers to decide:

**Questions that commonly use the fallback:**
- Optimal day structure and activity sequencing
- Which provider to choose when differences are marginal
- Rest day placement
- Route direction (clockwise vs counterclockwise)
- Activity timing within a day

**How it works:**

```
Buddi: "I can optimize the day-by-day ordering based on geography 
       and conditions, or would you like to arrange the sequence yourself?"
       [🤖 You decide — I trust you, Buddi!]
       [✋ Let me see the options first]
```

When the user chooses "you decide," Buddi makes the call AND explains its reasoning briefly: "I put Milford Sound on Day 12 because that's when the forecast looks clearest — and it follows naturally from Te Anau."

**Principle:** The agent should always be ready to take full ownership of a decision. The user should never feel forced to answer a question they don't have a strong opinion on.

## Conversation Recovery

### What if the user goes off-script?

Buddi should handle natural language gracefully:

- **"I've already been to Kaikoura"** → Buddi removes Kaikoura options and re-suggests
- **"My friend recommended Hobbiton"** → Buddi notes it, checks if it fits the route, suggests placement
- **"This is too many days"** → Buddi enters trimming mode with specific cut suggestions
- **"What about the North Island too?"** → Buddi expands scope, presents North Island options
- **"I'm actually more interested in food and wine"** → Buddi pivots, highlights Marlborough, Central Otago, adds culinary experiences

### What if the user wants to skip ahead?

- "Just build me a trip, I trust you" → Buddi generates a balanced itinerary using profile defaults and presents it for review
- "I already know what I want to do, here's my list" → Buddi takes the list and optimizes route/timing/logistics
- "Build it your way, Buddi, and I'll tweak it" → Buddi generates a complete itinerary using profile + smart defaults, presents it as an interactive dashboard, and the user edits whatever they want. This is the most common flow for users who trust the AI — Buddi can generate 80-100% of the itinerary autonomously, and the user's job is to review, customize, and get excited.

## Conversation State Management

The conversation maintains a growing state object:

```
ConversationState {
  step: string                    // Current step in the flow
  profile: UserProfile            // Accumulated preferences
  destination: Destination        // Selected destination
  dates: DateRange                // Trip dates
  travel_group: string            // Solo, couple, family, friends
  max_driving_hours: number       // Preferred max per day
  priority_locations: Location[]  // Must-visit places
  must_not_do: string[]           // Things to avoid
  flight_details: FlightInfo      // Arrival and departure flights
  selected_interests: string[]    // What excites the user
  selected_attractions: Attraction[]  // Specific things to do
  rejected_attractions: string[]  // Things the user passed on
  route: RouteNode[]              // Geographic sequence
  transport: TransportPlan        // How they're getting around
  pace: PaceConfig                // Activity density
  duration: number                // Total days
  locked_days: Day[]              // Days that can't change
  conversation_history: Message[] // Full chat history for context
}
```

This state persists across sessions — the user can close the app and return to continue planning.

## Tone & Language

- Enthusiastic but not cheesy
- Specific and knowledgeable, never vague
- Uses "I'd recommend" and "I suggest" — has opinions
- Acknowledges trade-offs honestly ("this adds 2 hours of driving but it's worth it")
- Celebrates good choices ("Oh you're going to love this one!")
- Never condescending — respects the user's intelligence
- Concise — doesn't over-explain unless asked
