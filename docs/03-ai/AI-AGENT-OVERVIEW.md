# AI Agent System — Overview

## Role of AI in Journey Buddi

AI is not a feature of Journey Buddi — it IS Journey Buddi. Every core interaction is powered by AI:

- The planning conversation is driven by an AI agent
- Itinerary generation uses AI reasoning over constraints and preferences
- Daily briefings are AI-generated from condition data and destination knowledge
- Swap suggestions are AI-evaluated decisions
- Activity guidance is AI-composed from multiple data sources
- The "expert guide" personality IS an AI persona

Without AI, Journey Buddi would be a better spreadsheet. With AI, it's a travel companion.

## AI Architecture — High Level

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACE                         │
│              (Web App / Mobile App)                       │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│                 BUDDI AGENT LAYER                         │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Planning    │  │    Live      │  │   General     │  │
│  │   Agent       │  │  Companion   │  │   Chat        │  │
│  │              │  │   Agent      │  │   Agent       │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                 │           │
│  ┌──────▼─────────────────▼─────────────────▼───────┐  │
│  │              TOOL / FUNCTION LAYER                │  │
│  │                                                   │  │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐   │  │
│  │  │Weather │ │ Tides  │ │ Maps   │ │ Know-  │   │  │
│  │  │  API   │ │  API   │ │  API   │ │ ledge  │   │  │
│  │  │        │ │        │ │        │ │  Base   │   │  │
│  │  └────────┘ └────────┘ └────────┘ └────────┘   │  │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐   │  │
│  │  │ Solar  │ │Itiner- │ │ User   │ │ Route  │   │  │
│  │  │Activity│ │ary DB  │ │Profile │ │Optimize│   │  │
│  │  │  API   │ │        │ │        │ │        │   │  │
│  │  └────────┘ └────────┘ └────────┘ └────────┘   │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

## Agent Types

### 1. Planning Agent
**Purpose:** Guide the user through trip planning via structured conversation.

**Capabilities:**
- Conducts the preference gathering conversation
- Presents destination-specific options
- Evaluates and recommends attractions based on route and preferences
- Generates optimized itineraries
- Handles itinerary refinement requests

**Personality:** Enthusiastic, knowledgeable, opinionated (has recommendations), collaborative.

**Context window:** Maintains full conversation history + user profile + destination knowledge.

### 2. Live Companion Agent
**Purpose:** Monitor conditions, generate daily briefings, and suggest itinerary adaptations.

**Capabilities:**
- Analyzes condition data against activity requirements
- Generates daily briefings with personalized guidance
- Evaluates swap opportunities and generates suggestions
- Provides activity-specific guidance with pro tips
- Handles in-trip questions and changes

**Personality:** Calm, helpful, decisive but not pushy. Like a guide who knows when to speak up and when to let you enjoy the moment.

**Context window:** Current itinerary + recent conditions + user profile + conversation history.

### 3. General Chat Agent
**Purpose:** Handle ad-hoc questions, requests, and conversations that don't fit the structured planning or companion flows.

**Capabilities:**
- Answer questions about the destination
- Provide recommendations for restaurants, activities not in the itinerary
- Share stories and cultural context
- Handle itinerary modification requests
- Provide logistical help (currency, customs, emergency info)

**Personality:** Same Buddi persona — warm, knowledgeable, helpful.

**Context window:** User profile + current itinerary + destination knowledge.

## LLM Selection

### Primary LLM: Google Gemini

**Rationale:**
- Strong reasoning capabilities for complex itinerary optimization
- Good at structured output generation (JSON, formatted text)
- Multimodal capabilities (future: photo-based location recognition)
- Competitive pricing for high-volume usage
- Long context window for maintaining conversation state

### Fallback/Complementary: OpenAI GPT-4 or Anthropic Claude

**Use cases for fallback:**
- If Gemini has availability issues
- For specific tasks where another model performs better (discovered through testing)
- A/B testing different models for quality comparison

### Model Usage Strategy

| Task | Model | Reasoning |
|------|-------|-----------|
| Planning conversation | Gemini Pro | Needs strong reasoning + personality |
| Itinerary generation | Gemini Pro | Complex constraint satisfaction |
| Daily briefing generation | Gemini Flash (or equivalent fast tier) | Needs speed, lower complexity |
| Condition assessment | Gemini Flash | Structured evaluation, lower complexity |
| Activity guidance | Gemini Pro | Rich, creative, knowledgeable content |
| Swap evaluation | Gemini Pro | Complex multi-factor decision making |
| General chat | Gemini Pro | Natural conversation, broad knowledge |

### Cost Projection (Rough)

Per trip (assuming 18-day trip):
- Planning phase: ~50-100 LLM calls → ~$0.50-1.00
- Daily briefings: 18 calls → ~$0.20
- Activity guidance: ~60 calls → ~$0.60
- Swap evaluations: ~10-20 calls → ~$0.20
- General chat: ~30 calls → ~$0.30
- **Estimated total per trip: $2-3**

At scale (10,000 trips/month): ~$20,000-30,000/month in LLM costs. Manageable.

## AI Tooling & Framework

### Agent Framework

Use **LangChain** or a lightweight custom agent framework for:
- Tool/function calling orchestration
- Conversation memory management
- Prompt template management
- Output parsing and validation
- Streaming response support

### Tool/Function Calling

The AI agents interact with external systems through defined tools:

```python
available_tools = [
    get_weather_forecast(location, date_range),
    get_tide_data(location, date),
    get_solar_data(location, date),
    get_aurora_forecast(location, date),
    search_attractions(destination, category, filters),
    get_attraction_details(attraction_id),
    calculate_route(origin, destination, mode),
    get_driving_time(origin, destination),
    get_user_profile(user_id),
    get_itinerary(trip_id),
    update_itinerary(trip_id, changes),
    search_knowledge_base(query, destination),
]
```

### Retrieval Augmented Generation (RAG)

For destination-specific knowledge, we use RAG to ground the LLM's responses in curated, accurate information:

1. **Knowledge Base**: Curated destination data (attractions, tips, logistics, stories)
2. **Vector Store**: Embeddings of knowledge base content for semantic search
3. **Retrieval**: When generating guidance, retrieve relevant knowledge chunks
4. **Augmentation**: Include retrieved chunks in the LLM prompt as context
5. **Generation**: LLM synthesizes a response grounded in real data

See [KNOWLEDGE-SYSTEM.md](./KNOWLEDGE-SYSTEM.md) for the full knowledge architecture.

## AI Quality & Safety

### Hallucination Prevention
- Ground responses in structured data (weather APIs, tide data) whenever possible
- Use RAG for destination knowledge instead of relying on LLM training data
- For safety-critical information (trail closures, volcanic alerts), always cite the data source
- Implement confidence scoring — when the AI isn't sure, it says so

### Response Validation
- Structured outputs are validated against schemas
- Itinerary changes are validated for logical consistency (no impossible drives, date conflicts)
- Condition assessments are cross-checked against raw data thresholds
- Critical safety information is never AI-generated — it comes from official sources

### Tone Consistency
- All agents share the Buddi persona guidelines
- Response tone is calibrated through system prompts and few-shot examples
- Regular review of generated content to catch tone drift

### Feedback Loop
- Users can rate daily briefings (helpful / not helpful)
- Swap suggestion acceptance/rejection rates tracked
- Post-trip satisfaction surveys
- Data feeds back into prompt optimization and model selection
