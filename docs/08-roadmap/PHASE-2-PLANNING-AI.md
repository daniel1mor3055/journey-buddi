# Phase 2: Planning AI — Weeks 4-8

## Goal

Build the conversational planning experience. A user can chat with Buddi, tell Buddi about their travel preferences, explore NZ attractions, and receive a complete day-by-day itinerary. This is the phase where Journey Buddi becomes a real product.

## Week 4: AI Agent Foundation

### Tasks

**Day 1-2: LLM Integration**
- Set up Google Gemini API integration
  - API key configuration
  - Client wrapper with retry logic and error handling
  - Token counting and cost tracking
  - Response streaming support
- Create prompt template system
  - Load prompts from files
  - Variable injection
  - Version tracking
- Write and test the Planning Agent system prompt (from PERSONA-BUDDI.md and PROMPT-ARCHITECTURE.md)

**Day 3-4: Chat Backend**
- Implement Conversation and Message database models
- Build conversation CRUD endpoints
- Implement WebSocket endpoint for real-time chat
  - Authentication on WebSocket connection
  - Message handling (receive user input → process → stream response)
  - Connection lifecycle management
- Build conversation state management (track planning step)

**Day 5: Chat Frontend**
- Build chat UI component:
  - Buddi message bubbles (left-aligned, with avatar)
  - User message bubbles (right-aligned)
  - Typing indicator (while waiting for AI)
  - Streaming text display (tokens appear as they arrive)
- Connect to WebSocket endpoint
- Handle connection lifecycle (connect, reconnect, disconnect)
- Store conversation in Zustand for local state

### Deliverables
- User can chat with Buddi in real-time
- AI responses stream token-by-token
- Conversation persists to database
- Basic chat works end-to-end

## Week 5: Structured Planning Conversation

### Tasks

**Day 1-2: Choice Card Components**
- Build choice card UI components:
  - Single-select card (3 options with icons)
  - Multi-select gallery (interest selection grid)
  - Recommendation card (with accept/alternative)
  - Confirmation summary card
- Build card selection handling (user taps card → sends structured data)
- Build progress indicator component (planning steps)

**Day 3-4: Planning Flow Logic**
- Implement planning state machine (from CONVERSATION-DESIGN.md):
  - PROFILE → DESTINATION → INTERESTS → ATTRACTION_SELECTION → ROUTE → TRANSPORT → PACE → ITINERARY → CONFIRMED
- Build step-specific prompt templates
- Implement structured output parsing (AI returns JSON for choice cards)
- Handle back-navigation (return to previous step)
- Handle free-text fallback (when user types instead of tapping)

**Day 5: Profile & Destination Steps**
- Implement user profile gathering:
  - Adventure level selection
  - Fitness level selection
  - Pace preference selection
  - Budget indication
- Implement interest multi-select
- Implement destination selection (NZ only for now)
- Implement date selection
- Store all selections in trip planning_state

### Deliverables
- Beautiful choice cards render in the chat
- User can complete profile and interest selection through structured cards
- Planning state tracks progress and allows back-navigation
- All selections persist to database

## Week 6: NZ Knowledge Base & Attraction Curation

### Tasks

**Day 1-2: Knowledge Base Setup**
- Set up Chroma vector store
- Create NZ attraction data (from NZ-ATTRACTIONS-DATABASE.md):
  - 20-30 key attractions with full metadata
  - Pro tips for each attraction
  - Stories and cultural context
  - Condition profiles
- Build knowledge ingestion pipeline (JSON → embeddings → Chroma)
- Build RAG retrieval function (query → relevant knowledge chunks)

**Day 3-4: Interest Deep Dive Flow**
- For each selected interest category, implement:
  - Retrieve relevant attractions from knowledge base
  - AI generates destination-specific options with descriptions
  - Present as multi-select gallery cards
  - Handle attraction selection and storage
- Implement location recommendation logic:
  - When an activity is available at multiple locations
  - AI recommends best location based on route context
  - Present as recommendation card with reasoning

**Day 5: Attraction Storage & State**
- Store selected attractions in database (linked to trip)
- Implement attraction detail view (expand for more info)
- Handle attraction add/remove during planning
- Build "selected attractions summary" card

### Deliverables
- Chroma knowledge base with NZ attraction data
- User can explore attractions by interest category
- AI recommends specific locations with reasoning
- Selected attractions are stored and viewable

## Week 7: Route & Itinerary Generation

### Tasks

**Day 1-2: Route Optimization**
- Implement geographic clustering algorithm:
  - Group selected attractions by proximity
  - Name clusters by area
  - Calculate inter-cluster distances
- Implement route optimization:
  - Consider entry/exit points
  - Minimize total driving time
  - Avoid backtracking
- Present route to user on map (Mapbox integration start)
- Handle route approval/modification

**Day 3-4: Transport Recommendation**
- Implement transport recommendation logic (from TRANSPORT-LOGIC.md):
  - Analyze each route segment
  - Recommend campervan vs car vs mixed
  - Generate reasoning text
- Present transport recommendation as a recommendation card
- Handle user transport preference selection

**Day 5: Itinerary Assembly**
- Implement the itinerary generation engine (from ITINERARY-GENERATION.md):
  - Distribute activities across days based on pace preference
  - Apply scheduling rules (morning vs afternoon, strenuous spacing)
  - Insert flex days for weather flexibility
  - Generate day titles and summaries
  - Include transport segments between days
- Build the AI review step (AI validates and enriches the generated itinerary)
- Store generated itinerary in database

### Deliverables
- Route optimizer clusters attractions and builds an efficient route
- Transport recommendations with reasoning
- Full day-by-day itinerary generated and stored

## Week 8: Itinerary View & Review

### Tasks

**Day 1-2: Itinerary View UI**
- Build itinerary overview page:
  - Trip summary bar (days, activities, km)
  - Day cards list (scrollable, tappable)
  - Map view with route and attraction pins
- Build day detail page:
  - Activity list with details
  - Timeline view
  - Transport segment info
  - Area notes

**Day 3-4: Itinerary Editing**
- Implement itinerary modification via chat:
  - "Add an activity" → Buddi suggests placement
  - "Remove [activity]" → Buddi re-optimizes
  - "Swap day X and Y" → Buddi validates and executes
- Implement day locking (user can lock days with bookings)
- Re-generate affected days when changes are made

**Day 5: Planning Flow Polish**
- End-to-end testing of the full planning flow
- Fix edge cases and error handling
- Polish transition between planning steps
- Add "Confirm Itinerary" celebration moment
- Trip status transitions (planning → confirmed)

### Deliverables
- Complete itinerary viewable as list and map
- Day detail pages with activity information
- Itinerary editable through Buddi chat
- Full planning flow works end-to-end

## Phase 2 Definition of Done

- [ ] User can complete the full planning conversation with Buddi
- [ ] Buddi asks structured questions through choice cards
- [ ] NZ attractions are presented based on user interests
- [ ] AI recommends locations with clear reasoning
- [ ] Route is optimized and shown on a map
- [ ] Transport mode is recommended with reasoning
- [ ] Complete day-by-day itinerary is generated
- [ ] Itinerary is viewable, modifiable, and persistable
- [ ] Knowledge base provides accurate NZ attraction information
- [ ] The experience feels like talking to a knowledgeable friend
