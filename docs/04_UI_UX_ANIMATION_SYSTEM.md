# 04 — Approved UI/UX and Animation System

## Visual direction
**Premium futuristic AI Command Center.** The approved reference is a deep navy/graphite interface with electric violet and cyan-blue glow, a luminous AURA mark, orbiting particles, sequential loading and a polished dashboard reveal.

Do not turn the product into a cluttered cyberpunk game UI. It must remain professional, readable, calm and usable for long work sessions.

## Design tokens (initial direction; refine with accessible contrast testing)
- Background: deep navy/graphite.
- Surfaces: layered charcoal/navy panels.
- Primary accent: electric violet.
- Secondary accent: cyan/blue.
- Text: high-contrast off-white.
- Muted text: cool grey.
- Borders: subtle low-contrast strokes.
- Radius: consistent medium/large rounding.
- Typography: readable modern sans-serif with clear hierarchy.

Create centralized design tokens. Do not scatter arbitrary colors, spacing or shadows across components.

## Startup sequence
1. AURA logo reveal.
2. Light/orbit particle animation.
3. Tagline: “Your AI Powerhouse”.
4. Module initialization status.
5. Progress animation.
6. Workspace preparation.
7. Smooth dashboard transition.

Do not fake actual progress. If startup progress is indeterminate, use an honest animated loading indicator. Show percentage only when it reflects real completed work.

## Every module must share the design language
- Route/page transitions.
- Sequential card entrance where useful.
- Smooth modal, drawer and tab transitions.
- Hover/focus feedback and subtle glow.
- AI activity indicators.
- Agent execution timeline and live status.
- Animated charts with reduced-motion fallback.
- File upload and export progress.
- Skeleton loading states.
- Clear empty, success and error states.
- Responsive layouts.
- Keyboard navigation and visible focus.
- Reduced-motion preference support.

## Animation implementation
- Framer Motion: standard UI transitions and state changes.
- GSAP: only complex choreographed sequences.
- Three.js: optional limited 3D hero/brand effects; never required for core usability.
- CSS transitions for simple hover/focus effects.
- Lazy-load expensive visual scenes.
- Respect `prefers-reduced-motion`.
- Offer an in-app animation intensity setting: Full / Reduced / Off.
- Avoid animating large lists or expensive charts unnecessarily.
- Maintain smooth performance on ordinary laptops and mobile browsers.

## Layout
- Persistent left navigation on desktop, collapsible.
- Top bar with global search, notifications, task status and profile.
- Main workspace with clear content hierarchy.
- Optional right-side context/agent panel.
- Mobile navigation adapts to compact layout.
- Global command palette (Ctrl/Cmd + K).
- Dark mode default; accessible light mode alternative.

## Required screens
- Marketing/landing page.
- Sign up, sign in, email verification, password recovery.
- Onboarding and workspace selection.
- Main dashboard.
- Universal chat.
- Research workspace.
- Agent Control Room.
- Knowledge Base.
- Document Studio.
- Data Studio.
- Coding Lab.
- Workflow builder.
- Model Arena.
- Evaluation Center.
- File manager.
- Project workspace.
- Usage and billing/plan status (do not charge unless explicitly implemented and approved).
- Settings, memory controls, language controls.
- Admin dashboard.
- Error, offline, maintenance and permission screens.

## Acceptance
A visual regression/screenshot review must inspect key screens at desktop, tablet and mobile sizes. No page may use a completely unrelated visual theme.
