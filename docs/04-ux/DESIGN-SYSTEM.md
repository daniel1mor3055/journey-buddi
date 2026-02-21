# Design System

## Overview

Journey Buddi's design system defines the visual language, component library, and design tokens that ensure consistency across web and future mobile platforms. The aesthetic is **modern, clean, warm, and premium** — it should feel like a high-quality travel magazine crossed with a thoughtful productivity app.

## Design Values

1. **Warmth over clinical:** Rounded corners, warm colors, friendly typography
2. **Clarity over decoration:** Every visual element serves a purpose
3. **Space and breathing room:** Generous whitespace, no cramming
4. **Photography-forward:** Beautiful destination imagery throughout
5. **Accessible:** WCAG AA compliant, readable in bright sunlight (outdoor usage)

## Color Palette

### Primary Colors
```
Buddi Blue:     #2563EB  — Primary actions, links, Buddi's accent
Ocean Teal:     #0D9488  — Secondary actions, success states
Sunset Warm:    #F59E0B  — Highlights, warnings, attention
```

### Neutrals
```
Ink:            #1E293B  — Primary text
Slate:          #475569  — Secondary text
Mist:           #94A3B8  — Tertiary text, placeholders
Cloud:          #E2E8F0  — Borders, dividers
Snow:           #F8FAFC  — Backgrounds
White:          #FFFFFF  — Cards, elevated surfaces
```

### Condition Colors
```
Excellent:      #22C55E  (🟢 green)
Good:           #84CC16  (🟡 yellow-green)
Fair:           #F59E0B  (🟠 amber)
Poor:           #EF4444  (🔴 red)
Unsafe:         #7C2D12  (⛔ dark red)
```

### Semantic Colors
```
Success:        #22C55E
Warning:        #F59E0B
Error:          #EF4444
Info:           #3B82F6
```

## Typography

### Font Family
- **Headings:** Inter (clean, modern, excellent readability)
- **Body:** Inter
- **Chat/Buddi messages:** Inter (same family, different weight/style for personality)
- **Monospace (data):** JetBrains Mono (for condition data, times)

### Type Scale
```
Display:        36px / 2.25rem  — Hero text, trip title
H1:             30px / 1.875rem — Page titles
H2:             24px / 1.5rem   — Section headers
H3:             20px / 1.25rem  — Card titles, day headers
H4:             18px / 1.125rem — Activity titles
Body:           16px / 1rem     — Default text, chat messages
Body Small:     14px / 0.875rem — Secondary info, metadata
Caption:        12px / 0.75rem  — Labels, timestamps
```

### Font Weights
```
Regular:  400 — Body text
Medium:   500 — Emphasized body, card titles
Semibold: 600 — Section headers, important actions
Bold:     700 — Page titles, key information
```

## Spacing

### Spacing Scale (4px base)
```
xs:   4px    — Tight spacing within components
sm:   8px    — Component internal padding
md:   16px   — Card padding, between related elements
lg:   24px   — Between sections
xl:   32px   — Major section gaps
2xl:  48px   — Page-level spacing
3xl:  64px   — Hero sections, major breaks
```

## Components

### Cards

The primary content container. Used for activity cards, day cards, tip cards.

```
Card {
  background: white
  border-radius: 12px
  padding: 16px
  shadow: 0 1px 3px rgba(0,0,0,0.1)
  border: 1px solid Cloud (#E2E8F0)
}

Card:hover {
  shadow: 0 4px 12px rgba(0,0,0,0.1)
  transform: translateY(-1px)
}
```

**Variants:**
- **Default card:** White background, subtle border
- **Highlighted card:** Tinted background (light blue for active day)
- **Alert card:** Left border accent (amber for warning, red for urgent)
- **Buddi card:** Slight blue tint background (Buddi's recommendations)

### Buttons

```
Primary Button {
  background: Buddi Blue (#2563EB)
  color: white
  border-radius: 8px
  padding: 12px 24px
  font-weight: 600
  font-size: 16px
}

Secondary Button {
  background: transparent
  color: Buddi Blue
  border: 2px solid Buddi Blue
  border-radius: 8px
  padding: 10px 22px
}

Ghost Button {
  background: transparent
  color: Slate (#475569)
  padding: 12px 24px
}
```

### Choice Cards (Planning Chat)

Interactive selection cards used during the planning conversation.

```
ChoiceCard {
  background: white
  border: 2px solid Cloud
  border-radius: 12px
  padding: 16px
  text-align: center
  cursor: pointer
}

ChoiceCard:selected {
  border-color: Buddi Blue
  background: #EFF6FF (very light blue)
}

ChoiceCard .icon {
  font-size: 32px
  margin-bottom: 8px
}

ChoiceCard .label {
  font-weight: 600
  font-size: 16px
}

ChoiceCard .description {
  font-size: 14px
  color: Slate
}
```

### Chat Bubbles

```
BuddiMessage {
  background: #F1F5F9 (light gray)
  border-radius: 16px 16px 16px 4px
  padding: 12px 16px
  max-width: 85%
  align: left
}

UserMessage {
  background: Buddi Blue (#2563EB)
  color: white
  border-radius: 16px 16px 4px 16px
  padding: 12px 16px
  max-width: 75%
  align: right
}
```

### Condition Badge

Small visual indicator of condition quality.

```
ConditionBadge {
  display: inline-flex
  align-items: center
  gap: 6px
  padding: 4px 10px
  border-radius: 20px
  font-size: 14px
  font-weight: 500
}

ConditionBadge.excellent { background: #DCFCE7; color: #166534 }
ConditionBadge.good      { background: #ECFCCB; color: #3F6212 }
ConditionBadge.fair      { background: #FEF3C7; color: #92400E }
ConditionBadge.poor      { background: #FEE2E2; color: #991B1B }
ConditionBadge.unsafe    { background: #7C2D12; color: #FFFFFF }
```

### Timeline

Vertical timeline for day view.

```
Timeline {
  border-left: 2px solid Cloud
  margin-left: 24px
  padding-left: 24px
}

TimelineItem {
  position: relative
  margin-bottom: 16px
}

TimelineItem .dot {
  width: 12px
  height: 12px
  border-radius: 50%
  background: Buddi Blue
  position: absolute
  left: -31px
}

TimelineItem .time {
  font-size: 14px
  color: Mist
  font-family: monospace
}

TimelineItem .content {
  font-size: 16px
}
```

## Icons

Use a consistent icon set throughout. Recommended: **Lucide Icons** (clean, consistent, MIT licensed).

Supplement with emoji for activity types (🐋 🏔️ 🚣 etc.) and condition status (🟢 🟡 🟠 🔴 ⛔).

## Responsive Design

### Breakpoints
```
Mobile:   < 640px    — Single column, full-width cards
Tablet:   640-1024px — Optional sidebar, wider cards
Desktop:  > 1024px   — Sidebar navigation, multi-column layouts
```

### Mobile-First Priority
- All core experiences must work beautifully on 375px width (iPhone SE)
- Touch targets minimum 44x44px
- Bottom navigation for primary sections
- No hover-dependent interactions (everything tap-accessible)

## Dark Mode (Future)

Not in MVP but design with dark mode in mind:
- Use semantic color tokens (not hardcoded hex values)
- Ensure sufficient contrast ratios in both modes
- Test imagery against dark backgrounds

## Accessibility

- All text meets WCAG AA contrast ratio (4.5:1 for body, 3:1 for large text)
- Interactive elements have visible focus states
- Screen reader labels for all interactive components
- Condition status communicated through text labels, not just color
- Outdoor readability: test designs in bright sunlight scenarios
