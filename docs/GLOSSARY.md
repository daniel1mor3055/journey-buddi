# Glossary

## Product Terms

**Buddi**
The AI persona and brand character of Journey Buddi. Buddi is the knowledgeable, friendly travel companion that guides users through planning and accompanies them during trips. Named to evoke the feeling of having a travel buddy who knows everything.

**Planning Phase**
The pre-trip experience where the user converses with Buddi to build their itinerary. Includes preference gathering, attraction selection, route optimization, and itinerary generation.

**Live Companion Phase**
The during-trip experience where Buddi actively monitors conditions, delivers daily briefings, suggests itinerary adaptations, and provides activity-specific guidance.

**Daily Briefing**
The morning summary delivered to the traveler each day during an active trip. Contains overall condition assessment, activity-specific guidance, packing list, timing recommendations, and hidden gems.

**Evening Preview**
A brief notification the evening before, previewing tomorrow's plan with key preparation items.

**Condition Assessment**
The scoring of environmental conditions (weather, tides, solar, etc.) against an activity's requirements. Results in a color-coded rating: EXCELLENT (green), GOOD (yellow-green), FAIR (amber), POOR (red), UNSAFE (dark red).

**Swap Suggestion**
A recommended change to the itinerary, typically swapping two days, to place a weather-sensitive activity on a day with better conditions. Always presented with reasoning and impact analysis.

**Activity Guidance**
Expert-level advice for a specific activity on a specific day, including condition-specific packing, optimal timing, pro tips, stories, safety notes, and photography guidance.

**Condition Profile**
A definition of what environmental conditions matter for a specific activity type (hiking, marine, scenic, etc.) and what the ideal, acceptable, and dealbreaker thresholds are.

**Flex Day**
A buffer day inserted into the itinerary to accommodate weather-based swaps and spontaneous exploration. Positioned strategically to maximize swap flexibility.

**Cluster**
A geographic grouping of nearby attractions that can be visited from a single base location. Used in route optimization.

## Technical Terms

**Magic Link**
A passwordless authentication method where users receive an email with a unique, time-limited link. Clicking the link authenticates them without needing to remember a password.

**RAG (Retrieval Augmented Generation)**
A technique where relevant knowledge is retrieved from a database (via semantic search) and injected into an LLM prompt, grounding the AI's response in specific, accurate information rather than relying solely on training data.

**Vector Store**
A database optimized for storing and searching high-dimensional vectors (embeddings). Used for semantic search in the knowledge base. Chroma for MVP, Pinecone for production.

**Embedding**
A numerical representation of text content as a high-dimensional vector. Enables semantic similarity search — finding content that means similar things, even if the words are different.

**Tool/Function Calling**
An LLM capability where the AI can invoke defined functions (APIs, database queries, calculations) to access real-time data during a conversation. Essential for Buddi to check weather, look up attractions, etc.

**PostGIS**
A PostgreSQL extension that adds support for geographic objects and spatial queries. Enables distance calculations, area searches, and route optimization using real-world coordinates.

**Celery**
A distributed task queue for Python. Used for background jobs like generating daily briefings, monitoring conditions, and sending notifications.

**PWA (Progressive Web App)**
A web application that provides native-app-like experiences including offline capability, push notifications, and home screen installation. Our initial deployment model before native mobile apps.

**WebSocket**
A protocol enabling full-duplex, real-time communication between client and server. Used for streaming AI chat responses token-by-token.

**VAPID (Voluntary Application Server Identification)**
A protocol used for identifying the server sending web push notifications. Required for PWA push notification support.

## External Service Terms

**Gemini (Google)**
Google's large language model family. Our primary AI model for generating conversational responses, itineraries, briefings, and guidance.

**OpenWeatherMap**
Weather data API providing current conditions and forecasts. One of our primary weather data sources.

**Open-Meteo**
Free, open-source weather API. Used as a fallback/alternative weather data source.

**WorldTides**
API providing global tide prediction data. Used for coastal activity planning.

**NOAA SWPC**
National Oceanic and Atmospheric Administration Space Weather Prediction Center. Provides aurora/geomagnetic activity forecasts (Kp index).

**Mapbox**
Map visualization and routing platform. Used for displaying trip routes, attraction pins, and calculating driving distances/times.

**DOC (Department of Conservation)**
New Zealand's conservation authority. Source of official trail conditions, closures, and conservation area information.

**MetService**
New Zealand's official weather forecasting service. A key source for NZ-specific weather data.

## Data & Metrics Terms

**Condition Score**
A numerical score (0-100) representing how suitable current or forecasted conditions are for a specific activity. Derived from weighted evaluation of relevant environmental factors.

**Improvement Score**
The net benefit of a proposed itinerary swap, measured as the condition improvement for the primary activity minus the condition impact on the displaced activity.

**Disruption Score**
A measure of how much hassle a swap causes the user — additional driving, accommodation changes, cascading day modifications, etc.

**Swap Threshold**
The minimum improvement-to-disruption ratio required before Buddi suggests a swap. Calibrated to avoid excessive change suggestions while catching genuinely beneficial opportunities.

## Abbreviations

| Abbreviation | Full Term |
|-------------|-----------|
| AI | Artificial Intelligence |
| API | Application Programming Interface |
| B2B | Business to Business |
| B2C | Business to Consumer |
| CTA | Call to Action |
| DOC | Department of Conservation (NZ) |
| JWT | JSON Web Token |
| LLM | Large Language Model |
| MVP | Minimum Viable Product |
| NZ | New Zealand |
| PWA | Progressive Web App |
| RAG | Retrieval Augmented Generation |
| REST | Representational State Transfer |
| SSR | Server-Side Rendering |
| TTL | Time to Live |
| UX | User Experience |
| WS | WebSocket |
