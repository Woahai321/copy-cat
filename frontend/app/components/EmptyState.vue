<template>
  <div class="empty-state text-center py-12 px-6">
    <div class="mb-6">
      <slot name="illustration">
        <!-- Queue illustration -->
        <svg
          v-if="variant === 'queue'"
          class="w-32 h-32 mx-auto"
          viewBox="0 0 200 200"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <rect x="40" y="50" width="120" height="30" rx="8" class="fill-[var(--brand-1)]/20 stroke-[var(--brand-5)]/40" stroke-width="3"/>
          <circle cx="70" cy="65" r="8" class="fill-[var(--brand-5)]/60"/>
          <rect x="90" y="60" width="60" height="10" rx="3" class="fill-slate-600/60"/>
          <rect x="40" y="95" width="120" height="30" rx="8" class="fill-[var(--brand-1)]/10 stroke-[var(--brand-5)]/30" stroke-width="3"/>
          <circle cx="70" cy="110" r="8" class="fill-[var(--brand-5)]/40"/>
          <rect x="90" y="105" width="60" height="10" rx="3" class="fill-slate-600/40"/>
          <rect x="40" y="140" width="120" height="30" rx="8" class="fill-[var(--brand-1)]/5 stroke-[var(--brand-5)]/20" stroke-width="3"/>
          <circle cx="70" cy="155" r="8" class="fill-[var(--brand-5)]/20"/>
          <rect x="90" y="150" width="60" height="10" rx="3" class="fill-slate-600/20"/>
        </svg>
        
        <!-- History illustration -->
        <svg
          v-else-if="variant === 'history'"
          class="w-32 h-32 mx-auto"
          viewBox="0 0 200 200"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <circle cx="100" cy="100" r="60" class="stroke-[var(--brand-5)]/40" stroke-width="6"/>
          <path d="M100 50 L100 100 L130 120" class="stroke-[var(--brand-5)]/60" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
          <circle cx="100" cy="50" r="6" class="fill-[var(--brand-5)]/60"/>
          <circle cx="150" cy="100" r="6" class="fill-[var(--brand-5)]/40"/>
          <circle cx="100" cy="150" r="6" class="fill-[var(--brand-5)]/40"/>
          <circle cx="50" cy="100" r="6" class="fill-[var(--brand-5)]/40"/>
          <path d="M90 35 Q100 25 110 35" class="stroke-[var(--brand-5)]/60" stroke-width="5" fill="none" stroke-linecap="round"/>
        </svg>
        
        <!-- Folder illustration -->
        <svg
          v-else-if="variant === 'folder'"
          class="w-32 h-32 mx-auto"
          viewBox="0 0 200 200"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path d="M30 70 L30 160 Q30 170 40 170 L160 170 Q170 170 170 160 L170 80 Q170 70 160 70 L105 70 L95 55 Q92 50 85 50 L40 50 Q30 50 30 60 Z" class="fill-[var(--brand-1)]/10 stroke-[var(--brand-5)]/40" stroke-width="4"/>
          <path d="M30 80 L170 80" class="stroke-[var(--brand-5)]/30" stroke-width="3"/>
          <rect x="60" y="100" width="80" height="8" rx="2" class="fill-slate-600/40"/>
          <rect x="60" y="120" width="60" height="8" rx="2" class="fill-slate-600/30"/>
          <rect x="60" y="140" width="50" height="8" rx="2" class="fill-slate-600/20"/>
        </svg>
        
        <!-- Search/No results illustration -->
        <svg
          v-else-if="variant === 'search'"
          class="w-32 h-32 mx-auto"
          viewBox="0 0 200 200"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <circle cx="80" cy="80" r="40" class="stroke-[var(--brand-5)]/40" stroke-width="6"/>
          <line x1="110" y1="110" x2="140" y2="140" class="stroke-[var(--brand-5)]/60" stroke-width="8" stroke-linecap="round"/>
          <path d="M55 75 L70 90 L95 65" class="stroke-slate-600/40" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
        </svg>
        
        <!-- Activity/Idle illustration -->
        <svg
          v-else-if="variant === 'activity'"
          class="w-32 h-32 mx-auto"
          viewBox="0 0 200 200"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <circle cx="100" cy="100" r="50" class="fill-[var(--brand-1)]/10 stroke-[var(--brand-5)]/30" stroke-width="4"/>
          <path d="M30 100 L60 100 L70 70 L85 130 L100 80 L115 120 L130 100 L170 100" class="stroke-[var(--brand-5)]/50" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
          <circle cx="100" cy="80" r="6" class="fill-[var(--brand-5)]/60"/>
        </svg>
        
        <!-- Default illustration -->
        <svg
          v-else
          class="w-32 h-32 mx-auto"
          viewBox="0 0 200 200"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <circle cx="100" cy="100" r="60" class="stroke-[var(--brand-5)]/30" stroke-width="6" stroke-dasharray="15 15"/>
          <path d="M100 70 L100 130 M70 100 L130 100" class="stroke-slate-600/40" stroke-width="6" stroke-linecap="round"/>
        </svg>
      </slot>
    </div>
    
    <h3 class="text-xl font-bold text-[var(--win-text-primary)] mb-3">
      {{ title }}
    </h3>
    
    <p class="text-sm text-[var(--win-text-muted)] mb-6 max-w-md mx-auto leading-relaxed">
      {{ description }}
    </p>
    
    <slot name="action"></slot>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title: string
  description: string
  variant?: 'queue' | 'history' | 'folder' | 'search' | 'activity' | 'default'
}

withDefaults(defineProps<Props>(), {
  variant: 'default'
})
</script>

<style scoped>
/* Empty state styles are in main.css */
</style>

