
<template>
    <!-- Loading Shimmer State -->
    <div v-if="loading" class="animate-in fade-in duration-500">
       <!-- Header Shimmer -->
       <div class="flex justify-between items-center mb-8 border-b border-white/5 pb-6">
          <div class="space-y-2">
             <div class="h-8 w-48 rounded-lg bg-[var(--glass-level-1-bg)] shimmer-bg"></div>
             <div class="h-4 w-32 rounded bg-[var(--glass-level-1-bg)] shimmer-bg"></div>
          </div>
          <div class="h-8 w-32 rounded bg-[var(--glass-level-1-bg)] shimmer-bg"></div>
       </div>

       <!-- Stats Shimmer -->
       <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div v-for="i in 3" :key="i" class="glass-panel p-6 flex items-center gap-5">
             <div class="w-16 h-16 rounded-2xl bg-[var(--glass-level-1-bg)] shimmer-bg"></div>
             <div class="space-y-3">
                <div class="h-8 w-24 rounded bg-[var(--glass-level-1-bg)] shimmer-bg"></div>
                <div class="h-3 w-20 rounded bg-[var(--glass-level-1-bg)] shimmer-bg"></div>
             </div>
          </div>
       </div>

        <!-- Content Grid Shimmer -->
        <div class="space-y-8">
        <!-- Middle Monitors Shimmer -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
           <div class="lg:col-span-2 glass-panel p-6 h-48 w-full bg-[var(--glass-level-1-bg)] shimmer-bg"></div>
           <div class="glass-panel p-6 h-48 w-full bg-[var(--glass-level-1-bg)] shimmer-bg"></div>
        </div>

            <!-- Bottom Content Shimmer -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
               <div class="lg:col-span-2 space-y-4">
                  <div class="h-6 w-40 rounded bg-[var(--glass-level-1-bg)] shimmer-bg mb-4"></div>
                  <!-- Updated height to match new CopyJobCard -->
                  <div v-for="i in 4" :key="i" class="glass-panel p-0 h-[140px] w-full bg-[var(--glass-level-1-bg)] shimmer-bg rounded-xl"></div>
               </div>
               <div class="space-y-6">
                  <div class="h-6 w-32 rounded bg-[var(--glass-level-1-bg)] shimmer-bg"></div>
                  <div class="space-y-4">
                     <div v-for="i in 3" :key="i" class="glass-panel p-5 h-20 w-full bg-[var(--glass-level-1-bg)] shimmer-bg"></div>
                  </div>
               </div>
            </div>
        </div>
    </div>

    <div v-else class="space-y-6 animate-in fade-in duration-500">
    <!-- Header -->
    <div class="page-header flex items-center justify-between">
      <div>
        <h1 class="page-header-title flex items-center gap-3">
          <UIcon name="i-heroicons-chart-bar-square" class="page-header-icon" />
          Dashboard
        </h1>
        <p class="page-header-subtitle">System Overview & Activity</p>
      </div>
      
      <!-- Global Controls -->
      <div class="flex items-center gap-3">
         
      </div>
    </div>

    <!-- Main Dashboard Grid -->
    <div class="space-y-6">
        
        <!-- Top Row: Stats & System Monitor -->
        <div class="grid grid-cols-1 xl:grid-cols-3 gap-6 items-stretch">
            
            <!-- Quick Stats (Left, 2 cols wide on XL) -->
            <div class="xl:col-span-2 flex flex-col">
                <div class="space-y-4 flex flex-col h-full">
                <h2 class="text-sm font-bold text-[var(--win-text-muted)] uppercase tracking-widest flex items-center gap-2">
                    <UIcon name="i-heroicons-chart-pie" class="w-4 h-4" />
                    Activity Overview
                </h2>
                
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 flex-grow">
                  <!-- Active Jobs (Large) -->
                  <div 
                    class="glass-panel-interactive p-6 md:p-8 flex flex-col justify-center items-center text-center gap-6 group relative overflow-hidden transition-all duration-500 h-full" 
                    @click="navigateTo('/queue')"
                    :class="activeJobs > 0 ? 'bg-[var(--brand-1)]/10 border-[var(--brand-1)]/20 shadow-[0_0_30px_rgba(96,205,255,0.15)]' : ''"
                  >
                    <!-- Highlight -->
                    <div v-if="activeJobs > 0" class="absolute left-0 top-0 right-0 h-1 bg-[var(--brand-1)]"></div>
                    <div class="relative z-10 w-20 h-20 rounded-2xl bg-gradient-to-br from-[var(--brand-1)]/40 to-[var(--brand-5)]/40 flex items-center justify-center border border-[var(--brand-1)]/30 shadow-[0_0_20px_rgba(96,205,255,0.2)] group-hover:shadow-[0_0_40px_rgba(96,205,255,0.4)] transition-all duration-300">
                      <UIcon name="i-heroicons-arrow-path" class="w-10 h-10 text-[var(--brand-1)] group-hover:animate-spin" :class="activeJobs > 0 ? 'animate-spin-slow' : ''" />
                    </div>
                    <div class="relative z-10">
                       <div class="text-4xl font-black text-[var(--win-text-primary)] tracking-tight mb-1">{{ activeJobs }}</div>
                       <div class="text-xs text-[var(--brand-1)] uppercase tracking-[0.2em] font-black">Active Jobs</div>
                    </div>
                  </div>

                  <!-- Completed (Large) -->
                  <div class="glass-panel-interactive p-6 md:p-8 flex flex-col justify-center items-center text-center gap-6 group h-full" @click="navigateTo('/history')">
                    <div class="w-20 h-20 rounded-2xl bg-gradient-to-br from-emerald-900/40 to-green-900/40 flex items-center justify-center border border-emerald-500/30 shadow-[0_0_20px_rgba(16,185,129,0.2)] group-hover:shadow-[0_0_40px_rgba(16,185,129,0.4)] transition-all duration-300">
                      <UIcon name="i-heroicons-check" class="w-10 h-10 text-[var(--status-success)]" />
                    </div>
                    <div>
                       <div class="text-4xl font-black text-[var(--win-text-primary)] tracking-tight mb-1">{{ completedToday }}</div>
                       <div class="text-xs text-[var(--status-success)] uppercase tracking-[0.2em] font-black">Completed Today</div>
                    </div>
                  </div>

                  <!-- Failed (Large) -->
                  <div class="glass-panel-interactive p-6 md:p-8 flex flex-col justify-center items-center text-center gap-6 group h-full" @click="navigateTo('/history')">
                    <div class="w-20 h-20 rounded-2xl bg-gradient-to-br from-red-900/40 to-rose-900/40 flex items-center justify-center border border-red-500/30 shadow-[0_0_20px_rgba(244,63,94,0.2)] group-hover:shadow-[0_0_40px_rgba(244,63,94,0.4)] transition-all duration-300">
                      <UIcon name="i-heroicons-x-mark" class="w-10 h-10 text-[var(--status-error)]" />
                    </div>
                    <div>
                       <div class="text-4xl font-black text-[var(--win-text-primary)] tracking-tight mb-1">{{ failedToday }}</div>
                       <div class="text-xs text-[var(--status-error)] uppercase tracking-[0.2em] font-black">Failed Today</div>
                    </div>
                  </div>
                </div>
            </div>
        </div>

            <div class="flex flex-col">
                <div class="space-y-4 flex flex-col h-full">
                    <h2 class="text-sm font-bold text-[var(--win-text-muted)] uppercase tracking-widest flex items-center gap-2">
                        <UIcon name="i-heroicons-server" class="w-4 h-4" />
                        System Status
                    </h2>
                    <SystemMonitorWidget 
                        :system-status="systemStatus" 
                        :disk-usage="diskUsage" 
                        class="flex-grow h-full"
                    />
                </div>
            </div>
        </div>


        <!-- Bottom Row: Recent Activity (Taking more space) & Stats -->
        <div class="grid grid-cols-1 xl:grid-cols-3 gap-6 items-stretch">
           <!-- Recent Activity (2 Cols) -->
           <div class="xl:col-span-2 flex flex-col">
              <div class="space-y-4 flex flex-col h-full">
              <div class="flex items-center justify-between">
                  <h2 class="text-sm font-bold text-[var(--win-text-muted)] uppercase tracking-widest flex items-center gap-2">
                      <UIcon name="i-heroicons-clock" class="w-4 h-4" />
                      Recent Activity
                  </h2>
                  <button @click="navigateTo('/history')" class="text-xs text-[var(--win-accent)] hover:text-[var(--win-text-primary)] transition-colors">View All</button>
              </div>
              
              <div v-if="recentJobs.length > 0" class="space-y-3">
                <CopyJobCard 
                  v-for="job in recentJobs" 
                  :key="job.id" 
                  :job="job" 
                  :show-actions="false"
                  class="animate-in"
                  @click="handleJobClick"
                />
              </div>
              
              <div v-else class="glass-panel-static p-12 flex flex-col items-center justify-center text-center text-[var(--win-text-muted)] border-dashed border-white/10 bg-[var(--glass-level-1-bg)] flex-grow">
                <UIcon name="i-heroicons-clipboard-document-list" class="w-12 h-12 mb-4 opacity-20" />
                <p class="text-sm font-medium text-[var(--win-text-muted)] mb-1">No recent activity</p>
                <div class="flex gap-3 mt-4">
                    <button @click="navigateTo('/copy')" class="btn-primary text-xs px-4 py-2">
                        Start Transfer
                    </button>
                </div>
              </div>
              
              <!-- If we have jobs, we might want a container that grows or has fixed min height -->
              <div v-if="recentJobs.length > 0" class="flex-grow"></div>
           </div>
           </div>

           <!-- Transfer Stats Graph (1 Col) -->
           <div class="flex flex-col">
              <div class="space-y-4 flex flex-col h-full">
                  <h2 class="text-sm font-bold text-[var(--win-text-muted)] uppercase tracking-widest flex items-center gap-2">
                      <UIcon name="i-heroicons-presentation-chart-line" class="w-4 h-4" />
                      Performance
                  </h2>
                  <StatsWidget :stats="transferStats" class="flex-grow h-full" />
              </div>
           </div>
        </div>

    </div>

    <!-- Details Modal -->
    <JobDetailsModal 
        :job="selectedJob" 
        :show="!!selectedJob" 
        @close="selectedJob = null"
        @cancel="handleCancelJob"
        @retry="handleRetryJob"
    />
  </div>
</template>

<script setup lang="ts">
import CopyJobCard from '~/components/CopyJobCard.vue'
import JobDetailsModal from '~/components/JobDetailsModal.vue'
import SystemMonitorWidget from '~/components/SystemMonitorWidget.vue'
import StatsWidget from '~/components/StatsWidget.vue'

definePageMeta({
  middleware: 'auth'
})

const { getQueue, getHistory, getSystemStatus, getDiskUsage, getTransferStats, cancelJob, retryJob } = useApi()

const activeJobs = ref(0)
const completedToday = ref(0)
const failedToday = ref(0)
const recentJobs = ref<any[]>([])
const systemStatus = ref<any>(null)
const diskUsage = ref<any>(null)
const transferStats = ref<any>(null)

const selectedJob = ref<any>(null)

const loading = ref(true)

const loadData = async () => {
  try {
    const [queue, history, status, disk, stats] = await Promise.all([
      getQueue(),
      getHistory(10, 0),
      getSystemStatus(),
      getDiskUsage(),
      getTransferStats()
    ])
    
    activeJobs.value = queue.length
    recentJobs.value = history.slice(0, 5) // Expanded to 5 as per plan
    systemStatus.value = status
    diskUsage.value = disk
    transferStats.value = stats
    
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    
    completedToday.value = history.filter(job => 
      job.status === 'completed' && new Date(job.created_at) >= today
    ).length
    
    failedToday.value = history.filter(job => 
      job.status === 'failed' && new Date(job.created_at) >= today
    ).length
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  } finally {
    loading.value = false
  }
}

const formatRelativeInfo = (dateString: string) => {
  if (!dateString) return ''
  const now = new Date()
  const then = new Date(dateString)
  const diffInSeconds = Math.floor((now.getTime() - then.getTime()) / 1000)

  if (diffInSeconds < 60) return 'just now'
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`
  return `${Math.floor(diffInSeconds / 3600)}h ago`
}



const handleJobClick = (job: any) => {
    selectedJob.value = job
}

const handleCancelJob = async (id: number) => {
    try {
        await cancelJob(id)
        selectedJob.value = null
        loadData()
    } catch(e) {
        console.error(e)
    }
}

const handleRetryJob = async (id: number) => {
    try {
        await retryJob(id)
        selectedJob.value = null
        loadData()
    } catch(e) {
        console.error(e)
    }
}

onMounted(() => {
  loadData()
})

useIntervalFn(loadData, 5000)
</script>

<style scoped>
.animate-spin-slow {
  animation: spin 4s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.2; }
  50% { opacity: 0.4; }
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.animate-shimmer-slow {
  animation: shimmer 3s infinite linear;
}
</style>

