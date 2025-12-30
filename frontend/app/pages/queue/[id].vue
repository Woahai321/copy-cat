<template>
  <div class="h-full flex flex-col p-6 space-y-6 overflow-y-auto">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-4">
        <button 
          @click="navigateTo('/queue')"
          class="p-2 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
        >
          <UIcon name="i-heroicons-arrow-left" class="w-5 h-5" />
        </button>
        <div>
          <h1 class="text-2xl font-bold text-white flex items-center gap-2">
            <UIcon name="i-heroicons-document-text" class="w-6 h-6 text-[var(--win-accent)]" />
            Job Details
            <span class="text-sm font-normal text-gray-500 font-mono">#{{ job?.id }}</span>
          </h1>
        </div>
      </div>
      
      <div v-if="job" class="flex gap-2">
         <span 
            class="px-3 py-1 rounded text-sm font-bold uppercase tracking-wider border"
            :class="getStatusClass(job.status)"
         >
            {{ job.status }}
         </span>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex flex-1 items-center justify-center">
       <UIcon name="i-heroicons-arrow-path" class="w-10 h-10 text-[var(--win-accent)] animate-spin" />
    </div>
    
    <!-- Error -->
    <div v-else-if="error" class="p-8 text-center">
       <UIcon name="i-heroicons-exclamation-circle" class="w-12 h-12 text-red-500 mx-auto mb-4" />
       <h3 class="text-xl text-white font-bold">Failed to load job</h3>
       <p class="text-gray-400">{{ error }}</p>
    </div>

    <!-- Content -->
    <div v-else-if="job" class="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-fade-in-up">
       
       <!-- Main Stats -->
       <div class="glass-panel p-6 space-y-6 lg:col-span-2">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
             
             <!-- Progress -->
             <div class="space-y-2">
                <div class="text-xs text-gray-400 uppercase tracking-widest">Progress</div>
                <div class="text-4xl font-bold text-white font-mono">
                   {{ job.status === 'completed' ? 100 : progressPercent }}<span class="text-xl text-[var(--win-accent)]">%</span>
                </div>
                 <div class="h-1.5 bg-white/10 rounded-full overflow-hidden w-full mt-2">
                    <div class="h-full bg-[var(--win-accent)] transition-all duration-300" :style="{ width: `${progressPercent}%` }"></div>
                 </div>
             </div>

             <!-- Size -->
             <div class="space-y-2">
                <div class="text-xs text-gray-400 uppercase tracking-widest">Total Size</div>
                <div class="text-3xl font-bold text-white font-mono">{{ formatSize(job.total_size_bytes) }}</div>
                <div class="text-xs text-gray-500">
                   Copied: {{ formatSize(realtimeCopiedBytes) }}
                </div>
             </div>

             <!-- Time -->
             <div class="space-y-2">
                <div class="text-xs text-gray-400 uppercase tracking-widest">Timings</div>
                <div class="space-y-1">
                   <div class="flex justify-between text-sm">
                      <span class="text-gray-500">Started:</span>
                      <span class="text-gray-200">{{ formatDate(job.created_at) }}</span>
                   </div>
                   <div v-if="job.completed_at" class="flex justify-between text-sm">
                      <span class="text-gray-500">Finished:</span>
                      <span class="text-gray-200">{{ formatDate(job.completed_at) }}</span>
                   </div>
                </div>
             </div>

          </div>
       </div>

       <!-- Paths Config -->
       <div class="glass-panel p-6 space-y-4">
          <h3 class="text-lg font-bold text-white mb-4 flex items-center gap-2">
             <UIcon name="i-heroicons-map" class="w-5 h-5 text-[var(--win-accent)]" />
             Transfer Path
          </h3>
          
          <div class="space-y-1">
             <div class="text-xs text-gray-500 font-bold uppercase">Source</div>
             <div class="p-3 bg-black/20 rounded border border-white/5 text-sm font-mono text-gray-300 break-all select-all">
                {{ job.source_path }}
             </div>
          </div>

          <div class="flex justify-center text-gray-600">
             <UIcon name="i-heroicons-arrow-down" class="w-5 h-5" />
          </div>

          <div class="space-y-1">
             <div class="text-xs text-gray-500 font-bold uppercase">Destination</div>
             <div class="p-3 bg-black/20 rounded border border-white/5 text-sm font-mono text-gray-300 break-all select-all">
                {{ job.destination_path }}
             </div>
          </div>
       </div>

       <!-- Logs / Errors -->
       <div class="glass-panel p-0 flex flex-col overflow-hidden">
          <div class="p-4 border-b border-white/10 bg-white/5">
             <h3 class="text-lg font-bold text-white flex items-center gap-2">
                <UIcon name="i-heroicons-command-line" class="w-5 h-5 text-gray-400" />
                System Output
             </h3>
          </div>
          <div class="flex-1 p-4 bg-black/40 font-mono text-xs text-gray-400 overflow-y-auto max-h-[300px]">
             <div v-if="job.error_message" class="text-red-400">
                <span class="text-red-600 font-bold">[ERROR]</span> {{ job.error_message }}
             </div>
             <div v-else class="text-gray-600 italic">No errors reported.</div>
             <div class="mt-2 text-gray-600">
                > Job initialized at {{ formatDate(job.created_at) }}<br>
                > Status: <span class="text-[var(--win-accent)]">{{ job.status.toUpperCase() }}</span><br>
                <span v-if="job.completed_at">> Completed at {{ formatDate(job.completed_at) }} <span class="text-emerald-400">✓ Success</span></span>
             </div>
          </div>
       </div>

    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth'
})

const route = useRoute()
const { getJob } = useApi()
const { getJobProgress } = useWebSocket()

const job = ref<any>(null)
const loading = ref(true)
const error = ref<string | null>(null)

// Realtime Computed
const realtimeJob = computed(() => {
   if (!job.value) return null
   return getJobProgress(job.value.id)
})

const progressPercent = computed(() => {
   if (realtimeJob.value) return realtimeJob.value.progress_percent
   return job.value?.progress_percent || 0
})

const realtimeCopiedBytes = computed(() => {
   if (realtimeJob.value) return realtimeJob.value.copied_size_bytes
   return job.value?.copied_size_bytes || 0
})

const loadJob = async () => {
   loading.value = true
   try {
      // @ts-ignore
      job.value = await getJob(parseInt(route.params.id as string))
   } catch (e: any) {
      error.value = e.message || 'Failed to fetch job'
   } finally {
      loading.value = false
   }
}

onMounted(() => {
   loadJob()
})

// Utils
const formatSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
}

const formatDate = (dateString: string) => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleString()
}

const getStatusClass = (status: string) => {
  switch (status) {
    case 'completed': return 'text-[#6cc173] border-[#6cc173]/30 bg-[#6cc173]/10'
    case 'failed': return 'text-[#ff4d4f] border-[#ff4d4f]/30 bg-[#ff4d4f]/10'
    case 'processing': return 'text-[#60cdff] border-[#60cdff]/30 bg-[#60cdff]/10 animate-pulse'
    default: return 'text-gray-400 border-gray-600/30'
  }
}
</script>
