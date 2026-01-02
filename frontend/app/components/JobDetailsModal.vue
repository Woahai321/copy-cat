<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-end md:items-center justify-center md:p-4 bg-[var(--glass-level-4-bg)] backdrop-blur-md animate-in fade-in duration-200" @click.self="$emit('close')">
      <!-- Modal Container -->
      <div class="bg-[var(--win-bg-base)] md:bg-[var(--glass-level-3-bg)] md:backdrop-blur-xl w-full max-w-4xl h-[100dvh] md:h-auto md:rounded-2xl md:overflow-hidden shadow-[0_0_50px_rgba(0,0,0,0.8)] border-x md:border border-white/10 flex flex-col md:flex-row md:max-h-[85vh] relative">
          
          <!-- Close Button (Mobile Floating) -->
          <button @click="$emit('close')" class="absolute top-4 right-4 z-30 md:hidden w-10 h-10 bg-[var(--glass-level-4-bg)] backdrop-blur-md rounded-full flex items-center justify-center text-[var(--win-text-primary)] border border-white/10 shadow-lg active:scale-95 transition-transform">
              <UIcon name="i-heroicons-x-mark" class="w-6 h-6" />
          </button>

          <!-- Poster Side -->
          <div class="w-full md:w-1/3 aspect-[2/3] md:aspect-auto md:h-auto relative group shrink-0">
              <!-- Mobile Gradient Overlay for Text Readability -->
              <div class="absolute inset-0 bg-gradient-to-t from-[var(--win-bg-base)] via-transparent to-transparent z-10 md:hidden"></div>
              
              <img 
                 v-if="job.media_poster || job.poster_url" 
                 :src="(job.media_poster || job.poster_url || '').startsWith('http') ? (job.media_poster || job.poster_url) : `${apiBase}${(job.media_poster || job.poster_url)}`" 
                 class="w-full h-full object-cover bg-[var(--glass-level-4-bg)] object-top"
              />
              <div v-else class="w-full h-full flex flex-col items-center justify-center bg-[var(--glass-level-1-bg)] gap-4">
                  <UIcon :name="job.media_type === 'movie' ? 'i-heroicons-film' : (job.media_type === 'tv' ? 'i-heroicons-tv' : 'i-heroicons-document')" class="w-20 h-20 text-[var(--win-text-muted)]" />
                  <span class="text-xs text-[var(--win-text-secondary)] font-mono max-w-[80%] text-center break-all">{{ getJobName(job.source_path || job.full_path) }}</span>
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
                              <h2 class="text-2xl md:text-3xl font-bold text-[var(--win-text-primary)] mb-2 leading-tight">{{ job.media_title || job.title || getJobName(job.source_path || job.full_path) }}</h2>
                              <p v-if="job.status" class="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider mb-3" :class="getStatusBadgeClass(job.status)">
                                  {{ job.status }}
                              </p>
                              <p v-else-if="isLibraryItem && job.tagline" class="text-[var(--win-text-muted)] italic mb-3 text-sm">{{ job.tagline }}</p>
                          </div>
                      </div>

                      <div class="flex flex-wrap items-center gap-4 text-sm mt-3">
                          <span v-if="job.media_year || job.year" class="text-[var(--win-text-primary)] font-mono bg-[var(--glass-level-2-bg)] px-2 py-0.5 rounded">{{ job.media_year || job.year }}</span>
                          <span v-if="job.media_rating || job.rating" class="text-[var(--brand-1)] flex items-center gap-1 font-bold">
                              <UIcon name="i-heroicons-star" class="w-4 h-4" />
                              {{ parseFloat(job.media_rating || job.rating).toFixed(1) }}
                          </span>
                           <span class="text-[var(--win-text-muted)] flex items-center gap-1">
                              <UIcon name="i-heroicons-calendar" class="w-4 h-4" />
                              {{ formatDate(job.created_at) }}
                          </span>
                      </div>
                  </div>
                  
                  <!-- Library Item Overview -->
                  <div v-if="isLibraryItem && job.overview" class="mb-8">
                      <h3 class="text-[var(--win-text-muted)] text-xs font-bold uppercase mb-2 tracking-widest">Overview</h3>
                      <p class="text-[var(--win-text-secondary)] leading-relaxed text-sm lg:text-base">
                          {{ job.overview }}
                      </p>
                  </div>

                  <!-- Progress Section (Queued/Processing) -->
                  <div v-if="['processing', 'queued'].includes(job.status)" class="bg-[var(--glass-level-2-bg)] p-4 rounded-xl border border-white/5 mb-6">
                      <div class="flex justify-between items-end mb-2">
                          <span class="text-xs font-bold text-[var(--win-text-muted)] uppercase">Progress</span>
                          <span class="text-2xl font-bold text-[var(--win-accent)]">{{ progressPercent }}%</span>
                      </div>
                      <div class="h-2 bg-[var(--glass-level-1-bg)] rounded-full overflow-hidden w-full relative mb-2">
                          <div class="h-full bg-gradient-to-r from-[var(--brand-1)] to-[var(--brand-5)] transition-all duration-300" :style="{ width: `${progressPercent}%` }"></div>
                          <div v-if="job.status === 'processing'" class="absolute inset-0 bg-[var(--win-text-primary)]/20 animate-pulse-slow"></div>
                      </div>
                      <div class="flex justify-between text-xs text-[var(--win-text-muted)] font-mono">
                           <span>{{ formatSize(job.copied_size_bytes) }} / {{ formatSize(job.total_size_bytes) }}</span>
                           <span v-if="eta">{{ eta }} remaining</span>
                      </div>
                  </div>

                  <!-- Completed Stats -->
                  <div v-if="job.status === 'completed'" class="grid grid-cols-2 gap-4 mb-6">
                       <div class="bg-[var(--glass-level-2-bg)] p-3 rounded-lg border border-white/5">
                           <div class="text-[10px] text-[var(--win-text-muted)] uppercase font-bold mb-1">Total Size</div>
                           <div class="text-[var(--win-text-primary)] font-mono">{{ formatSize(job.total_size_bytes) }}</div>
                       </div>
                       <div class="bg-[var(--glass-level-2-bg)] p-3 rounded-lg border border-white/5">
                           <div class="text-[10px] text-[var(--win-text-muted)] uppercase font-bold mb-1">Duration</div>
                           <div class="text-[var(--win-text-primary)] font-mono">{{ getDuration(job) }}</div>
                       </div>
                  </div>

                  <!-- Error Message -->
                  <div v-if="job.error_message" class="mb-6 p-4 bg-[var(--status-error)]/10 border border-[var(--status-error)]/30 rounded-xl">
                      <h4 class="text-[var(--status-error)] font-bold text-xs uppercase mb-1 flex items-center gap-2">
                          <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4" />
                          Error Details
                      </h4>
                      <p class="text-[var(--status-error)]/80 text-sm font-mono break-words">{{ job.error_message }}</p>
                  </div>

                  <!-- Paths -->
                  <div class="space-y-3 mb-8">
                      <div class="bg-[var(--glass-level-2-bg)] p-4 rounded-lg border border-white/5 grid grid-cols-2 gap-4">
                          <div class="col-span-2">
                              <div class="flex items-center gap-2 mb-2 text-[var(--win-text-muted)] text-xs font-bold uppercase">
                                  <span class="w-8 text-right">SRC</span>
                                  <UIcon name="i-heroicons-folder" class="w-4 h-4" />
                                  Source
                              </div>
                              <code class="text-xs text-[var(--brand-1)] break-all font-mono select-all block pl-10">
                                  {{ job.source_path || job.full_path }}
                              </code>
                          </div>

                          <div>
                               <div class="flex items-center gap-2 mb-2 text-[var(--win-text-muted)] text-xs font-bold uppercase pl-10">
                                   <UIcon name="i-heroicons-server" class="w-4 h-4" />
                                   File Size
                               </div>
                               <div class="text-xs text-[var(--win-text-primary)] font-mono font-bold pl-10">
                                   {{ formatSize(job.total_size_bytes || job.size_bytes) }}
                               </div>
                          </div>
                      </div>
                      
                      <div v-if="!isLibraryItem" class="bg-[var(--glass-level-2-bg)] p-4 rounded-lg border border-white/5">
                          <div class="flex items-center justify-between mb-2">
                              <div class="flex items-center gap-2 text-[var(--win-text-muted)] text-xs font-bold uppercase">
                                  <span class="w-8 text-right">DST</span>
                                  <UIcon name="i-heroicons-folder-open" class="w-4 h-4" />
                                  Destination
                              </div>
                              <button @click="copyToClipboard(job.destination_path)" class="text-[10px] text-[var(--win-text-muted)] hover:text-[var(--win-text-primary)] flex items-center gap-1">
                                  <UIcon name="i-heroicons-clipboard" class="w-3 h-3" /> Copy
                              </button>
                          </div>
                          <code class="text-xs text-[var(--brand-5)] break-all font-mono select-all block pl-10">
                              {{ job.destination_path || 'Not set' }}
                          </code>
                      </div>
                  </div>
              </div>

              <!-- Sticky Actions Footer -->
              <div class="fixed md:static bottom-0 left-0 right-0 p-4 md:p-8 bg-[var(--win-bg-base)]/95 md:bg-transparent backdrop-blur-xl md:backdrop-blur-none border-t border-white/10 md:border-none z-20 flex gap-3 mt-auto">
                  <button 
                      v-if="job.status === 'queued'"
                      @click="$emit('cancel', job.id)"
                      class="flex-1 py-3 bg-[var(--status-error)]/20 hover:bg-[var(--status-error)]/30 border border-[var(--status-error)]/30 text-[var(--status-error)] font-bold rounded-xl md:rounded-lg transition-colors flex items-center justify-center gap-2 active:scale-95 md:active:scale-100"
                  >
                      <UIcon name="i-heroicons-x-mark" class="w-5 h-5" />
                      Cancel Transfer
                  </button>

                  <button 
                      v-if="isLibraryItem"
                      @click="$emit('copy', job)"
                      class="flex-1 py-3 bg-[var(--brand-1)] hover:bg-[var(--brand-2)] text-[var(--win-bg-base)] font-bold rounded-xl md:rounded-lg transition-colors flex items-center justify-center gap-2 shadow-lg shadow-[var(--brand-1)]/20 active:scale-95 md:active:scale-100"
                  >
                      <UIcon name="i-heroicons-document-duplicate" class="w-5 h-5" />
                      Copy to Library
                  </button>
                  
                  <button 
                      v-if="job.status === 'failed'"
                      @click="$emit('retry', job.id)"
                      class="flex-1 py-3 bg-[var(--brand-1)] hover:bg-[var(--brand-2)] text-[var(--win-bg-base)] font-bold rounded-xl md:rounded-lg transition-colors flex items-center justify-center gap-2 shadow-lg shadow-[var(--brand-1)]/20 active:scale-95 md:active:scale-100"
                  >
                      <UIcon name="i-heroicons-arrow-path" class="w-5 h-5" />
                      Retry Transfer
                  </button>

                  <button 
                      @click="$emit('close')"
                      class="flex-1 py-3 btn-ghost font-bold rounded-xl md:rounded-lg"
                  >
                      Close
                  </button>
              </div>

          </div>
      </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  job: any
  show?: boolean
  realtimeProgress?: any
  isLibraryItem?: boolean
}>()

const emit = defineEmits(['close', 'cancel', 'retry', 'copy'])

const config = useRuntimeConfig()
const apiBase = config.public.apiBase 
const { getEstimatedTimeRemaining } = useWebSocket()

// Computed
const progressPercent = computed(() => props.realtimeProgress?.progress_percent ?? props.job.progress_percent)

const eta = computed(() => {
  if (props.job.status !== 'processing') return null
  return getEstimatedTimeRemaining(props.job.id) 
})

// Helpers
const getJobName = (path: string) => path?.split('/').pop() || path

const getStatusBadgeClass = (status: string) => {
  switch (status) {
    case 'completed': return 'bg-[var(--status-success)]/10 text-[var(--status-success)] border border-[var(--status-success)]/20'
    case 'failed': return 'bg-[var(--status-error)]/10 text-[var(--status-error)] border border-[var(--status-error)]/20'
    case 'processing': return 'bg-[var(--brand-1)]/10 text-[var(--brand-1)] border border-[var(--brand-1)]/20'
    default: return 'bg-[var(--glass-level-2-bg)] text-[var(--win-text-muted)] border border-white/10'
  }
}

const formatSize = (bytes: number) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
}

const formatDate = (dateString: string) => {
    if (!dateString) return 'Unknown'
    return new Date(dateString).toLocaleString()
}

const getDuration = (job: any) => {
    if (!job.completed_at || !job.created_at) return 'Unknown'
    const start = new Date(job.created_at).getTime()
    const end = new Date(job.completed_at).getTime()
    const diff = Math.floor((end - start) / 1000)
    
    if (diff < 60) return `${diff}s`
    if (diff < 3600) return `${Math.floor(diff/60)}m ${diff%60}s`
    return `${Math.floor(diff/3600)}h ${Math.floor((diff%3600)/60)}m` 
}

const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    // could toast here if we had toast access easily or just emit
}
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
