<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-end md:items-center justify-center md:p-4 bg-[var(--glass-level-4-bg)] backdrop-blur-md animate-in fade-in duration-200" @click.self="$emit('close')">
      <!-- Modal Container -->
      <div class="bg-[var(--win-bg-base)] md:bg-[var(--glass-level-3-bg)] md:backdrop-blur-xl w-full max-w-4xl h-[100dvh] md:h-auto md:rounded-2xl md:overflow-hidden shadow-[0_0_50px_rgba(0,0,0,0.8)] border-x md:border border-white/10 flex flex-col md:flex-row md:max-h-[85vh] relative">
          
          <!-- Close Button (Mobile Floating) -->
          <button @click="$emit('close')" class="absolute top-4 right-4 z-30 md:hidden w-10 h-10 bg-black/50 backdrop-blur-md rounded-full flex items-center justify-center text-white border border-white/10 shadow-lg active:scale-95 transition-transform">
              <UIcon name="i-heroicons-x-mark" class="w-6 h-6" />
          </button>

          <!-- Poster Side -->
          <div class="w-full md:w-1/3 aspect-[2/3] md:aspect-auto md:h-auto relative group shrink-0">
              <!-- Mobile Gradient Overlay for Text Readability -->
              <div class="absolute inset-0 bg-gradient-to-t from-[var(--win-bg-base)] via-transparent to-transparent z-10 md:hidden"></div>
              
              <img 
                 v-if="posterUrl" 
                 :src="posterUrl.startsWith('http') ? posterUrl : `${apiBase}${posterUrl}`" 
                 class="w-full h-full object-cover bg-black/50 object-top"
              />
              <div v-else class="w-full h-full bg-white/5 flex items-center justify-center flex-col gap-4">
                  <UIcon :name="isMovie ? 'i-heroicons-film' : 'i-heroicons-tv'" class="w-16 h-16 text-gray-700" />
                  <span class="text-xs text-[var(--win-text-muted)] font-mono max-w-[80%] text-center break-all opacity-50">{{ title }}</span>
              </div>
          </div>

          <!-- Content Side -->
          <div class="w-full md:w-2/3 flex flex-col overflow-y-auto custom-scrollbar md:relative bg-transparent">
              
              <!-- Scrollable Content -->
              <div class="p-6 md:p-8 pb-32 md:pb-8">
                  <!-- Header -->
                  <div class="mb-4 md:mb-6">
                      <div class="flex items-start justify-between gap-4">
                          <div>
                              <h2 class="text-2xl md:text-3xl font-bold text-white mb-2 leading-tight flex items-center gap-3">
                                  {{ title }}
                                  <a v-if="item.homepage" :href="item.homepage" target="_blank" class="text-gray-500 hover:text-[var(--win-accent)] transition-colors" title="Official Website">
                                      <UIcon name="i-heroicons-link" class="w-5 h-5" />
                                  </a>
                              </h2>
                              <!-- Job Status Badge -->
                              <p v-if="job?.status" class="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider mb-3" :class="getStatusBadgeClass(job.status)">
                                  {{ job.status }}
                              </p>
                          </div>
                      </div>
                      
                      <p v-if="item.tagline" class="text-gray-400 italic mb-3 text-sm">{{ item.tagline }}</p>
                      
                      <!-- Tech Tags -->
                      <div v-if="techTags.length" class="flex flex-wrap gap-2 mb-3">
                        <span 
                          v-for="tag in techTags" 
                          :key="tag.label"
                          :class="[
                              'text-[10px] font-bold px-2 py-1 rounded uppercase tracking-wider',
                              tag.color
                          ]"
                        >
                          {{ tag.label }}
                        </span>
                      </div>

                      <div class="flex flex-wrap items-center gap-4 text-sm mt-3">
                          <span v-if="year" class="text-white font-mono bg-white/10 px-2 py-0.5 rounded">{{ year }}</span>
                          <span v-if="item.status" class="text-gray-400 border border-gray-700 px-2 py-0.5 rounded text-xs capitalize">{{ item.status }}</span>
                          
                          <!-- Job Specific Date -->
                          <span v-if="job?.created_at" class="text-[var(--win-text-muted)] flex items-center gap-1">
                               <UIcon name="i-heroicons-calendar" class="w-4 h-4" />
                               {{ formatDate(job.created_at) }}
                          </span>
 
                          <span v-if="rating" class="text-amber-400 flex items-center gap-1 font-bold">
                              <UIcon name="i-heroicons-star" class="w-4 h-4" />
                              {{ parseFloat(rating).toFixed(1) }}
                          </span>
                          
                          <!-- Trailer -->
                          <button 
                              v-if="item.trailer_url"
                              @click="openExternal(item.trailer_url)"
                              class="flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-bold bg-[var(--win-accent)]/10 text-[var(--win-accent)] hover:bg-[var(--win-accent)] hover:text-black transition-colors"
                          >
                              <UIcon name="i-simple-icons-youtube" class="w-3.5 h-3.5" />
                              <span>Trailer</span>
                          </button>
                      </div>
                  </div>

                  <!-- Genres -->
                  <div v-if="genres.length" class="flex flex-wrap gap-2 mb-6">
                      <span v-for="g in genres" :key="g" class="px-3 py-1 bg-[var(--win-accent)]/10 text-[var(--win-accent)] border border-[var(--win-accent)]/20 rounded-full text-xs font-bold uppercase tracking-wider">
                          {{ g }}
                      </span>
                  </div>

                  <!-- Overview -->
                  <div class="mb-8" v-if="overview">
                      <h3 class="text-gray-500 text-xs font-bold uppercase mb-2 tracking-widest">Overview</h3>
                      <p class="text-gray-300 leading-relaxed text-sm lg:text-base">
                          {{ overview }}
                      </p>
                  </div>
                  
                  <!-- === JOB SPECIFIC SECTION === -->
                  <div v-if="job" class="mb-8 animate-in slide-in-from-bottom-2">
                       <div class="flex items-center gap-2 mb-3">
                           <div class="h-px bg-white/10 flex-1"></div>
                           <span class="text-xs font-bold uppercase tracking-widest text-[var(--win-text-muted)]">Transfer Details</span>
                           <div class="h-px bg-white/10 flex-1"></div>
                       </div>
                       
                       <!-- Progress -->
                        <div v-if="['processing', 'queued'].includes(job.status)" class="bg-[var(--glass-level-2-bg)] p-4 rounded-xl border border-white/5 mb-4">
                            <div class="flex justify-between items-end mb-2">
                                <span class="text-xs font-bold text-[var(--win-text-muted)] uppercase">Progress</span>
                                <span class="text-2xl font-bold text-[var(--win-accent)]">{{ progressPercent }}%</span>
                            </div>
                            <div class="h-2 bg-[var(--glass-level-1-bg)] rounded-full overflow-hidden w-full relative mb-2">
                                <div class="h-full bg-gradient-to-r from-[var(--brand-1)] to-[var(--brand-5)] transition-all duration-300" :style="{ width: `${progressPercent}%` }"></div>
                                <div v-if="job.status === 'processing'" class="absolute inset-0 bg-[var(--win-text-primary)]/20 animate-pulse-slow"></div>
                            </div>
                            <div class="flex justify-between text-xs text-[var(--win-text-muted)] font-mono">
                                    <span>{{ formatSize(job.copied_size_bytes) }} / {{ formatSize(job.total_size_bytes || item.size_bytes) }}</span>
                                    <span v-if="eta">{{ eta }} remaining</span>
                            </div>
                        </div>
                        
                        <!-- Error -->
                        <div v-if="job.error_message" class="mb-4 p-4 bg-[var(--status-error)]/10 border border-[var(--status-error)]/30 rounded-xl">
                            <h4 class="text-[var(--status-error)] font-bold text-xs uppercase mb-1 flex items-center gap-2">
                                <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4" />
                                Error Details
                            </h4>
                            <p class="text-[var(--status-error)]/80 text-sm font-mono break-words">{{ job.error_message }}</p>
                        </div>
                        
                        <!-- Paths -->
                        <div class="bg-black/30 p-4 rounded-lg border border-white/5 space-y-3">
                              <!-- Source (Always shown in modal) -->
                              <div>
                                   <div class="flex items-center gap-2 mb-2 text-gray-500 text-xs font-bold uppercase">
                                       <span class="w-8 text-right">SRC</span>
                                       <UIcon name="i-heroicons-folder" class="w-4 h-4" />
                                       Source
                                   </div>
                                   <code class="text-xs text-[var(--win-accent)] break-all font-mono select-all block pl-10">
                                       {{ job.source_path || job.full_path || item.full_path }}
                                   </code>
                              </div>
                              
                              <!-- Destination (Job Only) -->
                              <div>
                                  <div class="flex items-center justify-between mb-2">
                                      <div class="flex items-center gap-2 text-gray-500 text-xs font-bold uppercase">
                                          <span class="w-8 text-right">DST</span>
                                          <UIcon name="i-heroicons-folder-open" class="w-4 h-4" />
                                          Destination
                                      </div>
                                  </div>
                                  <code class="text-xs text-[var(--brand-5)] break-all font-mono select-all block pl-10">
                                      {{ job.destination_path || 'Not set' }}
                                  </code>
                              </div>
                        </div>
                  </div>

                  <!-- === ITEM FILE INFO (If no job) === -->
                  <div v-else class="bg-black/30 p-4 rounded-lg border border-white/5 mb-2 grid grid-cols-2 gap-4">
                      <div class="col-span-2">
                           <div class="flex items-center gap-2 mb-2 text-gray-500 text-xs font-bold uppercase">
                               <UIcon name="i-heroicons-folder" class="w-4 h-4" />
                               Source File
                           </div>
                           <code class="text-xs text-[var(--win-accent)] break-all font-mono select-all block">
                               {{ item.full_path }}
                           </code>
                      </div>
                      
                      <div>
                           <div class="flex items-center gap-2 mb-2 text-gray-500 text-xs font-bold uppercase">
                               <UIcon name="i-heroicons-server" class="w-4 h-4" />
                               File Size
                           </div>
                           <div class="text-xs text-white font-mono font-bold">
                               {{ item.size_formatted || formatSize(item.size_bytes) || 'Unknown' }}
                           </div>
                      </div>
                  </div>
              </div>

              <!-- Sticky Actions Footer -->
              <div class="fixed md:static bottom-0 left-0 right-0 p-4 md:p-8 bg-[var(--win-bg-base)]/95 md:bg-transparent backdrop-blur-xl md:backdrop-blur-none border-t border-white/10 md:border-none z-20 flex gap-3 mt-auto">
                  
                  <!-- Job Actions -->
                  <template v-if="job">
                      <button 
                          v-if="job.status === 'queued' || job.status === 'processing'"
                          @click="$emit('cancel', job.id)"
                          class="flex-1 py-3 bg-[var(--status-error)]/20 hover:bg-[var(--status-error)]/30 border border-[var(--status-error)]/30 text-[var(--status-error)] font-bold rounded-xl md:rounded-lg transition-colors flex items-center justify-center gap-2 active:scale-95 md:active:scale-100"
                      >
                          <UIcon name="i-heroicons-x-mark" class="w-5 h-5" />
                          Cancel
                      </button>

                      <button 
                          v-if="job.status === 'failed'"
                          @click="$emit('retry', job.id)"
                          class="flex-1 py-3 bg-[var(--brand-1)] hover:bg-[var(--brand-2)] text-[var(--win-bg-base)] font-bold rounded-xl md:rounded-lg transition-colors flex items-center justify-center gap-2 shadow-lg shadow-[var(--brand-1)]/20 active:scale-95 md:active:scale-100"
                      >
                          <UIcon name="i-heroicons-arrow-path" class="w-5 h-5" />
                          Retry
                      </button>
                  </template>
                  
                  <!-- Library Actions -->
                  <template v-else>
                      <button 
                          v-if="item.tmdb_id"
                          @click="$emit('view-trakt', item)"
                          class="flex-1 py-3 md:py-3 bg-[var(--win-accent)]/10 hover:bg-[var(--win-accent)]/20 border border-[var(--win-accent)]/20 text-[var(--win-accent)] font-bold rounded-xl md:rounded-lg transition-colors flex items-center justify-center gap-2 active:scale-95 md:active:scale-100"
                      >
                          <UIcon name="i-heroicons-arrow-top-right-on-square" class="w-5 h-5" />
                          <span class="md:hidden">Trakt</span>
                          <span class="hidden md:inline">View Trakt</span>
                      </button>
                      <button 
                          @click="$emit('copy', item)"
                          class="flex-1 py-3 md:py-3 bg-[var(--win-accent)] hover:bg-[var(--win-accent)]/80 text-black font-bold rounded-xl md:rounded-lg transition-colors flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/20 active:scale-95 md:active:scale-100"
                      >
                          <UIcon name="i-heroicons-document-duplicate" class="w-5 h-5" />
                          Copy to Library
                      </button>
                  </template>

                  <button 
                      @click="$emit('close')"
                      class="hidden md:flex flex-1 py-3 btn-ghost justify-center rounded-xl md:rounded-lg"
                  >
                      Close
                  </button>
              </div>

          </div>
      </div>
  </div>
</template>

<script setup lang="ts">
import { useWebSocket } from '~/composables/useWebSocket'

const props = defineProps<{
  item: any // MediaItem or Job (normalized)
  job?: any // CopyJob (optional, present if from Queue/History)
  show?: boolean
}>()

const emit = defineEmits(['close', 'cancel', 'retry', 'copy', 'view-trakt'])

const config = useRuntimeConfig()
const apiBase = config.public.apiBase 
const { getEstimatedTimeRemaining, getJobProgress } = useWebSocket()

// Normalization
// Sometimes "item" is a Job object if passed directly, so we fallback
const title = computed(() => props.item?.title || props.item?.media_title || props.job?.media_title || props.job?.media_item?.title || getFileName(props.item?.full_path || props.job?.source_path))
const posterUrl = computed(() => props.item?.poster_url || props.item?.media_poster || props.job?.media_poster || props.job?.media_item?.poster_url)
const year = computed(() => props.item?.year || props.item?.media_year || props.job?.media_year)
const rating = computed(() => props.item?.rating || props.item?.media_rating || props.job?.media_rating)
const overview = computed(() => props.item?.overview || props.job?.media_item?.overview) // Jobs often don't have overview unless enriched into media_item
const genres = computed(() => props.item?.genres || props.job?.media_item?.genres || [])
const isMovie = computed(() => (props.item?.media_type || props.job?.media_type) === 'movie')

// Tech Tags
const techTags = computed(() => {
    const i = props.item || {}
    const tags = []
    
    // Resolution
    if (i.resolution || i.full_path?.toLowerCase().includes('2160p') || i.full_path?.toLowerCase().includes('4k')) {
       tags.push({ label: '4K UHD', color: 'text-[var(--win-accent)] bg-[var(--win-accent)]/10' })
    } else if (i.full_path?.toLowerCase().includes('1080p')) {
       tags.push({ label: '1080p', color: 'text-white bg-white/10' })
    }
    
    // HDR
    if (i.hdr || i.full_path?.toLowerCase().includes('hdr') || i.full_path?.toLowerCase().includes('dv')) {
       tags.push({ label: 'HDR', color: 'text-purple-400 bg-purple-400/10' })
    }
    
    // Audio
    if (i.audio_codec?.includes('atmos') || i.full_path?.toLowerCase().includes('atmos')) {
       tags.push({ label: 'Dolby Atmos', color: 'text-blue-400 bg-blue-400/10' })
    }
    
    return tags
})

// Job Specifics
const progressPercent = computed(() => {
    // Try realtime from websocket first, then job prop
    if (props.job?.id) {
        const live = getJobProgress(props.job.id)
        if (live) return live.progress_percent
    }
    return props.job?.progress_percent || 0
})

const eta = computed(() => {
  if (props.job?.id && props.job.status === 'processing') {
      return getEstimatedTimeRemaining(props.job.id)
  }
  return null
})

// Utilities
const getFileName = (path?: string) => path?.split('/').pop() || 'Unknown File'

const formatSize = (bytes?: number) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
}

const formatDate = (dateString?: string) => {
    if (!dateString) return ''
    return new Date(dateString).toLocaleString()
}

const getStatusBadgeClass = (status: string) => {
  switch (status) {
    case 'completed': return 'bg-[var(--status-success)]/10 text-[var(--status-success)] border border-[var(--status-success)]/20'
    case 'failed': return 'bg-[var(--status-error)]/10 text-[var(--status-error)] border border-[var(--status-error)]/20'
    case 'processing': return 'bg-[var(--brand-1)]/10 text-[var(--brand-1)] border border-[var(--brand-1)]/20'
    default: return 'bg-[var(--glass-level-2-bg)] text-[var(--win-text-muted)] border border-white/10'
  }
}

const openExternal = (url: string) => window.open(url, '_blank')
</script>

<style scoped>
/* Scrollbar styling matching app */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: var(--glass-level-1-bg);
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: var(--glass-level-2-bg);
  border-radius: 3px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: var(--glass-level-3-bg);
}

@keyframes pulse-slow {
  0%, 100% { opacity: 0.1; }
  50% { opacity: 0.3; }
}
.animate-pulse-slow {
  animation: pulse-slow 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
