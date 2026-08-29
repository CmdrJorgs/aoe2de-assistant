---
name: Imperial Scribe
colors:
  surface: '#fff8ef'
  surface-dim: '#e3d9c1'
  surface-bright: '#fff8ef'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#fdf3da'
  surface-container: '#f7edd4'
  surface-container-high: '#f1e8cf'
  surface-container-highest: '#ece2c9'
  on-surface: '#201b0c'
  on-surface-variant: '#4e4638'
  inverse-surface: '#35301f'
  inverse-on-surface: '#faf0d7'
  outline: '#807666'
  outline-variant: '#d2c5b2'
  surface-tint: '#7a5909'
  primary: '#7a5909'
  on-primary: '#ffffff'
  primary-container: '#cda351'
  on-primary-container: '#523a00'
  inverse-primary: '#edc06b'
  secondary: '#aa3527'
  on-secondary: '#ffffff'
  secondary-container: '#fe725f'
  on-secondary-container: '#6f0703'
  tertiary: '#4b6633'
  on-tertiary: '#ffffff'
  tertiary-container: '#95b378'
  on-tertiary-container: '#2c4516'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdea5'
  primary-fixed-dim: '#edc06b'
  on-primary-fixed: '#271900'
  on-primary-fixed-variant: '#5d4200'
  secondary-fixed: '#ffdad4'
  secondary-fixed-dim: '#ffb4a8'
  on-secondary-fixed: '#410000'
  on-secondary-fixed-variant: '#891d12'
  tertiary-fixed: '#cdedac'
  tertiary-fixed-dim: '#b1d092'
  on-tertiary-fixed: '#0d2000'
  on-tertiary-fixed-variant: '#344e1d'
  background: '#fff8ef'
  on-background: '#201b0c'
  surface-variant: '#ece2c9'
  parchment-deep: '#E7D8B1'
  charcoal-ink: '#181C29'
  gold-leaf: '#B8862D'
  blood-accent: '#8B0000'
  map-forest: '#526D39'
typography:
  display-lg:
    fontFamily: Source Serif 4
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Source Serif 4
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
  headline-md:
    fontFamily: Source Serif 4
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Noto Sans
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Noto Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-tactical:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.05em
  headline-lg-mobile:
    fontFamily: Source Serif 4
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 8px
  gutter: 24px
  margin-desktop: 64px
  margin-mobile: 16px
  container-max: 1280px
---

## Brand & Style

The design system is built for the "AoE2 Coach AI," evoking the atmosphere of a royal tactician’s war room. It bridges the gap between historical manuscript aesthetics and high-performance tactical software. The brand personality is authoritative, weathered, and strategic.

The design style is **Tactile / Skeuomorphic Modernism**. It utilizes the organic textures of aged papyrus and heavy parchment as the canvas for precise, high-fidelity UI components. Drawing inspiration from Age of Empires II: DE, the system incorporates decorative gold filigree and "illuminated" interactive states, while maintaining a clean, systematic layout that ensures complex RTS data remains digestible during high-pressure gameplay.

## Colors

The palette is anchored by **Parchment (#F2E8CF)**, serving as the primary surface color to mimic aged paper. **Charcoal Ink (#181C29)** provides the high-contrast necessary for legibility, used for primary text and deep "sunken" UI containers.

**Primary Gold (#CDA351)** is reserved for interactive elements, borders, and significant tactical highlights, mimicking the gold leafing found in medieval manuscripts. **Blood Red (#660000)** is used sparingly for critical alerts, aggressive AI states, or "loss" indicators, while **Forest Green (#526D39)** serves as a secondary accent for "growth" metrics like villager production or resource surpluses.

## Typography

This design system employs a dual-purpose typographic scale. **Source Serif 4** provides the authoritative, "monumental" feel of a medieval scribe for headers and titles, featuring high readability even with its classic proportions.

For tactical data, build orders, and resource counts, **Noto Sans** offers a clean, neutral counterpoint that ensures speed of reading. **JetBrains Mono** is introduced for "Tactical Labels"—specific numbers like APM, EPM, or unit counts—to provide a precise, technical feel that differentiates raw data from strategic advice.

## Layout & Spacing

The layout follows a **Fixed Grid** model on desktop to preserve the "manuscript" composition, centering content within a 1280px parchment container. The spacing rhythm is based on an 8px base unit, ensuring consistent alignment of tactical widgets.

- **Desktop (1200px+):** 12-column grid, 24px gutters, generous 64px margins. Use "illuminated" margins for decorative scroll motifs.
- **Tablet (768px - 1199px):** 8-column grid, 16px gutters, 32px margins. Tactical widgets stack vertically.
- **Mobile (Below 768px):** 4-column grid, 12px gutters, 16px margins. The papyrus background texture should be simplified or fixed to prevent visual noise during scrolling.

## Elevation & Depth

Hierarchy is achieved through **Tonal Layers** and **Physical Metaphor** rather than standard drop shadows.

1.  **The Scroll (Base):** The primary background uses a subtle papyrus texture.
2.  **Inset Panels (Level 1):** Subtle inner shadows and darker parchment tones (#E7D8B1) create the effect of windows or "carved" sections within the paper.
3.  **Raised Vellum (Level 2):** Elevated cards use a slightly lighter parchment tone with a "deckle edge" (torn paper) border effect and very soft, amber-tinted ambient shadows.
4.  **The Quill (Interactions):** Active states use "Gold Leaf" borders (1px solid #B8862D) that appear to glow, signifying high importance.

## Shapes

The shape language is primarily **Soft (0.25rem)**, reflecting the organic nature of hand-cut parchment. 

Strictly avoid perfect circles or highly rounded "pill" shapes, as they feel too modern and "plastic." Instead, use slight corner radii for buttons and containers to mimic the natural wear of heavy paper. Large decorative elements like Build Order cards may use a "clipped corner" or "ornamental notch" aesthetic to reinforce the medieval theme.

## Components

### Buttons
Primary buttons are styled with a deep charcoal background and gold-leaf borders. The text is Noto Sans Bold, Uppercase. On hover, the gold border expands slightly, and the background transitions to a rich blood red (#660000).

### Cards & Tactical Widgets
Cards should feature a 1px border in a darker parchment shade (#D4C5A1). Headers within cards should be separated by a decorative "horizontal rule"—a thin line with a diamond or fleur-de-lis motif in the center.

### Input Fields
Fields appear as "sunken" parchment. The focus state replaces the soft inner shadow with a crisp Primary Gold outline. Use JetBrains Mono for input text to maintain the "scribe writing data" feel.

### Chips & Tags
Used for unit types (Cavalry, Archer, Siege). These use a low-saturation version of the secondary colors (e.g., a muted Slate for Infantry) with sharp 2px borders.

### Progress Bars (Research & Production)
Progress bars should look like an "ink fill." The empty state is a faint charcoal outline; the filled state is Primary Gold, featuring a slight texture to make it look like hand-painted gold leaf.

### Modals
Modals should cover the screen with a semi-transparent Charcoal Ink backdrop. The modal container itself is a "Heavy Scroll," featuring vertical wooden bar textures at the top and bottom.
