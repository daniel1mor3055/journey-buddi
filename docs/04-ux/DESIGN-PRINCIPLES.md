# Design Principles

## The Five Principles

These principles guide every design decision in Journey Buddi. When facing a trade-off, refer to these in priority order.

---

### 1. Useful Over Beautiful

Beauty matters — a well-designed app builds trust and delight. But utility comes first. A gorgeous screen that doesn't help the traveler make a decision or take action is a failure. A plain screen that tells you exactly what to pack and when to leave is a success.

**In practice:**
- Every pixel on screen should either inform, guide, or delight (in that priority order)
- If an element is only decorative, question whether it's pulling its weight
- Data visualization (conditions, timeline, map) should be clear before it's pretty
- When in doubt, optimize for speed of comprehension

**Examples:**
- ✅ Condition badge with emoji + text: "🟢 Excellent" — instantly scannable
- ❌ Beautiful animated weather widget that takes 3 seconds to parse

---

### 2. Calm Over Urgent

Travelers on vacation are trying to relax. Our app should never add stress. Notifications should feel like helpful nudges from a friend, not alarm bells from a monitoring system.

**In practice:**
- Use calm, confident language — not urgent imperatives
- Reserve red/warning colors for genuine safety concerns
- Notifications are informational first, actionable second
- Quiet hours are sacred — never interrupt sleep for non-safety alerts
- When suggesting changes, frame as opportunities, not problems

**Examples:**
- ✅ "Tomorrow's looking a bit wet. I have a great alternative if you're interested."
- ❌ "⚠️ ALERT: Weather conditions deteriorating! Action required!"

---

### 3. Specific Over Generic

The #1 complaint about travel advice is vagueness. "Dress in layers" tells you nothing. Journey Buddi's value is in specificity — and the design must support that.

**In practice:**
- Show actual temperatures, not just "cold" or "warm"
- Show actual times ("arrive by 7:30 AM") not just "arrive early"
- Show actual items to pack, not categories ("thermal base layer" not "warm clothes")
- Show actual distances and drive times, not "nearby"
- Condition data should be precise and attributable

**Examples:**
- ✅ "18°C dropping to 4°C at summit. Wind chill: -1°C. Pack: thermal base layer, fleece, windproof shell, gloves, beanie."
- ❌ "It might be cold at higher elevations. Dress warmly and bring rain gear just in case."

---

### 4. Conversation Over Configuration

When the user needs to make a choice or provide input, the default should be a conversation with Buddi, not a settings page or a form. Forms are for machines. Conversations are for humans.

**In practice:**
- Preference gathering happens through chat with Buddi, not profile forms
- Itinerary changes are discussed with Buddi, not managed through drag-and-drop alone
- The settings screen is minimal — most configuration happens through chat
- "Just ask Buddi" should be the answer to most "how do I...?" questions

**Examples:**
- ✅ User says "I want to add a wine day" → Buddi finds the best spot in the itinerary
- ❌ User opens "Add Activity" modal → selects category → selects region → picks from list

---

### 5. Trust Through Transparency

The AI makes complex decisions (itinerary structure, swap suggestions, condition assessments). Users must trust these decisions. Trust comes from transparency — showing the reasoning, acknowledging uncertainty, and being honest about limitations.

**In practice:**
- Every recommendation includes "why" — even if brief
- Condition scores show what factors contributed (wind, rain, cloud, etc.)
- Forecast-based decisions acknowledge uncertainty ("if the forecast holds")
- When Buddi doesn't know something, it says so
- Users can always see the underlying data if they want to

**Examples:**
- ✅ "I'd suggest Fox Glacier over Franz Josef — less crowded, better valley walk, and Lake Matheson is right there for sunrise reflections."
- ❌ "Recommended: Fox Glacier" (no reasoning)

---

## Design Decision Framework

When making a design decision, ask these questions in order:

1. **Is it useful?** Does this help the traveler plan better, experience more, or adapt to conditions?
2. **Is it calm?** Does this add stress or reduce it?
3. **Is it specific?** Does this give actionable, precise information?
4. **Is it conversational?** Could this be handled by Buddi instead of a form/menu?
5. **Is it transparent?** Does the user understand why this is being shown/suggested?

If you can answer "yes" to all five, the design is on track.

## Anti-Patterns to Avoid

### The Dashboard Trap
Don't create a dashboard with 15 widgets showing data nobody asked for. The daily briefing IS the dashboard, and it's curated by Buddi.

### The Notification Firehose
Don't notify for every data point change. Only notify when there's a human-meaningful change that warrants attention.

### The Feature Graveyard
Don't add features "because other travel apps have them." Every feature must serve the core mission: help travelers experience their trip at its best.

### The Form Fortress
Don't build complex multi-step forms for things that can be handled conversationally. The planning flow should feel like a chat, not a government application.

### The Data Dump
Don't show raw weather data in a table. Synthesize it into a human-readable assessment with context ("18°C is comfortable for hiking, but the summit will feel like -1°C with wind chill — bring warm layers").
