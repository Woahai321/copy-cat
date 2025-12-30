<template>
  <div 
    class="group relative aspect-[2/3] bg-black/40 rounded-xl overflow-hidden cursor-pointer transition-all duration-300 hover:scale-[1.02] hover:shadow-[0_0_30px_rgba(0,0,0,0.5)] border border-white/5 hover:border-[var(--brand-1)]"
    :class="{ 'ring-2 ring-[var(--brand-1)] shadow-[0_0_20px_rgba(96,205,255,0.3)]': selected }"
  >
      <!-- Selection Overlay (Mobile or Selection Mode) -->
      <div 
         v-if="selectionMode"
         class="absolute inset-0 z-30 bg-black/20 backdrop-blur-[1px] flex items-start justify-end p-2"
      >
         <div 
           class="w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all bg-black/50"
           :class="selected ? 'border-[var(--brand-1)] bg-[var(--brand-1)]' : 'border-white/50'"
         >
             <UIcon v-if="selected" name="i-heroicons-check" class="w-4 h-4 text-black" />
         </div>
      </div>

      <!-- Poster -->
      <img 
        v-if="item.poster_url"
        :src="item.poster_url.startsWith('http') ? item.poster_url : `${apiBase}${item.poster_url}`"
        class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
        loading="lazy" 
      />
      <div v-else class="w-full h-full flex flex-col items-center justify-center bg-white/5 p-4 text-center">
         <UIcon :name="item.media_type === 'movie' ? 'i-heroicons-film' : 'i-heroicons-tv'" class="w-12 h-12 text-gray-700 mb-2" />
         <span class="text-xs text-gray-500 font-bold line-clamp-2">{{ item.title }}</span>
      </div>

      <!-- Hover Overlay -->
      <div class="absolute inset-0 bg-gradient-to-t from-black via-black/40 to-transparent opacity-0 group-hover:opacity-100 transition-all duration-300 flex flex-col justify-end p-4">
          
          <!-- Rating Badge -->
          <div class="absolute top-3 left-3 flex gap-2">
             <span v-if="item.rating" class="px-2 py-1 bg-black/60 backdrop-blur-md rounded-lg text-[10px] font-bold text-[var(--brand-1)] flex items-center gap-1 border border-white/10">
                <UIcon name="i-heroicons-star" class="w-3 h-3" />
                {{ parseFloat(item.rating).toFixed(1) }}
             </span>
             <span v-if="item.year" class="px-2 py-1 bg-black/60 backdrop-blur-md rounded-lg text-[10px] font-bold text-white border border-white/10">
                {{ item.year }}
             </span>
          </div>

          <div class="translate-y-4 group-hover:translate-y-0 transition-transform duration-300">
             <h3 class="text-sm font-bold text-white leading-tight line-clamp-2 mb-1">{{ item.title }}</h3>
             
             <div class="flex items-center gap-2 mt-3">
                 <!-- Primary Action (Copy) -->
                 <button 
                   @click.stop="$emit('copy', item)"
                   class="flex-1 py-2 bg-[var(--brand-1)] hover:bg-[var(--brand-2)] text-black text-[10px] font-bold rounded-lg flex items-center justify-center gap-1.5 transition-colors shadow-lg shadow-[var(--brand-1)]/20"
                 >
                    <UIcon name="i-heroicons-document-duplicate" class="w-3 h-3" />
                    Copy
                 </button>
             </div>
          </div>
      </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  item: any
  selected?: boolean
  selectionMode?: boolean
  apiBase?: string
}>()

const emit = defineEmits(['copy'])
const config = useRuntimeConfig()
const apiBase = props.apiBase || config.public.apiBase
</script>
