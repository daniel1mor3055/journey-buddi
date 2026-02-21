# Mobile Considerations

## Why Mobile Matters

During the planning phase, users may work from desktop or mobile. But during the trip — the phase where Journey Buddi's unique value is delivered — mobile is the primary (often only) interface. Travelers check their phone in bed for the morning briefing, glance at activity tips at the trailhead, and review swap suggestions at a café.

Mobile isn't just "responsive desktop." It's the primary design target for the most important phase of the product.

## Mobile-First Design Constraints

### Screen Real Estate
- Design for 375px width minimum (iPhone SE)
- Assume viewport height of ~650px (keyboard reduces this further)
- Critical information must be visible without scrolling (above the fold)
- Cards should use full width with comfortable horizontal margins (16px)

### Touch Targets
- Minimum tap target: 44x44px (Apple HIG) / 48x48dp (Material)
- Spacing between targets: minimum 8px
- Primary actions (Accept swap, Send) should be large and thumb-reachable
- Bottom-anchored primary actions for one-handed use

### Connectivity
- Travelers are often in areas with poor connectivity (remote NZ, Iceland highlands)
- Critical data (today's briefing, itinerary, maps for current area) should be cached
- Degrade gracefully: show cached content with "last updated" timestamp
- Queue actions (mark activity complete, accept swap) for when connectivity returns
- Don't show loading spinners for >5 seconds without explanation

### Battery Life
- Minimize background processing
- Don't poll APIs aggressively — use scheduled checks
- Optimize images (compress, appropriate resolution)
- Avoid continuous GPS tracking (only check location when needed)

### Outdoor Readability
- High contrast text (WCAG AA minimum, AAA preferred)
- Avoid light gray text on white backgrounds
- Condition badges use both color AND text labels
- Test designs in bright sunlight (turn screen brightness to max)

## Navigation Structure

### Bottom Tab Bar
```
┌──────┬──────┬──────┬──────┬──────┐
│  📋  │  📅  │  💬  │  🗺️  │  ⚙️  │
│Today │ Trip │ Chat │ Map  │ More │
└──────┴──────┴──────┴──────┴──────┘
```

- **Today:** Daily briefing / current day detail (primary during trip)
- **Trip:** Full itinerary overview
- **Chat:** Free-form conversation with Buddi
- **Map:** Route and attraction map
- **More:** Settings, profile, trip management

### Pre-Trip Navigation
During planning, the bottom tabs shift:
```
┌──────┬──────┬──────┬──────┬──────┐
│  🏠  │  💬  │  📋  │  🗺️  │  ⚙️  │
│Home  │ Plan │ Trip │ Map  │ More │
└──────┴──────┴──────┴──────┴──────┘
```

- **Home:** Dashboard with trip status and next steps
- **Plan:** Planning conversation with Buddi
- **Trip:** Itinerary (once generated)
- **Map:** Trip route map
- **More:** Settings

## Key Mobile Patterns

### Pull-to-Refresh
- Available on daily briefing to get fresh conditions
- Available on itinerary to refresh condition badges
- Shows last updated timestamp

### Swipe Gestures
- Swipe left/right on itinerary to navigate between days
- Swipe down on notification cards to dismiss
- No essential functionality locked behind swipes (always provide tap alternative)

### Bottom Sheets
- Activity detail opens as a bottom sheet (pull up for full screen)
- Swap suggestion slides up as a bottom sheet
- More natural than full-page transitions for secondary content

### Sticky Headers
- Day title stays fixed at top when scrolling through day details
- Weather summary bar stays visible when scrolling activities

## Mobile Performance Targets

| Metric | Target | Reasoning |
|--------|--------|-----------|
| Initial load (cold) | < 3 seconds | Travelers open the app wanting immediate info |
| Daily briefing load | < 1.5 seconds | Morning ritual, needs to be fast |
| Activity card expand | < 0.5 seconds | Tap response should feel instant |
| Map load | < 2 seconds | Map includes route and pins |
| Chat response (AI) | < 5 seconds (streamed) | Streaming mitigates perceived latency |

## Mobile-Specific Features

### Location-Aware Contextual Tips
When the user is near an attraction (GPS proximity):
- Surface relevant tips without the user having to search
- "You're near Cathedral Cove — remember, parking fills up by 9 AM. Head to the southern lot."
- Passive — no constant GPS tracking, just check when app is opened

### Quick-Glance Widget (Future)
Home screen widget showing:
- Today's top-line assessment (🟢 Great day ahead!)
- Next activity name and departure time
- Current conditions summary

### Notification Actions
Push notifications with actionable buttons:
- Swap suggestion: [Accept] [Decline] directly from notification
- Briefing: [Open Briefing] from notification
- Reminder: [Got it] to dismiss

## Progressive Web App (PWA)

For the initial web launch, implement as a Progressive Web App:

### PWA Benefits
- Installable on home screen (feels like native app)
- Push notifications via service worker
- Offline capability for cached content
- No app store approval process
- Shared codebase with desktop web

### PWA Limitations
- Slightly less smooth than native for complex gestures
- Push notification permission flow is different from native
- Limited background processing
- No access to some native APIs (fine for our use case)

### PWA Technical Requirements
- Service worker for offline support and push notifications
- Web app manifest for install capability
- App shell architecture for instant loading
- IndexedDB for local data storage

## Future: React Native Migration

When user demand justifies native apps:
- React Native enables code sharing with the web codebase (shared logic, API layer)
- Native benefits: smoother animations, better push notifications, home screen widget, deeper OS integration
- Migration path: Start with the most-used screens (daily briefing, itinerary) as native, keep less-used screens as web views
- Platform-specific features: iOS Live Activities for trip status, Android widgets for daily briefing
