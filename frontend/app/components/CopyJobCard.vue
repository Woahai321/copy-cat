```html
<template>
  <div class="relative overflow-hidden rounded-lg group">
    <!-- Background Action (Swipe Reveal) -->
    <div 
        v-if="canSwipe"
        class="absolute inset-y-0 right-0 w-[100px] flex items-center justify-center z-0 transition-colors cursor-pointer"
        :class="job.status === 'queued' ? 'bg-[var(--status-error)]/10 text-[var(--status-error)] border-[var(--status-error)]/20' : 'bg-[var(--brand-1)]/10 text-[var(--brand-1)] border-[var(--brand-1)]/20'"
        @click="handleAction"
    >
        <!-- Background Gradient -->
        <div class="absolute inset-0 bg-gradient-to-br opacity-10 transition-opacity group-hover:opacity-20 pointer-events-none"
             :class="job.status === 'queued' ? 'from-[var(--status-error)] to-gray-600' : 'from-[var(--brand-1)] to-[var(--brand-5)]'"></div>
        <div class="flex flex-col items-center gap-1 font-bold text-xs uppercase tracking-wider relative z-10">
            <UIcon :name="job.status === 'queued' ? 'i-heroicons-trash' : 'i-heroicons-arrow-path'" class="w-6 h-6" />
            <span>{{ job.status === 'queued' ? 'Cancel' : 'Retry' }}</span>
        </div>
    </div>

    <!-- Foreground Card -->
    <div 
        ref="cardEl"
        @click="handleClick"
        class="relative z-10 card bg-[var(--glass-level-2-bg)] border border-white/5 rounded-xl overflow-hidden hover:border-[var(--win-accent)]/50 transition-all duration-300 cursor-pointer group-hover:shadow-[0_8px_30px_rgba(0,0,0,0.6)]"
        :style="cardStyle"
    >
        <div class="flex gap-4 items-stretch h-full">
          <!-- Poster / Icon Section -->
          <div class="relative w-20 sm:w-28 flex-shrink-0 bg-[var(--glass-level-3-bg)] border-r border-white/5 overflow-hidden group/poster">
             <img 
               v-if="job.media_poster" 
               :src="job.media_poster.startsWith('http') ? job.media_poster : `${apiBase}${job.media_poster}`" 
               class="w-full h-full object-cover transition-transform duration-700 group-hover/poster:scale-110"
               loading="lazy"
             />
             <div v-else class="w-full h-full flex flex-col items-center justify-center p-2 bg-gradient-to-br from-[var(--glass-level-1-bg)] to-[var(--win-bg-base)] text-center">
                <UIcon 
                  :name="job.media_type ? (job.media_type === 'movie' ? 'i-heroicons-film' : 'i-heroicons-tv') : getTypeIcon(job.source_path)" 
                  class="w-8 h-8 mb-1 opacity-50" 
                  :class="job.media_type ? 'text-[var(--win-text-muted)]' : getTypeClass(job.source_path)"
                />
                <span class="text-[9px] font-bold text-[var(--win-text-muted)] line-clamp-2 leading-tight px-1 break-words w-full">
                    {{ job.media_title || getJobName(job.source_path) }}
                </span>
             </div>

             <!-- Status Overlay for Processing -->
             <div v-if="job.status === 'processing'" class="absolute inset-0 bg-[var(--win-accent)]/10 backdrop-blur-[1px] flex items-center justify-center">
                <div class="w-1.5 h-1.5 rounded-full bg-[var(--win-accent)] animate-ping shadow-[0_0_10px_var(--win-accent)]"></div>
             </div>
          </div>

          <!-- Content Section -->
          <div class="flex-1 min-w-0 p-4 flex flex-col justify-between py-5">
            <div>
              <div class="flex items-start justify-between mb-2">
                <div class="min-w-0 pr-4">
                  <h4 class="text-base sm:text-lg font-bold text-[var(--win-text-primary)] truncate leading-tight mb-1" :title="job.media_title || getJobName(job.source_path)">
                      {{ job.media_title || getJobName(job.source_path) }}
                  </h4>
                  <div class="flex items-center gap-2 flex-wrap">
                    <span v-if="job.media_year" class="text-[10px] font-bold text-[var(--win-text-muted)] bg-[var(--glass-level-1-bg)] px-1.5 py-0.5 rounded border border-white/10">
                      {{ job.media_year }}
                    </span>
                    <span v-if="job.media_rating" class="flex items-center gap-1 text-[10px] font-bold text-[var(--brand-1)] bg-[var(--brand-1)]/10 px-1.5 py-0.5 rounded border border-[var(--brand-1)]/20">
                      <UIcon name="i-heroicons-star" class="w-3 h-3" />
                      {{ job.media_rating.toFixed(1) }}
                    </span>
                    <span class="text-[10px] text-[var(--win-text-muted)] font-medium">
                      {{ formatRelativeTime(job.created_at) }}
                    </span>
                  </div>
                </div>
                <div class="flex flex-col items-end gap-2">
                  <span 
                      class="text-[9px] uppercase font-black px-2 py-0.5 rounded-full"
                      :class="getStatusBadgeClass(job.status)"
                  >
                      {{ job.status }}
                  </span>
                </div>
              </div>

              <!-- Paths -->
              <div class="text-[10px] text-[var(--win-text-muted)] font-mono flex flex-col gap-1 mt-3 group-hover:text-[var(--win-text-secondary)] transition-colors">
                <div class="flex items-center gap-2 truncate opacity-60" :title="job.source_path">
                    <span class="w-6 text-right shrink-0">SRC:</span> 
                    <span class="truncate">{{ job.source_path }}</span>
                </div>
                <div class="flex items-center gap-2 truncate opacity-60" :title="job.destination_path">
                    <span class="w-6 text-right shrink-0">DST:</span> 
                    <span class="truncate">{{ job.destination_path }}</span>
                </div>
              </div>
            </div>

            <!-- Bottom Row: Stats & Progress -->
            <div class="mt-4 flex items-end justify-between gap-4">
               <div class="flex-1">
                  <div v-if="['processing', 'queued'].includes(job.status)" class="space-y-1.5">
                      <!-- Progress Bar -->
                      <div class="h-1.5 bg-[var(--glass-level-4-bg)] rounded-full overflow-hidden w-full relative">
                          <div class="h-full bg-gradient-to-r from-[var(--brand-1)] to-[var(--brand-5)] transition-all duration-300" :style="{ width: `${progressPercent}%` }"></div>
                          <div class="absolute inset-0 bg-[var(--glass-level-3-bg)] animate-pulse-slow" v-if="job.status === 'processing'"></div>
                      </div>
                      <div class="flex justify-between items-center text-[10px]">
                          <span class="font-bold text-[var(--win-accent)]">{{ progressPercent }}% <span class="text-[var(--win-text-muted)] font-medium ml-1">completed</span></span>
                          <span v-if="eta" class="text-[var(--win-text-muted)] font-mono">{{ eta }} remaining</span>
                      </div>
                  </div>
                  <div v-else class="flex items-center gap-3 text-[10px] font-medium text-[var(--win-text-muted)]">
                    <span class="flex items-center gap-1"><UIcon name="i-heroicons-clock" class="w-3 h-3"/> {{ formatDateShort(job.created_at) }}</span>
                    <span class="flex items-center gap-1"><UIcon name="i-heroicons-square-3-stack-3d" class="w-3 h-3"/> {{ formatSize(job.total_size_bytes) }}</span>
                  </div>
               </div>

              <!-- Desktop Actions -->
              <div v-if="showActions && ['queued', 'failed'].includes(job.status)" class="hidden md:flex items-center gap-1">
                <button
                    v-if="job.status === 'queued'"
                    @click.stop="$emit('cancel', job.id)"
                    class="p-2 hover:bg-[var(--status-error)]/20 rounded-lg text-[var(--win-text-muted)] hover:text-[var(--status-error)] transition-all border border-transparent hover:border-[var(--status-error)]/30"
                    title="Cancel"
                >
                    <UIcon name="i-heroicons-x-mark" class="w-5 h-5" />
                </button>
                <button
                    v-if="job.status === 'failed'"
                    @click.stop="$emit('retry', job.id)"
                    class="p-2 hover:bg-[var(--win-accent)]/20 rounded-lg text-[var(--win-text-muted)] hover:text-[var(--win-accent)] transition-all border border-transparent hover:border-[var(--win-accent)]/30"
                    title="Retry"
                >
                    <UIcon name="i-heroicons-arrow-path" class="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Error Footer -->
        <div v-if="job.error_message" class="px-4 py-2 bg-[var(--status-error)]/10 border-t border-[var(--status-error)]/10 text-[var(--status-error)] text-[10px] font-medium flex items-center gap-2">
          <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4" />
          {{ job.error_message }}
        </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useSwipe, useWindowSize } from '@vueuse/core'

const { getEstimatedTimeRemaining } = useWebSocket() 
const config = useRuntimeConfig()
const apiBase = config.public.apiBase 

interface CopyJob {
  id: number
  source_path: string
  destination_path: string
  status: string
  progress_percent: number
  total_size_bytes: number
  copied_size_bytes: number
  error_message: string | null
  created_at: string
  completed_at: string | null
  // Enriched
  media_title?: string | null
  media_year?: number | null
  media_rating?: number | null
  media_poster?: string | null
  media_type?: string | null
}

interface Props {
  job: CopyJob
  showActions?: boolean
  realtimeProgress?: { progress_percent: number; copied_size_bytes: number; total_size_bytes: number } | null
  customClick?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showActions: true,
  realtimeProgress: null
})

const emit = defineEmits<{
  cancel: [jobId: number]
  retry: [jobId: number]
  click: [job: CopyJob]
}>()

// --- Swipe Logic ---
const cardEl = ref<HTMLElement | null>(null)
const { width: windowWidth } = useWindowSize()
const isMobile = computed(() => windowWidth.value < 768)

// We only enable swipe on mobile and if actions are available
// status: queued -> cancel (swipe left)
// status: failed -> retry (swipe left)
const canSwipe = computed(() => isMobile.value && props.showActions && ['queued', 'failed'].includes(props.job.status))

const { lengthX, isSwiping: isSwipingVueUse } = useSwipe(cardEl, {
  passive: true,
  onSwipeEnd(e: TouchEvent, direction: string) {
      if (lengthX.value < -80) {
          // Swiped left enough, keep open or trigger?
          // Let's toggle 'revealed' state
          if (revealed.value) revealed.value = false
          else revealed.value = true
      } else {
          revealed.value = false
      }
  },
})

const revealed = ref(false)

const swipeOffset = computed(() => {
    if (!canSwipe.value) return 0
    if (revealed.value) return -100 // Width of action button
    if (lengthX.value < 0) return Math.max(lengthX.value, -100) // Dragging left
    return 0
})

const cardStyle = computed(() => ({
    transform: `translateX(${swipeOffset.value}px)`,
    transition: isSwipingVueUse.value ? 'none' : 'transform 0.2s ease-out'
}))

// --- End Swipe ---

const progressPercent = computed(() => props.realtimeProgress?.progress_percent ?? props.job.progress_percent)

const eta = computed(() => {
  if (props.job.status !== 'processing') return null
  return getEstimatedTimeRemaining(props.job.id) 
})

const getJobName = (path: string) => path.split('/').pop() || path

// New Logic to distinguish icons
const isMovie = (path: string) => {
  const ext = path.split('.').pop()?.toLowerCase()
  return ['mkv', 'mp4', 'avi', 'mov', 'wmv'].includes(ext || '')
}

const getTypeIcon = (path: string) => {
  return isMovie(path) ? 'i-heroicons-film' : 'i-heroicons-folder-20-solid'
}

const getTypeClass = (path: string) => {
   // Movie = Win11 Blueish/Purple, Folder = Yellow
   return isMovie(path) ? 'text-[var(--brand-10)]' : 'text-[var(--brand-1)]'
}

const getStatusBadgeClass = (status: string) => {
  switch (status) {
    case 'completed': return 'bg-[var(--status-success)]/10 text-[var(--status-success)] border border-[var(--status-success)]/20'
    case 'failed': return 'bg-[var(--status-error)]/10 text-[var(--status-error)] border border-[var(--status-error)]/20'
    case 'processing': return 'bg-[var(--status-info)]/10 text-[var(--status-info)] border border-[var(--status-info)]/20'
    case 'queued': return 'bg-[var(--status-warning)]/10 text-[var(--status-warning)] border border-[var(--status-warning)]/20'
    default: return 'bg-[var(--glass-level-1-bg)] text-[var(--win-text-muted)] border border-white/10'
  }
}

const formatSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
}

const formatDate = (dateString: string) => new Date(dateString).toLocaleString()

const formatDateShort = (dateString: string) => {
  const d = new Date(dateString)
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const formatRelativeTime = (dateString: string) => {
  const now = new Date()
  const then = new Date(dateString)
  const diffInSeconds = Math.floor((now.getTime() - then.getTime()) / 1000)

  if (diffInSeconds < 60) return 'just now'
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`
  return `${Math.floor(diffInSeconds / 86400)}d ago`
}

const handleAction = () => {
    revealed.value = false // close swipe
    if (props.job.status === 'queued') emit('cancel', props.job.id)
    if (props.job.status === 'failed') emit('retry', props.job.id)
}

const handleClick = () => {
    emit('click', props.job)
}
</script>

<style scoped>


@keyframes pulse-slow {
  0%, 100% { opacity: 0.1; }
  50% { opacity: 0.3; }
}

.animate-pulse-slow {
  animation: pulse-slow 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
