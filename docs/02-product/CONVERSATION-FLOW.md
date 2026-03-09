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
Buddi: "To help me pace our days perfectly, let's talk about your energy levels.
        What does a comfortable day of exploring look like for you?"
       [🛋️ Keep it relaxed — scenic drives, flat strolls, frequent stops. Up to an hour of walking a day.]
       [🥾 Active explorer — on my feet for a few hours, towns/beaches/undulating paths, but I need time to recharge.]
       [🔥 Endless energy — highly physical days, steep climbs, full-day excursions, no problem.]
       [🎲 A mix of everything — push myself occasionally, balanced with easy recovery days.]
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

### Round 2: Interest Categories (Multi-Select)

> **3-Level Activity Design**: The conversation only collects *categories* (Level 1).
> Specific activities (Level 2) and providers (Level 3) are chosen post-chat.

```
Buddi: "Now the fun part! What types of experiences get you excited?
       Pick everything that interests you."

       [🏛️ Attractions — Must-see landmarks, nature spots, parks, museums]
       [🗺️ Tours — Guided experiences, cruises, sightseeing, wildlife tours]
       [🚐 Day Trips — Full-day excursions from a base city]
       [🥾 Outdoor Activities — Hiking, water sports, adrenaline, wildlife]
       [🎭 Concerts & Shows — Live entertainment, cultural performances]
       [🎪 Events — Festivals, markets, exhibitions, sporting events]
       [🎨 Classes & Workshops — Hands-on learning, lessons, creative workshops]
       [🚂 Transportation — Scenic railways, ferries, cable cars]
       [ℹ️ Traveler Resources — Visitor centres, information hubs]
```

These are the 9 strict TripAdvisor-aligned categories. No additions allowed.

### Round 3: Island Preference

```
Buddi: "Which parts of New Zealand?"
       [🏔️ South Island — mountains, glaciers, fjords — the adventure hub]
       [🌋 North Island — volcanoes, geothermal, Māori culture, beaches]
       [🗺️ Both islands — the full NZ experience]
```

Buddi uses the user's chosen categories to provide an informed recommendation
about which island best matches their interests.

### Round 4: Transport & Route

```
Buddi: "Let's talk about getting around!"
       [🚐 Campervan — freedom camping, wake up to views]
       [🚗 Rental car — nimble, book accommodation]
       [🔀 Mix of both — best of both worlds]
       [🚌 Public transport — buses, trains, ferries]
```

```
Buddi: "Which direction do you want to loop around?"
       [🔄 Clockwise]
       [🔃 Counter-clockwise]
       [🗺️ Custom — let Buddi optimise the route]
```

### Conversation Complete

After transport & route, the planning conversation ends. Buddi generates a
skeleton itinerary and the user moves to the dashboard.

### Post-Conversation Experience

#### Level 2 — Activity Selection (Dashboard)

After the conversation, users browse and select specific activities within
their chosen categories. This happens in a proper UI, not in chat.

Example: User chose "Outdoor Activities" → they now see options like
bungy jumping, whale watching, glacier hiking, kayaking, etc.

#### Level 3 — Provider Selection (Progressive Itinerary)

Buddi generates a skeleton itinerary (route with locations and days).
Then, location by location:

1. The system shows which desired activities can be done at the current location
2. The user selects which activities they want to do there
3. For each selected activity, provider options are shown
4. The user picks providers and the itinerary "fills up"
5. Move to the next location, repeat

This spreads activities geographically instead of clustering everything
in one area.

#### Activity Wishlist / Tracker

A clear, always-visible tracker showing:
- All activities the user wants to accomplish (from Level 2)
- Which ones have been placed in the itinerary
- Which ones are still remaining / unassigned

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

The conversation collects a focused set of preferences (PlanningContext):

```
PlanningContext {
  current_agent: string           // Current pipeline step
  completed_agents: string[]      // Steps completed so far
  group_type: string              // Solo, couple, family, friends
  group_details: object           // Count, ages
  accessibility_needs: object     // Accessibility requirements
  fitness_profile: object         // Fitness level and capabilities
  budget: object                  // Budget preference
  destination: string             // "New Zealand"
  travel_dates: object            // Season / date range
  trip_duration: object           // Duration in days
  max_driving_hours: number       // Preferred max per day
  interest_categories: string[]   // Selected TripAdvisor categories (Level 1)
  island_preference: object       // North, South, or both
  transport_plan: object          // Transport mode
  route_direction: string         // Clockwise, counter-clockwise, custom
}
```

This state persists across sessions. After the conversation completes,
additional state is built during post-chat activity selection (Level 2)
and progressive itinerary building (Level 3).

## Tone & Language

- Enthusiastic but not cheesy
- Specific and knowledgeable, never vague
- Uses "I'd recommend" and "I suggest" — has opinions
- Acknowledges trade-offs honestly ("this adds 2 hours of driving but it's worth it")
- Celebrates good choices ("Oh you're going to love this one!")
- Never condescending — respects the user's intelligence
- Concise — doesn't over-explain unless asked
