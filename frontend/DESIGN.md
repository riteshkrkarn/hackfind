---
name: Hackfind
description: Check-in desk for personalized hackathon matches
colors:
  desk: "#0b1f1a"
  field: "#f2f4f1"
  band: "#e8ff47"
  deep: "#1a6b52"
  ink: "#0b1f1a"
  muted: "#3d524c"
  badge: "#e8ece6"
  rail: "#d5dbd4"
typography:
  display:
    fontFamily: "Chakra Petch, sans-serif"
    fontWeight: 700
    letterSpacing: "-0.03em"
  body:
    fontFamily: "Atkinson Hyperlegible, sans-serif"
    fontWeight: 400
  mono:
    fontFamily: "Fragment Mono, monospace"
    fontWeight: 400
rounded:
  none: "0px"
  sm: "2px"
spacing:
  section: "5rem"
  hero-pad: "4rem"
components:
  button-primary:
    backgroundColor: "{colors.band}"
    textColor: "{colors.desk}"
    rounded: "{rounded.none}"
    padding: "12px 20px"
  badge-card:
    backgroundColor: "{colors.badge}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
---

## Overview

Hackfind’s visual world is a hackathon **check-in desk**: dark desk surfaces, cool paper field, lime wristband signal, and matte badge stock on a rail. Persuade surfaces lead with the desk mark and a claimable rail; operate surfaces keep the same tokens with quieter chrome.

## Colors

- **desk** `#0b1f1a` — hero/footer ground, strap ink
- **field** `#f2f4f1` — reading ground (cool, not cream)
- **band** `#e8ff47` — wristband edge + primary CTA only
- **deep** `#1a6b52` — secondary marks, deadlines, course labels
- **muted** `#3d524c` — body secondary on field
- Never scatter lime across labels or counters

## Typography

- **Display:** Chakra Petch — desk mark, section titles, CTAs
- **Body:** Atkinson Hyperlegible — pitch and explanatory copy
- **Mono:** Fragment Mono — deadlines, match counts, course indices, source tags

## Layout

- Landing first viewport: brand → check-in headline → CTA → source line → badge rail
- How-it-works as ascending courses with hairline rules (sequence is informational)
- App shell uses field ground + rail border; no lime except primary actions

## Elevation & Depth

- Badges: soft drop shadow + inset highlight on matte texture (`/textures/badge-matte.png`)
- No glassmorphism; no zero-offset glow

## Shapes

- Sharp CTAs (0 radius) for desk-print feel
- Badges slight sm radius; elastic strap as rounded pill fragment

## Components

- **Primary button:** band fill, desk text, rectangular
- **Match badge:** matte texture, left band edge, top elastic strap, mono deadline
- **Rail:** subtle tick marks, horizontal scroll on small screens

## Do's and Don'ts

**Do**
- Keep lime on band edges and primary CTAs only
- Label synthetic demo data as synthetic
- Prefer rail/list proof over feature-card grids

**Don't**
- Generic SaaS purple gradients or cream paper defaults
- App nav chrome on the marketing landing
- Neon “hacker terminal” aesthetic
