<template>
  <div class="flex flex-col gap-6">
    <!-- Main Navigation -->
    <div class="p-1.5 bg-[var(--glass-level-2-bg)] rounded-xl border border-white/10 flex gap-1">
      <button 
        v-for="type in types" 
        :key="type.value"
        @click="$emit('update:type', type.value)"
        class="flex-1 py-2.5 px-4 rounded-lg text-sm font-bold transition-all duration-300 flex items-center justify-center gap-2"
        :class="currentType === type.value 
          ? 'bg-[var(--brand-1)] text-[var(--win-bg-base)] shadow-[0_0_15px_rgba(96,205,255,0.3)]' 
          : 'text-[var(--win-text-muted)] hover:text-[var(--win-text-primary)] hover:bg-[var(--glass-level-1-bg)]'"
      >
        <UIcon :name="type.icon" class="w-4 h-4" />
        {{ type.label }}
      </button>
    </div>

    <!-- Filters Section -->
    <div class="space-y-4">
      <h3 class="text-xs font-bold text-[var(--win-text-muted)] uppercase tracking-widest px-1">Sort & Filter</h3>
      
      <!-- Sort By -->
      <div class="space-y-2">
        <label class="text-xs font-semibold text-[var(--win-text-muted)] px-1">Sort By</label>
        <div class="relative group">
           <select 
             :value="currentSort"
             @input="$emit('update:sort', ($event.target as HTMLSelectElement).value)"
             class="w-full appearance-none bg-[var(--glass-level-1-bg)] border border-white/10 rounded-xl px-4 py-3 text-sm text-[var(--win-text-primary)] outline-none focus:border-[var(--brand-1)]/50 transition-colors cursor-pointer"
           >
             <option value="created_at">Date Added</option>
             <option value="title">Title</option>
             <option value="year">Release Year</option>
             <option value="rating">Rating</option>
           </select>
           <UIcon name="i-heroicons-chevron-down" class="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--win-text-muted)] pointer-events-none" />
        </div>
      </div>

      <!-- Order -->
      <div class="grid grid-cols-2 gap-2">
         <button 
           @click="$emit('update:order', 'asc')"
           class="py-2.5 rounded-lg border text-xs font-bold transition-all flex items-center justify-center gap-2"
           :class="currentOrder === 'asc' 
             ? 'bg-[var(--brand-1)]/10 border-[var(--brand-1)] text-[var(--brand-1)]' 
             : 'bg-transparent border-white/5 text-[var(--win-text-muted)] hover:border-white/10 hover:text-[var(--win-text-secondary)]'"
         >
           <UIcon name="i-heroicons-bars-arrow-up" class="w-4 h-4" />
           Ascending
         </button>
         <button 
           @click="$emit('update:order', 'desc')"
           class="py-2.5 rounded-lg border text-xs font-bold transition-all flex items-center justify-center gap-2"
           :class="currentOrder === 'desc' 
             ? 'bg-[var(--brand-1)]/10 border-[var(--brand-1)] text-[var(--brand-1)]' 
             : 'bg-transparent border-white/5 text-[var(--win-text-muted)] hover:border-white/10 hover:text-[var(--win-text-secondary)]'"
         >
           <UIcon name="i-heroicons-bars-arrow-down" class="w-4 h-4" />
           Descending
         </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  currentType: string
  currentSort: string
  currentOrder: string
}>()

const emit = defineEmits(['update:type', 'update:sort', 'update:order'])

const types = [
  { label: 'Movies', value: 'movie', icon: 'i-heroicons-film' },
  { label: 'TV Shows', value: 'tv', icon: 'i-heroicons-tv' }
]
</script>
