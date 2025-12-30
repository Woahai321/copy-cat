# 🎨 UI/UX Theme Blueprint: "Aurora Glass"
> **Version:** 2.0 (Investor Ready)
> **Framework:** Nuxt 3 + Tailwind CSS
> **Theme:** Dark Mode Only / Windows 11 Inspired / Glassmorphism

## 1. Design Philosophy
The "Aurora Glass" design system aims for a **high-premium, cinematic aesthetic**. It moves away from flat "admin panel" looks to an immersive, depth-driven interface.

### Core Pillars
*   **Depth & Layering:** No flat colored backgrounds. Everything floats on "Glass" layers (`backdrop-filter: blur`).
*   **Alive Backgrounds:** A subtle, animated "Aurora" gradient mesh provides a premium "living" backdrop, replacing harsh noise textures.
*   **Neon & Glow:** Critical actions and active states use **inner glows** and **gradient text**, not just solid fills.
*   **Micro-Interactions:** Buttons shine on hover, modals fade/zoom in, and lists have hover lifts.

---

## 2. Technical Stack
*   **Frontend:** Nuxt 3 (Vue 3 Composition API)
*   **Styling:** Vanilla CSS Variables (Theming) + Tailwind CSS (Utility)
*   **Icons:** Nuxt UI / Heroicons
*   **Motion:** CSS Keyframes & Transitions

---

## 3. CSS Token System (`main.css`)
We use global CSS variables to control the theme. Do not hardcode hex values in components.

### 🌑 Colors
| Variable | Value | Usage |
| :--- | :--- | :--- |
| `--win-bg-base` | `#0f0f0f` | Extreme deep background (behind Aurora) |
| `--win-text-primary` | `#ffffff` | Headings, primary content |
| `--win-text-secondary` | `#a0a0a0` | Subtitles, metadata |
| `--win-accent` | `#60cdff` | Primary Brand Color (Cyan/Blue) |

### 💎 Glassmorphism (The "Secret Sauce")
The core look is defined by these surface variables.
```css
:root {
  /* Semi-transparent dark layer */
  --glass-surface: rgba(30, 30, 30, 0.75); 
  
  /* Lighter on hover */
  --glass-surface-hover: rgba(45, 45, 45, 0.85); 
  
  /* The "Frost" effect */
  --glass-blur: 20px;
  
  /* Subtle white border for definition */
  --glass-border: rgba(255, 255, 255, 0.08); 
}
```

---

## 4. Reusable Components & Classes

### A. The Glass Panel (`.glass-panel`)
**Usage:** Replaces all "cards", widgets, and modals.
**Technique:**
*   `backdrop-filter: blur(20px)` ensures content behind it is frosted.
*   `box-shadow` adds depth and separation from the background.
*   `border` is 1px transparent white to act as a "light catcher".

```html
<div class="glass-panel p-6">
  <!-- Content here -->
</div>
```

### B. Gradient Text (`.text-gradient-accent`)
**Usage:** For high-impact numbers (Stats) or Hero titles.
**Technique:** `background-clip: text` with `color: transparent`.

```html
<h1 class="text-4xl font-bold text-gradient-accent">
  {{ activeJobCount }}
</h1>
```

### C. Buttons
*   **Primary (`.btn-primary`):** Gradient background + Shadow Glow.
*   **Secondary:** Glass background + Border.

---

## 5. Layout & Chrome (`default.vue`)

### The "Mica" Background
We inject a fixed `::before` element on `<body>` that holds the Aurora gradient animation. This ensures content scrolls *over* the background, giving a parallax-like feeling of depth.

```css
body::before {
  content: "";
  position: fixed;
  inset: 0;
  z-index: -1;
  background: radial-gradient(...);
  filter: blur(60px);
  animation: auroraMove 20s infinite;
}
```

### The Acrylic Sidebar
The sidebar is **not** solid. It uses a heavy resize of the Glass effect (`rgba(32,32,32, 0.7)` + `blur(40px)`) to mimic Windows 11's "Acrylic" material.

---

## 6. Development Guidelines
1.  **Never use solid backgrounds** for containers. Use `.glass-panel`.
2.  **Use `UIcon`** for all iconography (Heroicons via Nuxt UI).
3.  **Spacing:** Give content "breathing room". Use `gap-4` or `gap-6`, not `gap-2` for main layouts.
4.  **Z-Index:**
    *   `-1`: Background Aurora
    *   `0`: Page Content
    *   `40`: Sidebar
    *   `50`: Modals / Overlays
    *   `100`: Toast Notifications

## 7. Folder Structure
*   `assets/css/main.css`: **The Source of Truth** for all variables and global styles.
*   `layouts/default.vue`: Controls the App Shell (Sidebar + Background).
*   `components/`: Reusable Vue components (mostly using those CSS classes).
