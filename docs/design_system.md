# CopyCat Styling Guide: Premium Wizard Flow Design System

## 🎨 Overview

This document analyzes the **setup-paths page** design system and provides comprehensive guidelines for reproducing the premium "Aurora Glass" wizard flow consistently across all pages in CopyCat.

The setup-paths page exemplifies the ideal user experience: **minimal, focused, premium, and guided**. This design system creates a cohesive, professional interface that users love to interact with.

---

## 🌟 Core Design Principles

### **1. Full-Screen Centered Layout**
The setup wizard uses a **full-screen centered approach** that creates focus and immersion.

```vue
<template>
  <div class="min-h-screen flex items-center justify-center bg-[var(--win-bg-base)] relative overflow-hidden">
    <!-- Animated background -->
    <div class="app-background-lines">
      <!-- 10 animated vertical lines -->
    </div>

    <!-- Main container -->
    <div class="w-full max-w-5xl z-10 animate-fade-in-up">
      <!-- Content -->
    </div>
  </div>
</template>
```

**Key Elements:**
- `min-h-screen`: Full viewport height
- `flex items-center justify-center`: Perfect centering
- `bg-[var(--win-bg-base)]`: Consistent base background
- `app-background-lines`: Animated cyberpunk-style background
- `animate-fade-in-up`: Smooth entry animation

### **2. Progress Steps (Wizard Navigation)**
Visual progress indicators that guide users through multi-step flows.

```vue
<div class="w-full max-w-xl mb-12 flex items-center justify-between relative px-4">
  <!-- Connecting line -->
  <div class="absolute left-4 right-4 top-[20px] h-[1px] bg-white/5 -z-10"></div>

  <!-- Step indicator -->
  <div class="flex flex-col items-center gap-3 z-10">
    <div class="w-10 h-10 rounded-xl flex items-center justify-center border transition-all duration-500 shadow-2xl relative group"
         :class="step >= 1 ? 'border-[var(--win-accent)]/50 bg-[var(--win-accent)]/10 text-[var(--win-accent)] shadow-[0_0_20px_rgba(96,205,255,0.2)]' : 'border-white/5 bg-white/5 text-gray-500'">
      <!-- Active pulse effect -->
      <div v-if="step === 1" class="absolute -inset-1 bg-[var(--win-accent)]/20 blur-sm rounded-xl animate-pulse"></div>
      <UIcon name="i-heroicons-sparkles" class="w-5 h-5 relative z-10" />
    </div>
    <span class="text-[9px] uppercase font-bold tracking-[0.2em]" :class="step === 1 ? 'text-[var(--win-accent)]' : 'text-gray-500'">
      Step Name
    </span>
  </div>
</div>
```

**Key Elements:**
- **Visual states**: Inactive → Active → Completed
- **Color coding**: Gray (inactive) → Cyan accent (active/completed)
- **Animations**: Smooth transitions, pulse effects for current step
- **Typography**: Ultra-small caps with tight letter spacing
- **Icons**: Heroicons with consistent sizing

### **3. Glass Panel System**
The core content container uses the premium glass design system.

```vue
<div class="glass-panel w-full !rounded-[2rem] border-white/5 shadow-[0_32px_64px_-12px_rgba(0,0,0,0.5)] overflow-hidden flex flex-col h-[70vh] backdrop-blur-3xl animate-fade-in">
  <!-- Header section -->
  <div class="px-8 py-10 border-b border-white/5 bg-white/[0.02] flex-shrink-0 relative overflow-hidden">
    <!-- Accent blur blob -->
    <div class="absolute top-0 right-0 w-64 h-64 bg-[var(--win-accent)]/5 blur-[80px] rounded-full -translate-y-1/2 translate-x-1/2"></div>
  </div>

  <!-- Content area -->
  <div class="flex-1 relative overflow-hidden min-h-0">
    <!-- Step content -->
  </div>

  <!-- Footer actions -->
  <div class="p-8 border-t border-white/5 bg-white/[0.02] flex flex-col md:flex-row items-stretch md:items-center justify-between gap-6 flex-shrink-0 relative overflow-hidden">
    <!-- Gradient accent line -->
    <div class="absolute bottom-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-[var(--win-accent)]/20 to-transparent"></div>
  </div>
</div>
```

**Key Elements:**
- **Height constraint**: `h-[70vh]` creates focused content area
- **Border radius**: `!rounded-[2rem]` for premium feel
- **Depth layering**: Header, content, footer with proper borders
- **Accent elements**: Blur blobs and gradient lines
- **Overflow management**: Proper scrolling in content area

---

## 🎭 Typography & Color System

### **Dynamic Gradient Headings**
```vue
<h1 class="text-3xl md:text-4xl font-bold text-white tracking-tight mb-3">
  <span v-if="step === 1" class="bg-gradient-to-r from-blue-200 to-cyan-300 bg-clip-text text-transparent">
    Automatic Enrichment
  </span>
  <span v-else-if="step === 2" class="bg-gradient-to-r from-cyan-200 to-emerald-300 bg-clip-text text-transparent">
    Movies Library
  </span>
</h1>
```

**Key Elements:**
- **Responsive sizing**: `text-3xl md:text-4xl`
- **Gradient text**: Different colors per step for visual interest
- **Tight tracking**: `tracking-tight` for premium appearance

### **Description Text**
```vue
<p class="text-gray-400 text-sm max-w-xl font-light leading-relaxed">
  Step-specific description text here...
</p>
```

**Key Elements:**
- **Muted color**: `text-gray-400` for secondary text
- **Light weight**: `font-light` for readability
- **Relaxed leading**: `leading-relaxed` for comfortable reading

---

## 🎪 Step Content Patterns

### **Centered Content Step**
```vue
<div class="h-full flex flex-col items-center justify-center p-12 text-center">
  <!-- Large icon -->
  <div class="w-24 h-24 rounded-[2rem] bg-gradient-to-br from-white/10 to-white/5 flex items-center justify-center mb-10 border border-white/10 shadow-inner group">
    <UIcon name="i-heroicons-sparkles" class="w-12 h-12 text-[var(--win-accent)] group-hover:scale-110 transition-transform duration-500" />
  </div>

  <!-- Content -->
  <div class="max-w-md w-full space-y-8">
    <!-- Form elements -->
  </div>
</div>
```

### **Full-Width Component Step**
```vue
<FileExplorer
  v-else-if="step === 2 || step === 3"
  :key="`step-${step}`"
  source="16tb"
  :initialPath="initialPath"
  :selectable="true"
  @selection-change="onSelectionChange"
  class="h-full absolute inset-0"
/>
```

---

## 🎨 Form Design System

### **Premium Input Fields**
```vue
<div class="relative group">
  <div class="absolute inset-y-0 left-0 pl-5 flex items-center pointer-events-none">
    <UIcon name="i-heroicons-key" class="w-5 h-5 text-gray-500 group-focus-within:text-[var(--win-accent)] transition-colors" />
  </div>
  <input
    v-model="traktKey"
    type="password"
    placeholder="Paste Trakt Client ID"
    class="w-full bg-white/[0.03] border border-white/10 rounded-2xl py-5 pl-14 pr-4 text-white outline-none focus:border-[var(--win-accent)]/50 focus:bg-white/[0.05] transition-all font-mono text-sm shadow-inner"
  />
</div>
```

**Key Elements:**
- **Icon positioning**: Left-aligned with proper padding
- **Focus states**: Border and background color changes
- **Typography**: `font-mono` for technical inputs
- **Shadow**: `shadow-inner` for depth

### **Validation & Status Text**
```vue
<p class="text-[11px] text-gray-500 uppercase tracking-widest font-bold">
  Required for Posters & Metadata
</p>

<p v-if="error" class="text-[10px] text-red-500 uppercase tracking-widest font-bold animate-pulse">
  Passwords do not match
</p>
```

---

## 🎬 Animation System

### **Entry Animations**
```css
@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in-up {
  animation: fade-in-up 0.6s ease-out;
}

.animate-fade-in {
  animation: fade-in 0.4s ease-out;
}
```

### **Interactive States**
```vue
<button class="min-w-[160px] bg-white text-black hover:bg-white/90 disabled:bg-white/20 disabled:text-black/50 disabled:cursor-not-allowed rounded-2xl py-4 px-6 text-xs font-bold uppercase tracking-widest transition-all shadow-[0_10px_20px_-5px_rgba(255,255,255,0.1)] flex items-center justify-center gap-3 active:scale-95">
  <UIcon v-if="loading" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
  <span>Continue</span>
  <UIcon v-if="!loading" name="i-heroicons-arrow-right" class="w-4 h-4" />
</button>
```

**Key Elements:**
- **Scale feedback**: `active:scale-95`
- **Shadow depth**: Premium button shadows
- **Loading states**: Spinner animation
- **Disabled states**: Proper visual feedback

---

## 🎯 Action Button Patterns

### **Primary CTA (Continue/Complete)**
```vue
<button
  @click="handleNext"
  :disabled="loading || validationError"
  class="min-w-[160px] bg-white text-black hover:bg-white/90 disabled:bg-white/20 disabled:text-black/50 disabled:cursor-not-allowed rounded-2xl py-4 px-6 text-xs font-bold uppercase tracking-widest transition-all shadow-[0_10px_20px_-5px_rgba(255,255,255,0.1)] flex items-center justify-center gap-3 active:scale-95"
>
  <UIcon v-if="loading" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
  <span>{{ step < 4 ? 'Continue' : 'Complete Setup' }}</span>
  <UIcon v-if="!loading" :name="step < 4 ? 'i-heroicons-arrow-right' : 'i-heroicons-check-badge'" class="w-4 h-4" />
</button>
```

### **Secondary Action (Skip)**
```vue
<button
  v-if="step < 4"
  @click="skipStep"
  class="px-6 py-3.5 rounded-2xl text-xs font-bold uppercase tracking-widest text-gray-400 hover:text-white hover:bg-white/5 transition-all"
  :disabled="loading"
>
  {{ step === 1 ? 'Skip' : 'Skip Step' }}
</button>
```

---

## 🎪 Background Animation System

### **Cyberpunk Matrix Lines**
Located in `main.css`, creates the signature animated background:

```css
.app-background-lines {
  position: fixed;
  inset: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: space-evenly;
  pointer-events: none;
  z-index: -10;
  opacity: 0.2;
  padding: 0 40px;
}

.app-background-line {
  position: relative;
  width: 1px;
  height: 100%;
  background: rgba(255, 255, 255, 0.02);
  overflow: hidden;
}

.app-background-line::after {
  content: '';
  display: block;
  position: absolute;
  height: 15vh;
  width: 100%;
  top: -50%;
  left: 0;
  background: linear-gradient(to bottom,
    rgba(96, 205, 255, 0) 0%,
    rgba(96, 205, 255, 0.8) 75%,
    #60cdff 100%);
  animation: setup-drop 7s infinite cubic-bezier(0.4, 0.26, 0, 0.97);
}
```

**Key Elements:**
- **10 vertical lines** evenly spaced
- **Staggered animations** with different delays/durations
- **Cyan accent color** flowing down each line
- **Subtle opacity** (0.2) for background presence

---

## 📐 Layout Grid & Spacing

### **Container Widths**
- **Wizard container**: `max-w-5xl` (80rem)
- **Progress bar**: `max-w-xl` (36rem)
- **Content sections**: `max-w-md` (28rem)

### **Spacing Scale**
- **Section gaps**: `space-y-8`, `space-y-10`
- **Element gaps**: `gap-3`, `gap-6`
- **Padding**: `p-12`, `px-8 py-10`
- **Margins**: `mb-12`, `mb-10`

### **Responsive Breakpoints**
- **Mobile-first**: Default styles for mobile
- **Tablet+**: `md:` prefixes for medium screens and up
- **Flex layouts**: `flex-col md:flex-row`

---

## 🎨 Glass Design System Levels

### **CSS Variables (main.css)**
```css
:root {
  /* Level 1: Sidebar / Heavy Acrylic */
  --glass-level-1-bg: rgba(20, 20, 20, 0.6);
  --glass-level-1-blur: 40px;
  --glass-level-1-border: rgba(255, 255, 255, 0.05);

  /* Level 2: Cards / Content Glass (Default) */
  --glass-level-2-bg: rgba(30, 30, 30, 0.65);
  --glass-level-2-blur: 25px;
  --glass-level-2-border: rgba(255, 255, 255, 0.08);

  /* Level 3: Overlays / Modals */
  --glass-level-3-bg: rgba(40, 40, 40, 0.75);
  --glass-level-3-blur: 50px;
  --glass-level-3-border: rgba(255, 255, 255, 0.12);
}
```

### **Glass Panel Classes**
```css
.glass-panel {
  background: var(--glass-level-2-bg);
  backdrop-filter: blur(var(--glass-level-2-blur)) saturate(120%);
  border: 1px solid var(--glass-level-2-border);
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
  transition: all 0.3s var(--ease-spring);
  position: relative;
  overflow: hidden;
}
```

---

## 🚀 Implementation Checklist

### **For New Wizard Pages:**
- [ ] Use full-screen centered layout with animated background
- [ ] Implement progress steps with visual indicators
- [ ] Apply glass panel system with proper depth
- [ ] Use gradient text for headings
- [ ] Implement smooth animations and transitions
- [ ] Follow typography and spacing guidelines
- [ ] Include proper loading and disabled states
- [ ] Test responsive behavior on mobile/tablet

### **Reusable Components to Create:**
- [ ] `WizardProgress.vue` - Progress step indicator
- [ ] `WizardStep.vue` - Individual step content wrapper
- [ ] `GlassCard.vue` - Premium glass panel component
- [ ] `AnimatedBackground.vue` - Cyberpunk background lines

---

## 🎯 Best Practices

1. **Consistency**: Always use the established color palette and spacing
2. **Performance**: Use CSS transforms instead of layout properties for animations
3. **Accessibility**: Ensure proper focus states and keyboard navigation
4. **Mobile-first**: Design for mobile, enhance for larger screens
5. **Progressive enhancement**: Core functionality works without JavaScript
6. **Loading states**: Always provide visual feedback for async operations

---

## 📋 Migration Guide for Existing Pages

### **Current Library Page Issues:**
- ❌ No animated background
- ❌ Inconsistent glass panel usage
- ❌ Different spacing patterns
- ❌ Missing premium typography

### **Migration Steps:**
1. Add animated background to page container
2. Wrap content in proper glass panels
3. Update typography to match premium system
4. Implement consistent spacing using established scale
5. Add smooth animations and transitions
6. Update button styles to match premium design

This design system creates the **premium, focused, wizard-like experience** that users expect from modern applications. Implement it consistently across all pages to maintain the high-quality user experience established in the setup flow.
