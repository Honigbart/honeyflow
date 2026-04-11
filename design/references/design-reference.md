# Design Reference

## Tech Stack Conflicts

These combinations produce silent failures or incoherent output. Never combine them:

| Never combine | Why |
|---|---|
| Tailwind + CSS Modules on the same element | Specificity conflicts, unpredictable cascade |
| Framer Motion + CSS transitions on the same element | Double-animating the same property causes jank |
| styled-components or emotion + Tailwind | Two competing class systems fighting for the same DOM node |
| Heroicons + Lucide + Font Awesome in one project | Visual inconsistency, size mismatches, bundle bloat |
| Multiple Google Font families as display fonts | Competing personalities cancel each other out |
| Glassmorphism backdrop-filter + solid `border: 1px solid` | Solid borders shatter the layered depth illusion |
| Dark background + `#ffffff` text at full opacity | Too harsh; use `rgba(255,255,255,0.85)` or `#f0f0f0` |
| Tailwind v4 `@theme` + dynamically constructed class names | `@theme` tokens generate utility classes JIT; if class names are built from variables or not present in scanned source, the class is purged and styles silently disappear. Fix: use static class names in source files, add to `safelist`, or define custom colors in `:root` + `extend.colors` in `tailwind.config.js` instead of `@theme` |

Before writing the first component, name the single CSS strategy for the project: Tailwind only, CSS Modules only, or CSS-in-JS only. Do not drift from it.

## Common Traps

Before submitting, check whether any of the following slipped in without intention:

- A purple or blue gradient over white as the hero background
- A three-part hero: large headline, one-line subtext, two CTA buttons side by side
- A grid of cards with identical rounded corners, identical drop shadows, identical padding
- A top navigation bar with logo left, links center, primary action far right
- Sections that alternate between white and `#f9f9f9`
- A centered icon or illustration sitting above a heading above a paragraph
- A four-column footer with equal-weight columns

Any of these can appear if they serve the design intentionally. They cannot appear by default.

Final test: if you swapped in completely different content and the layout still made sense without changes, you built a template, not a design. Redo it.

## Production Quality Baseline

Check before handoff. These are not aesthetic choices, they are non-negotiable.

> Treat the sections below as craft details, not defaults. Only apply them when they serve the locked visual direction. If removing a detail changes nothing about how the interface feels, leave it out.

### Accessibility
- Icon-only buttons need `aria-label`
- Actions use `<button>`, navigation uses `<a>` (not `<div onClick>`)
- Images need `alt` (or `alt=""` if decorative)
- Visible focus states: `focus-visible:ring-*` or equivalent; never `outline: none` without replacement

### Animation
- Honor `prefers-reduced-motion`: disable or reduce animations when set
- Animate `transform`/`opacity` only (compositor-friendly, no layout thrash)
- Never `transition: all`; list properties explicitly
- Interruptible animations: prefer CSS transitions for interactive state changes (hover, toggle, open/close) because they retarget mid-animation; reserve keyframe animations for staged sequences that run once (e.g., staggered page enters)
- Staggered enter: split content into semantic chunks with ~100ms delay; titles into words at ~80ms; typical enter uses `opacity: 0 → 1`, `translateY(12px) → 0`, and `blur(4px) → 0`
- Subtle exit: use a small fixed `translateY(-12px)` instead of full height; keep duration ~150ms `ease-in`, shorter and softer than enter
- Contextual icon swaps: animate with `scale: 0.25 → 1`, `opacity: 0 → 1`, and `blur: 4px → 0px`. With a spring library: `{ type: "spring", duration: 0.3, bounce: 0 }`. Without: keep both icons in DOM (one absolute) and cross-fade with CSS using `cubic-bezier(0.2, 0, 0, 1)`
- Scale on press: buttons use `scale(0.96)` on active/press via CSS transitions so the press can be interrupted; add a `static` prop to disable when motion would be distracting
- Page-load guard: use `initial={false}` on animated presence wrappers for toggles, tabs, and icon swaps to prevent enter animations on first render; do not use it for intentional page-load entrance sequences

### Performance
- Transition specificity: never `transition: all`; list exact properties (e.g., `transition-property: scale, opacity`). Tailwind's `transition-transform` covers `transform, translate, scale, rotate`; use `transition-[scale,opacity,filter]` for mixed properties
- GPU compositing: only use `will-change` for `transform`, `opacity`, or `filter`. Never `will-change: all`. Add only when you notice first-frame stutter; do not apply preemptively to every element
- Images: explicit `width` and `height` (prevents layout shift)
- Below-fold images: `loading="lazy"`
- Critical fonts: `font-display: swap`

### Touch and Mobile
- `touch-action: manipulation` (prevents double-tap zoom delay)
- Full-bleed layouts: `env(safe-area-inset-*)` for notch devices
- Modals and drawers: `overscroll-behavior: contain`
- Hover guard: wrap interactive hover states with `@media(hover:hover)` so they only apply on pointer devices, not touch screens. Tailwind: `[@media(hover:hover)]:hover:bg-...`. Without this, a tapped element on mobile gets a permanent hover state until the next tap elsewhere.

### Typography Details
- Text wrapping: `text-wrap: balance` on headings and short text blocks (≤6 lines in Chromium, ≤10 in Firefox); `text-wrap: pretty` on body paragraphs and longer text; leave default on code blocks and pre-formatted text
- Font smoothing: apply `-webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale` once on the root layout (macOS only)
- Tabular numbers: use `font-variant-numeric: tabular-nums` for counters, timers, prices, number columns, or any dynamically updating numbers
- Letter-spacing scales with font size: display type needs negative tracking to look engineered rather than stretched. Two tiers: roughly -0.022em for display sizes (32px and above), -0.012em for mid-range (20–28px), normal at 16px and below. Apply to any display-weight typeface, not just geometric sans. Positive letter-spacing on large headlines is always wrong.

### Surfaces
- Concentric border radius: calculate `outerRadius = innerRadius + padding` so nested rounded corners feel intentional, not mechanical; if padding exceeds `24px`, treat layers as separate surfaces and choose each radius independently
- Optical alignment: nudge icons by eye, not just by math, so buttons feel centered; buttons with text and an icon use slightly less padding on the icon side (e.g., `pl-4 pr-3.5`); play triangles and asymmetric icons should shift `1px`-`2px` toward the heavier side, or fix the SVG directly
- Shadows over borders: use layered `box-shadow` for depth on cards, buttons, and elevated elements so the surface feels lifted, not fenced in; reserve actual `border` for dividers, table cells, and layout separation (applies primarily to light mode; on dark surfaces see the dark-mode surface hierarchy rule below)
- Image outlines: add a subtle inset outline so images hold their own depth without altering layout dimensions: `outline: 1px solid rgba(0,0,0,0.1); outline-offset: -1px` (light) or `outline: 1px solid rgba(255,255,255,0.1); outline-offset: -1px` (dark)
- Minimum hit area: keep every interactive target at least 40×40px so even small controls feel generous and precise; extend with a centered pseudo-element when the visible element is smaller, and never let hit areas of two interactive elements overlap
- Light-mode app surface hierarchy: adjacent nested surfaces must be visually distinguishable. Minimum: background-color step of at least 4% lightness between sidebar and main area, and between main area and cards; or a shadow of at least `0 1px 3px rgba(0,0,0,0.10)` on elevated cards. A white card on a near-white background with `box-shadow: 0 1px 2px rgba(0,0,0,0.05)` is invisible -- that is not depth, it is noise.
- Dark-mode surface hierarchy: the page canvas is a near-black solid (e.g. `#08090a`). Elevation is communicated by adding semi-transparent white overlays on top of that canvas: cards at `rgba(255,255,255,0.02)`, elevated surfaces at `0.04`, prominent panels at `0.05`. Borders follow the same logic: `rgba(255,255,255,0.05)` for subtle, `0.08` for standard. Traditional drop shadows (dark on dark) are nearly invisible; luminance stepping through background opacity is the primary depth cue on dark surfaces.
- Border radius system: define a named radius scale during direction lock instead of picking values ad-hoc. A minimal scale is 3–4 tiers (e.g. `{4px, 8px, 12px, pill}`); a richer system might run 6–8 tiers. The point is committing to a named set before the first component so that all surfaces speak the same spatial language — not covering every possible radius value.

## Reflex Fonts to Reject

LLMs default to these because they dominate training data. Using them signals "no decision was made." Pick from foundries with a clear voice instead. The ban is on reflex use as a display face; informed product-UI use (e.g. Inter for a dense data table) is allowed when justified.

Reject: Inter, DM Sans, DM Serif Display, DM Serif Text, Outfit, Plus Jakarta Sans, Instrument Sans, Instrument Serif, Space Grotesk, Space Mono, IBM Plex Sans, IBM Plex Serif, IBM Plex Mono, Syne, Fraunces, Newsreader, Lora, Crimson Pro, Crimson Text, Playfair Display, Cormorant, Cormorant Garamond.

## Font Selection Procedure

1. Write three words that describe the brand (e.g. "precise, minimal, fast").
2. Name the three fonts you would reach for reflexively.
3. Reject all three.
4. Pick a typeface from a named foundry (Klim, Commercial Type, Colophon, Grilli Type, OH no Type, Village, etc.) or an open-source option with a clear personality that matches the brand words. Be able to explain why that specific typeface in one sentence.

## Color System: OKLCH Rules

- Use OKLCH instead of HSL. OKLCH is perceptually uniform: equal numeric changes produce equal perceived changes across the spectrum.
- Reduce chroma as lightness approaches the extremes. At 85% lightness a chroma around 0.08 is enough; pushing to 0.15 looks garish. At 15% lightness, tighten chroma similarly.
- Tint neutrals toward the brand hue with a chroma of 0.005 to 0.01. Even this faint amount is perceptible and creates subconscious cohesion.
- 60-30-10 is about visual weight, not pixel count. 60% neutral/surface, 30% secondary text and borders, 10% accent.
- Never use gray text on a colored background. Use a shade of the background hue at reduced lightness instead.

## Theme Matrix

Choose light or dark deliberately based on audience and context. Neither is a default.

| Context | Direction | Reason |
|---|---|---|
| Trading or analytics dashboard, night-shift use | Dark | High data density; reduced glare during long sessions |
| Children's reading or learning app | Light | Welcoming, low fatigue for eyes still developing contrast sensitivity |
| Enterprise SRE or observability tool | Dark | Operator context; dark surfaces read at a glance in low-light NOC rooms |
| Weekend planning, recipes, journaling | Light | Ambient daytime use; light feels casual and approachable |
| Music player or media browser | Dark | Content-forward; dark surfaces recede and let media pop |
| Hospital or clinical patient portal | Light | Trust and legibility are paramount; clinical associations favor light |
| Vintage or artisanal brand site | Cream/warm light | Dark would clash with the analog material references |

If the answer is not obvious from the context, default to light. If the user's context implies both modes, ship light first and layer dark-mode tokens on top.

## Absolute Bans (CSS-Pattern Level)

These patterns appear in the majority of AI-generated interfaces. Each one has a specific rewrite.

| Pattern | Why | Rewrite |
|---|---|---|
| `border-left` or `border-right` wider than 1px as a section accent | The single most overused "design touch" in admin and dashboard UIs; it looks like a mistake at anything beyond a hairline divider | Change element structure: use a colored dot, a short horizontal rule, a background swatch, or a typographic weight shift instead |
| `background-clip: text` gradient text | Decorative rather than meaningful; one of the top AI design tells; illegible when printed or in high-contrast mode | Use a solid brand color, a tinted neutral, or typographic weight for emphasis |
| `backdrop-filter: blur` glassmorphism as the default card surface | Expensive on low-power devices; overused; the layered-depth illusion breaks with a solid border | Use elevated surfaces via background color steps and `box-shadow` instead |
| Purple-to-blue gradients or cyan-on-dark accent systems | The canonical "AI design" color palette; communicates nothing about the brand | Pick a palette from the brand words via the OKLCH rules above |
| Generic rounded-rect card with `box-shadow` as the default container | Template thinking; applies the same container to every content type regardless of hierarchy | Default to cardless sections; only add card treatment when the content type requires it |
| Modals as a lazy escape for overflow UI | Interrupts flow and breaks browser back navigation; used when an inline expansion, drawer, or separate page would be better | Inline expand, detail panel, or dedicated route; modals only when the action truly requires focus-lock |
| `transition: all` or animating width/height/padding/margin | Forces the browser into layout recalculation on every frame | List exact properties (`transition-property: transform, opacity`); use `grid-template-rows: 0fr to 1fr` for height reveals |

## Motion Specifics

Complements the motion timing in the main SKILL.md constraints.

- No bounce or elastic easing. Real objects decelerate smoothly. Use exponential ease-out (`ease-out-quart`, `ease-out-quint`, or `cubic-bezier(0.16,1,0.3,1)`) for natural, high-quality deceleration.
- Animate `transform` and `opacity` only. Every other property triggers layout or paint.
- For height reveals, use `grid-template-rows: 0fr` to `1fr` transitions instead of animating `height` directly. It avoids the `height: auto` animation trap.
- Icon swaps: use a 120ms cross-fade with `opacity` and a subtle `scale(0.9)` to `scale(1)`. No rotation unless rotation is semantically meaningful (e.g. a chevron indicating direction change).
- Do not use `transition: all` even as a quick prototype shortcut. It animates layout, color, and font-size simultaneously, causing visible jank.

## DESIGN.md Scaffold (Optional, Production UIs)

For a multi-page or production UI, emit a short `DESIGN.md`-style summary before writing the first component. This forces enumeration of decisions that would otherwise be left implicit and lets the user correct direction early. The nine sections:

1. **Visual Theme and Atmosphere** - mood, density, design philosophy in 2-3 sentences
2. **Color Palette and Roles** - semantic name + value + functional role for each color token
3. **Typography Rules** - font family, size scale, weight scale, line-height, letter-spacing; a table if more than 4 levels
4. **Component Stylings** - buttons (all states), cards (if used), inputs, navigation; describe each with states (default, hover, active, disabled)
5. **Layout Principles** - spacing scale, grid columns, whitespace philosophy
6. **Depth and Elevation** - shadow system or background-color-step system; describe each level
7. **Do's and Don'ts** - 5 to 10 guardrails specific to this project, not generic rules
8. **Responsive Behavior** - breakpoints, how navigation collapses, touch target minimums
9. **Agent Prompt Guide** - a quick color reference (name: value pairs) + 3 to 5 example component prompts ready to paste into a follow-up request. Prompts must be specific enough to execute without further lookup: every value, every radius, every letter-spacing, every weight inlined. Example standard (values are illustrative, use the project's own tokens): "Create a hero on `{bg-canvas}`, headline at 48px weight 600, line-height 1.00, letter-spacing -0.022em, color `{text-primary}`, CTA at `{accent}` with `{btn-radius}` radius" — that level of specificity, not "hero with primary color and CTA button"

For a single component or quick prototype, skip this. The three-line thesis in SKILL.md is sufficient.

## AI Slop Test

Would a stranger glancing at the first viewport say "an AI made this" immediately? If yes, the committed direction was not committed enough. The usual culprits: reflex font, default purple accent, centered hero with generic card grid beneath. Fix the typography, the color system, or the layout until the answer flips.

## Content Realism

Placeholder content gives away AI output as quickly as typography does. Treat sample data, copy, and imagery as part of the design, not filler.

**Names and brands**

| Reject | Why | Replace with |
|---|---|---|
| "John Doe", "Jane Doe", "Sarah Chan" | Default dataset — reads as stock | Invent plausible names with specificity: "Priya Venkatesan", "Hiro Okafor", "Maren Lindqvist" |
| "Acme", "Nexus", "SmartFlow", "InnovateX" | Startup-slop naming | Contextual brand names tied to the product's domain (e.g. a lockbox rental SaaS → "Tumbler", not "SmartLock Pro") |
| Generic job titles: "Product Manager" | Too neutral to feel real | Specific roles that imply a real org: "Staff Platform Engineer, Growth", "Regional Lead, APAC" |

**Numbers**

- Ban round or suspiciously perfect metrics: `99.99%`, `100%`, `50%`, `10,000+`.
- Real metrics are messy: `47.2%`, `3,847 teams`, `+1 (312) 847-1928`, `$4.17M ARR`.
- Pick numbers that would make sense on a real dashboard — not numbers that look nice centered in a marketing panel.
- For dynamically updating numerals (counters, timers, prices), use `font-variant-numeric: tabular-nums` so columns don't jitter.

**Copy**

Ban AI-copywriter verbs that signal "LLM wrote this":

> Elevate · Seamless · Unleash · Next-Gen · Empower · Harness · Revolutionize · Transform · Reimagine · Supercharge · Unlock

Replace with concrete, specific verbs tied to what the product actually does. "Cuts deployment time by 40%" beats "Empower your team to ship faster."

**Imagery**

- Do not hotlink Unsplash — links break, images are overused. Use `https://picsum.photos/seed/{stable-seed}/{w}/{h}` for deterministic placeholders that survive reloads.
- Avatars: never the default egg, Lucide user icon, or generic SVG silhouette. Use initials on a tinted neutral background tied to the project palette, or a small inline illustration system.
- Icons: stick to one family at one weight. Mixing Heroicons, Lucide, and Font Awesome shows through as inconsistent line weight.
- No emojis inside UI chrome (buttons, nav, labels). Emojis are acceptable in user-generated content but not in shipped interface text — use an icon family instead.

## Responsive Hazards

Mobile-first sounds obvious until you ship a layout that works on every breakpoint except the one iOS Safari actually renders. Specific traps to avoid:

- **`h-screen` and the collapsing URL bar**: on iOS Safari and Chrome Mobile, the address bar expands and collapses on scroll, so `100vh` jumps by ~80px mid-page. For any full-viewport hero or fullscreen overlay, use `min-h-[100dvh]` (dynamic viewport height) or, for layouts that need the smallest-stable value, `100svh`. Reserve `100lvh` for intentional edge-to-edge immersive states. Do not use `h-screen` for hero sections.
- **Flexbox percentage math**: expressions like `w-[calc(33.333%-1rem)]` are brittle — they drift under `box-sizing`, break when a sibling reflows, and are a pain to debug. Use CSS Grid (`grid grid-cols-1 md:grid-cols-3 gap-6`) for any multi-column structure. Reserve flex for one-dimensional alignment (a row of icons in a header, a button with an icon).
- **Asymmetric layouts and the `<md` fallback**: any non-symmetric grid — masonry, 2-column split, overlap, diagonal flow — must collapse explicitly to a single column below `768px`. Do not rely on the grid "sort of working" on mobile; write the fallback. Pattern: `grid md:grid-cols-[2fr_1fr] gap-8 px-4 md:px-8` with per-item `order-*` overrides for mobile reading flow.
- **Horizontal overflow from large headlines**: display type at 48–72px will blow past a `375px` viewport if you haven't tested it. Use `clamp(32px, 6vw, 72px)` for display sizes instead of fixed breakpoint sizes, or explicitly shrink the headline at `sm:`.
- **Container width**: cap the main column with `max-w-[1400px] mx-auto` (or `max-w-7xl`) on large screens so 27" monitors don't stretch line length past the readable limit (~80ch).
- **Touch hover-stickiness**: on touch devices, a tapped element can stick in the `:hover` state until the next tap elsewhere. Wrap hover styles with `@media (hover: hover)` so they only apply to pointer devices (Tailwind: `[@media(hover:hover)]:hover:*`).
- **`dvh` browser support**: `dvh`/`svh`/`lvh` are well-supported on modern iOS and evergreen browsers, but test on the lowest-version Safari in your target. For a safe fallback, stack `min-height: 100vh; min-height: 100dvh;`.

## Dependency and Stack Verification

Before writing motion or component code that imports a third-party library, confirm the library is actually installed — the single most common AI-design failure in real projects is importing a framework that isn't in `package.json`, then shipping broken code.

- **`package.json` first**: if the code uses `framer-motion`, `lucide-react`, `@phosphor-icons/react`, `zustand`, `@radix-ui/*`, `gsap`, `three`, or any motion/UI library, grep `package.json` before writing the import. If missing, either install it explicitly or write the CSS equivalent instead of importing.
- **Tailwind version lock**: Tailwind v3 and v4 are *not* syntax-compatible. Check the `tailwindcss` version in `package.json` first:
  - v3: classic config in `tailwind.config.js`, `@tailwind base/components/utilities` directives.
  - v4: `@import "tailwindcss"`, `@theme` in CSS, `@tailwindcss/postcss` plugin (not plain `tailwindcss`). Do not put `tailwindcss` directly in `postcss.config.js` on v4.
  - Using v4 syntax in a v3 project silently produces no styles; the page renders as unstyled HTML and the error looks like "nothing is applying."
- **RSC and motion libraries**: in a Next.js App Router project, motion libraries (`framer-motion`, `gsap`) and anything using `useState`/`useEffect`/browser APIs must live inside a Client Component (`'use client'` at the top of the file). Isolate the interactive piece as a small leaf component so the rest of the tree stays server-rendered.
- **Mixing motion systems**: do not mix GSAP and Framer Motion inside the same component tree — their animation clocks fight each other. Default to Framer Motion for UI interactions; reserve GSAP + ScrollTrigger for full-page scroll sequences in isolated wrappers with explicit `useEffect` cleanup.

## Creative Arsenal

When the locked direction calls for something visually distinctive and reflex patterns aren't enough, pull from this list of concrete, implementable concepts. None of these are defaults — use them only when they serve the committed thesis.

**Navigation and entry points**

- Dock magnification (Mac OS style): icons scale fluidly on hover proximity
- Magnetic buttons: CTA pulls slightly toward the cursor using `useMotionValue` and `useTransform` (do not implement with `useState` — it collapses performance on mobile)
- Morphing menus: a pill-shaped primary CTA that expands into its full dialog on click
- Full-screen mega menu reveal: dropdown stagger-fades entire content sections
- Floating speed dial: FAB springs out into a curved arc of secondary actions
- Dynamic-island-style status pill: morphs to show transient alerts and collapses back

**Layout and grids**

- Bento grid: asymmetric tile composition (3-col row + 2-col 70/30 row is a good default)
- Masonry: staggered grid without fixed row heights
- Split-screen scroll: two halves slide in opposite directions on scroll
- Horizontal scroll hijack: vertical scroll translates to horizontal gallery pan (restrict to a bounded section, not the full page)
- Sticky scroll stack: cards pin and physically stack over each other as you scroll past

**Cards and containers**

- Parallax tilt card: 3D transform tracks mouse position (cap at 8° — more feels like a toy)
- Spotlight border: card border illuminates under cursor using a radial gradient masked to the border
- Holographic foil: iridescent hue-shift on hover, keyed to mouse X/Y
- Morphing modal: button physically expands into its dialog container using `layoutId`

**Typography as a visual element**

- Kinetic marquee: infinite text band that reverses or speeds up on scroll
- Text mask reveal: massive type as a transparent window to video or image behind
- Character scramble on load or hover (Matrix-style decoding, used sparingly)
- SVG text on a circular path
- Gradient stroke running along outlined type

**Scroll animation**

- Scroll-linked video or 3D sequence (frame tied to scrollbar position)
- SVG line drawing that reveals itself along a scroll progress path
- Parallax zoom on a background image, keyed to scroll
- Scroll-linked text blur-to-sharp reveal

**Micro-interactions**

- Skeleton shimmer: light sweep across placeholder blocks during loading
- Directional hover fill: fill enters from the exact side the cursor crossed into
- Ripple click effect: visual wave from exact click coordinates
- Particle explosion on button success (sparingly — one CTA per page, not every button)
- Mesh gradient background: organic lava-lamp color blobs (GPU-accelerated, pointer-events: none)

**Implementation notes for the arsenal**

- Any effect that runs continuously (marquees, infinite loops, mesh gradients) must be memoized and isolated in its own component so it does not cause parent re-renders.
- Grain/noise filters go on `fixed inset-0 pointer-events-none z-50` overlays, never inside scrolling content — continuous repaints kill mobile frame rate.
- Magnetic hover, scroll parallax, and any mouse-linked transform must use compositor-friendly properties (`transform`, `opacity`) and read position outside the React render cycle via `useMotionValue`.
- GSAP ScrollTrigger and ThreeJS canvases belong in their own isolated wrapper components with explicit `useEffect` cleanup — leaking scroll listeners or WebGL contexts is the most common production bug.
- Honor `prefers-reduced-motion`: every entry in the arsenal must have a reduced-motion fallback that either disables the effect entirely or reduces it to a simple opacity fade.

## Bento Motion Paradigm (SaaS Dashboards)

When the locked direction is a modern SaaS dashboard or feature-grid section — the "Vercel-core meets Dribbble-clean" territory — the static-card paradigm is not enough. Apply this pattern instead.

**Surface**

- Canvas: off-white (`#f9fafb`, `#fafafa`) in light mode or near-black (`#08090a`) in dark. Not pure white or pure black.
- Cards: pure white (`#ffffff`) in light mode or `rgba(255,255,255,0.02–0.05)` over canvas in dark mode.
- Border: translucent hairline (`border-slate-200/50` or `border-white/5`) — not solid `border-slate-200`.
- Radius: large and consistent (`rounded-[2rem]` to `rounded-[2.5rem]` on outer cards). Apply concentric radius math for nested rounded elements.
- Shadow: diffusion shadow, wide and soft, not the default boxy drop shadow. Example: `shadow-[0_20px_40px_-15px_rgba(0,0,0,0.05)]`. Tint the shadow toward the canvas hue.
- Padding: generous (`p-8` to `p-10` inside cards). Cockpit-dense dashboards are a different paradigm — do not mix them.
- Labels: place card titles and descriptions *outside and below* each tile, not inside. The card becomes a clean visual surface, the labels become a gallery-style caption.

**Motion philosophy**

Every card should feel alive, not static. The phrase "perpetual micro-interaction" captures it: a low-amplitude, continuously running loop that signals the surface is responsive without demanding attention.

- **Spring physics, not linear easing**: `{ type: "spring", stiffness: 100, damping: 20 }` (or the CSS equivalent with `cubic-bezier`). No `ease-out`, no `linear`.
- **Layout transitions**: use Framer Motion's `layout` and `layoutId` for state changes — reordering, resizing, shared-element hand-offs between views. This is the single highest-leverage motion primitive in this paradigm.
- **Staggered reveals**: lists and grids mount with `staggerChildren` — children appear in sequence, not all at once. The parent variants and children must sit in the same client component tree; if data is fetched async, pass it as props into a central motion wrapper.
- **Infinite loops, isolated**: every "alive" card has a micro-loop (pulse, float, shimmer, typewriter cycle, auto-reorder). Each loop lives in its own small Client Component wrapped in `React.memo` so it cannot trigger parent re-renders. A dashboard where every card infinite-loops inside a shared parent will drop frames on mobile.
- **`AnimatePresence` for transient elements**: notifications, tooltips, modals, toasts.

**Archetype cards (pick 3–5 for a dashboard section, not all)**

- **Intelligent list**: vertical stack where items auto-sort over time via `layoutId`, simulating a priority queue or AI ranking
- **Command input**: search or prompt bar with a typewriter cycle through multiple sample prompts, blinking cursor, shimmering processing state
- **Live status**: calendar or schedule surface with "breathing" status dots and notification badges that overshoot on entry and linger briefly
- **Data stream**: horizontal infinite carousel of metric tiles (`x: ["0%", "-100%"]` with seamless looping)
- **Focus mode**: a document preview with a staggered highlight sweep and a floating-toolbar entry on hover

**When not to use this paradigm**

- Editorial or brand-led pages: the bento grid is utility-first and competes with strong editorial typography.
- Cockpit-dense dashboards (trading, observability, SRE): cards with generous padding destroy data density. Use border dividers and `font-mono` for numbers instead.
- Documentation, reading apps, content-forward surfaces: these need a reading column, not a grid of tiles.

---

*Content Realism, Responsive Hazards, Dependency and Stack Verification, Creative Arsenal, and Bento Motion Paradigm are paraphrased and expanded from concepts in [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) (no explicit license at time of merge — ideas and rules used under fair use, no verbatim text copied). Original credit to the taste-skill author for surfacing these specific failure modes and patterns.*

*Rules in Reflex Fonts, Font Selection, OKLCH, Theme Matrix, Absolute Bans, Motion Specifics, and AI Slop Test adapted from [pbakaus/impeccable](https://github.com/pbakaus/impeccable) (Apache 2.0). DESIGN.md Scaffold adapted from [getdesign.md](https://getdesign.md) (MIT); concept credited to Google Stitch.*

*Core skill structure, direction-lock procedure, gotchas table, and Non-Negotiable Constraints extracted from [tw93/waza](https://github.com/tw93/waza) `skills/design` (MIT, © Tw93). See `LICENSE.upstream`.*
