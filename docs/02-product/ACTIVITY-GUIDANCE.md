# Activity Guidance System

## Overview

For every activity in the itinerary, Journey Buddi provides expert-level, condition-aware guidance. This isn't generic information from a guidebook — it's specific, timely, and personalized advice that adapts to today's actual conditions, the user's profile, and contextual factors.

The activity guidance system is what makes Buddi feel like a knowledgeable local friend rather than a search engine.

## Guidance Components

### 1. Condition-Specific Preparation

Not just "bring a jacket" but precisely what to bring and why, based on actual forecasted conditions for this specific activity on this specific day.

**Generic guidebook advice:**
> "Wear comfortable shoes and bring layers."

**Buddi's condition-specific guidance:**
> "Today at the Tongariro Crossing: temperature will be 12°C at the trailhead dropping to 4°C at the summit around 11 AM. Wind chill will make it feel like -1°C on the exposed Red Crater ridge. Pack: thermal base layer, fleece mid-layer, windproof/waterproof shell, warm gloves, beanie. Your normal hiking shoes are fine — the track is well-maintained but rocky above the tree line. The descent has loose scoria — trekking poles help if you have them."

### 2. Optimal Timing

When to arrive, when to start, and how to time the experience for the best outcome.

**Factors considered:**
- Crowd patterns (early morning beats the tour buses)
- Light conditions (sunrise/sunset, golden hour for photography)
- Tide timing (coastal activities)
- Wildlife activity windows (dawn/dusk for many species)
- Temperature progression (hiking in heat — start early)
- Activity-specific scheduling (boat tours, guided walks)

**Example:**
> "🐧 Yellow-eyed Penguin Colony — Dunedin"
> 
> "The penguins return from sea between 4:30-6:00 PM this time of year. Arrive at the hide by 4:00 PM to settle in before they start appearing. The best viewing is from the main hide — the one on the left as you enter. They come ashore in small groups, usually starting from the right side of the beach.
> 
> Sunset is at 8:47 PM, so you'll have good light through the whole viewing. The ultraviolet light is still strong at 4 PM — wear sunscreen even though it feels like evening."

### 3. Location-Specific Tips

Precise, local-knowledge-level guidance for the specific place.

**Categories of tips:**

**Best viewpoints:**
> "At Milford Sound, the most photographed spot is the main wharf looking toward Mitre Peak. But the better shot is from the kayak launch point 200m further south — it gives you foreground water reflections and avoids the tour boats."

**Hidden gems:**
> "Most people turn back at the main lookout at Pancake Rocks. If you continue 100m past the blowholes on the unmarked trail to the right, there's a secluded viewpoint where you can see the full rock stack formation. Best at high tide when the blowholes are most active — today that's at 2:15 PM."

**Practical logistics:**
> "Parking at Cathedral Cove fills up by 9 AM in summer. Park at the Hahei Beach car park ($10/day) and walk the additional 15 minutes. Or better yet — arrive at 7:30 AM for a nearly empty beach and morning light through the arch."

**Food & drink:**
> "After your glacier walk, stop at Matheson Café right by Lake Matheson. Their flat white is excellent and the view of Mt Cook and Mt Tasman reflected in the lake is best in the morning before wind picks up. Today the wind drops to 5 km/h between 8-10 AM — perfect for reflections."

### 4. Stories & Context

What makes this place special — history, geology, ecology, culture. Delivered naturally, like a guide who loves the subject.

**Example:**
> "📖 About Tongariro:"
> 
> "The Tongariro Alpine Crossing isn't just a hike — it's a walk through New Zealand's most active volcanic landscape. The three volcanoes here (Tongariro, Ngauruhoe, Ruapehu) are sacred to the Ngāti Tūwharetoa people and were gifted to the nation in 1887, making Tongariro New Zealand's first national park.
> 
> The emerald lakes you'll pass get their stunning color from dissolved minerals leached from the surrounding volcanic rock. The color intensity varies — on clear days like today, they'll look impossibly vivid.
> 
> Fun fact: Mt Ngauruhoe played Mt Doom in Lord of the Rings. You can see it throughout the crossing — it's the perfectly conical peak."

### 5. Safety Considerations

When relevant, clear safety information specific to today's conditions.

**Example:**
> "⚠️ Safety notes for today's crossing:"
> 
> "Wind gusts of 35 km/h are forecast at the summit between 11 AM and 1 PM. This is within safe limits but you'll feel it on the exposed Red Crater ridge. Take your time and keep your balance on the narrow sections. If gusts exceed 60 km/h (unlikely today), DOC may close the track — check the trailhead notice board.
> 
> There's no water source on the track — carry at least 2 liters per person. The sun is strong at altitude even on cool days — SPF50 minimum.
> 
> The track is well-marked but navigation above the tree line can be tricky in cloud. Today's forecast shows clear skies so this shouldn't be an issue."

### 6. Photography-Specific Guidance

For users who indicated photography as an interest:

> "📸 Photography tips:"
> 
> "Golden hour this evening: 7:45-8:20 PM"
> "Best angles: Southwest for Mitre Peak backlit by sunset"
> "Lens suggestion: Wide angle (16-35mm) for the fiord scale, telephoto (100-400mm) for dolphins and waterfalls"
> "Reflection shot: Best from the main wharf area — water calms in the evening"
> "Pro tip: Bring a polarizing filter to cut the glare on the water surface"

### 7. Nearby Alternatives

If conditions deteriorate during the activity, what can the user do instead nearby?

> "🔄 If conditions change:"
> 
> "If the weather turns while you're in the Kaikoura area, these are excellent rain-friendly alternatives within 15 minutes:"
> - Kaikoura Museum (local maritime history, small but interesting)
> - Kaikoura Lavender Farm (partially covered, great for photos even in rain)
> - Nin's Bin crayfish shack (eat fresh crayfish from a roadside caravan — iconic!)
> - Seal viewing at Point Kean (seals don't care about rain — and moody photos are stunning)

## Guidance Generation Pipeline

### Data Sources

1. **Activity database**: Core information about each activity (location, type, duration, requirements)
2. **Condition data**: Real-time and forecasted conditions from the monitoring system
3. **Knowledge base**: Destination-specific tips, stories, and insider knowledge
4. **User profile**: Interests, fitness level, preferences (to personalize tips)
5. **LLM generation**: For narrative content, stories, and nuanced advice that goes beyond structured data

### Generation Process

```
Activity Data + Conditions + User Profile + Knowledge Base
                        ↓
              AI Prompt Construction
                        ↓
              LLM Generates Guidance
                        ↓
              Validation & Enrichment
                        ↓
              Structured Output for UI
```

### AI Prompt Strategy

The LLM is prompted with:
1. Activity details (what, where, when)
2. Current conditions (full weather data)
3. User profile (what they care about)
4. Destination knowledge context (retrieved from knowledge base via RAG)
5. Tone guidelines (Buddi persona)
6. Output structure requirements

See [../03-ai/PROMPT-ARCHITECTURE.md](../03-ai/PROMPT-ARCHITECTURE.md) for the full prompting strategy.

## Quality Standards

### What Makes Good Activity Guidance

1. **Specific over generic**: "Arrive at 7:30 AM" beats "arrive early"
2. **Contextual**: Adapts to today's conditions, not boilerplate text
3. **Actionable**: The user knows exactly what to do after reading
4. **Honest**: If conditions are suboptimal, say so — don't sugarcoat
5. **Personality**: Buddi's enthusiasm should shine through without being forced
6. **Concise**: Each section is scannable in seconds — travelers don't read essays on their phone

### What to Avoid

- **Vague platitudes**: "Wear comfortable clothing" (no kidding)
- **Information overload**: 2000 words about the geological history of every rock formation
- **Incorrect confidence**: Presenting speculative information as fact
- **Repetitive tips**: Same "bring sunscreen" advice repeated for every outdoor activity
- **Tourist-trap suggestions**: Recommending mediocre attractions just to fill the day
