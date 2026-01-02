<template>
  <div class="glass-panel p-0 overflow-hidden h-full relative border border-white/5 rounded-lg md:rounded-xl">
      <!-- Full Size Poster Shimmer -->
      <div class="absolute inset-0 bg-[var(--glass-level-1-bg)] shimmer-bg"></div>
      
      <!-- Bottom Metadata Simulation -->
      <div class="absolute bottom-0 left-0 right-0 p-3 space-y-2 bg-gradient-to-t from-[var(--win-bg-base)]/80 to-transparent">
          <div class="h-4 w-3/4 bg-[var(--glass-level-2-bg)] rounded-sm shimmer-bg"></div>
          <div class="flex gap-2">
              <div class="h-3 w-10 bg-[var(--glass-level-1-bg)] rounded-sm shimmer-bg"></div>
              <div class="h-3 w-8 bg-[var(--glass-level-1-bg)] rounded-sm shimmer-bg"></div>
          </div>
      </div>
  </div>
</template>
