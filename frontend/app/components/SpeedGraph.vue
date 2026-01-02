<template>
  <div class="glass-panel p-4">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-sm font-semibold text-[var(--win-text-secondary)] flex items-center gap-2">
        <UIcon name="i-heroicons-chart-bar" class="w-4 h-4 text-[var(--win-accent)]" />
        Transfer Speed
      </h3>
      <div class="bg-[var(--glass-level-1-bg)] px-2 py-0.5 rounded text-xs font-mono text-[var(--win-accent)] border border-white/5 shadow-[0_0_10px_rgba(96,205,255,0.2)]">
        {{ currentSpeedFormatted }}/s
      </div>
    </div>
    
    <!-- Chart Container -->
    <div class="relative h-32 w-full overflow-hidden rounded-lg bg-[var(--glass-level-1-bg)] border border-white/5">
       <!-- Grid Lines -->
       <div class="absolute inset-0 flex flex-col justify-between pointer-events-none opacity-10">
          <div class="border-t border-white w-full h-0"></div>
          <div class="border-t border-white w-full h-0"></div>
          <div class="border-t border-white w-full h-0"></div>
       </div>

       <svg class="w-full h-full" preserveAspectRatio="none">
          <!-- Gradient Definition -->
          <defs>
            <linearGradient id="speedGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="var(--brand-1)" stop-opacity="0.5"/>
              <stop offset="100%" stop-color="var(--brand-1)" stop-opacity="0"/>
            </linearGradient>
          </defs>

          <!-- Area Path -->
          <path 
            :d="areaPath" 
            fill="url(#speedGradient)" 
            class="transition-[d] duration-300 ease-linear"
          />
          
          <!-- Line Path -->
          <path 
             :d="linePath" 
             fill="none" 
             stroke="var(--brand-1)" 
             stroke-width="2" 
             class="transition-[d] duration-300 ease-linear"
          />
       </svg>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
    history: number[] // Array of speed values (bytes/sec)
}>()

const maxPoints = 50

// Computed Max for scaling
const maxSpeed = computed(() => {
    const max = Math.max(...props.history, 1024 * 1024) // Min 1MB scale
    return max * 1.1 // 10% headroom
})

const currentSpeedFormatted = computed(() => {
    const current = props.history[props.history.length - 1] || 0
    return formatSize(current)
})

const points = computed(() => {
    // Fill width with available data (no padding)
    const data = [...props.history]
    if (data.length === 0) return []
    
    // If only one point, duplicate it to make a line
    if (data.length === 1) data.push(data[0]) 
    
    const maxX = data.length - 1
    
    return data.map((val, index) => {
        const x = (index / maxX) * 100
        const y = 100 - ((val / maxSpeed.value) * 100)
        return `${x},${y}`
    })
})

const linePath = computed(() => {
    return `M ${points.value.join(' L ')}`
})

const areaPath = computed(() => {
    return `M ${points.value.join(' L ')} L 100,100 L 0,100 Z`
})

const formatSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
}
</script>
