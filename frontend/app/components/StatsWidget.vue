<template>
  <div class="glass-panel p-6 bg-black/20 h-full flex flex-col">
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-xs font-bold text-gray-500 uppercase tracking-widest flex items-center gap-2">
        <div class="w-2 h-2 rounded-full bg-[var(--brand-10)] shadow-[0_0_8px_rgba(110,72,139,0.6)] animate-pulse"></div>
        Transfer Statistics
      </h3>
      
      <!-- Tab Selector -->
      <div class="flex gap-1 bg-white/5 rounded-lg p-1 border border-white/10">
        <button 
          v-for="tab in tabs" 
          :key="tab.value"
          @click="activeTab = tab.value"
          class="px-2 py-1 text-[10px] font-bold uppercase tracking-wider rounded transition-all"
          :class="activeTab === tab.value 
            ? 'bg-[var(--win-accent)] text-black shadow-[0_0_10px_rgba(96,205,255,0.3)]' 
            : 'text-gray-500 hover:text-white hover:bg-white/5'"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>

    <div v-if="stats" class="space-y-6">
      <!-- Stats Grid -->
      <div class="grid grid-cols-2 gap-4">
        <!-- Total Transfers -->
        <div class="p-4 rounded-xl bg-white/5 border border-white/5">
          <div class="text-2xl font-bold text-white">{{ currentPeriod.count }}</div>
          <div class="text-[10px] text-gray-500 uppercase tracking-wider mt-1">Total Transfers</div>
        </div>
        
        <!-- Data Moved -->
        <div class="p-4 rounded-xl bg-white/5 border border-white/5">
          <div class="text-2xl font-bold text-[var(--win-accent)]">{{ currentPeriod.bytes_formatted }}</div>
          <div class="text-[10px] text-gray-500 uppercase tracking-wider mt-1">Data Moved</div>
        </div>
        
        <!-- Success Rate -->
        <div class="p-4 rounded-xl bg-white/5 border border-white/5">
          <div class="text-2xl font-bold" :class="getSuccessRateColor(currentPeriod.success_rate)">
            {{ currentPeriod.success_rate }}%
          </div>
          <div class="text-[10px] text-gray-500 uppercase tracking-wider mt-1">Success Rate</div>
        </div>
        
        <!-- Avg Speed -->
        <div class="p-4 rounded-xl bg-white/5 border border-white/5">
          <div class="text-2xl font-bold text-[var(--brand-10)]">{{ currentPeriod.avg_speed_formatted }}</div>
          <div class="text-[10px] text-gray-500 uppercase tracking-wider mt-1">Avg Speed</div>
        </div>
      </div>

      <!-- Mini Bar Chart (Last 7 Days) -->
      <div v-if="stats.daily_breakdown && stats.daily_breakdown.length > 0" class="pt-4 border-t border-white/5 h-[140px] flex flex-col">
        <div class="text-[10px] text-gray-500 uppercase tracking-wider mb-2">Last 7 Days</div>
        <div class="flex-1 relative w-full h-full">
            <Bar :data="chartData" :options="chartOptions" />
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-else class="space-y-4">
      <div class="grid grid-cols-2 gap-4">
        <div v-for="i in 4" :key="i" class="p-4 rounded-xl bg-white/5">
          <div class="h-6 w-16 bg-white/10 rounded shimmer-bg"></div>
          <div class="h-3 w-20 bg-white/10 rounded mt-2 shimmer-bg"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

interface PeriodStats {
  count: number
  completed: number
  failed: number
  cancelled: number
  bytes: number
  bytes_formatted: string
  avg_duration: number
  avg_speed: number
  avg_speed_formatted: string
  success_rate: number
}

interface DailyBreakdown {
  date: string
  day: string
  completed: number
  failed: number
  bytes: number
  bytes_formatted: string
}

interface TransferStats {
  today: PeriodStats
  week: PeriodStats
  month: PeriodStats
  all_time: PeriodStats
  daily_breakdown: DailyBreakdown[]
}

const props = defineProps<{
  stats: TransferStats | null
}>()

const tabs = [
  { label: 'Today', value: 'today' },
  { label: 'Week', value: 'week' },
  { label: 'Month', value: 'month' },
  { label: 'All', value: 'all_time' }
]

const activeTab = ref<'today' | 'week' | 'month' | 'all_time'>('today')

const currentPeriod = computed((): PeriodStats => {
  if (!props.stats) {
    return {
      count: 0,
      completed: 0,
      failed: 0,
      cancelled: 0,
      bytes: 0,
      bytes_formatted: '0 B',
      avg_duration: 0,
      avg_speed: 0,
      avg_speed_formatted: 'N/A',
      success_rate: 0
    }
  }
  return props.stats[activeTab.value]
})

const getSuccessRateColor = (rate: number) => {
  if (rate >= 90) return 'text-emerald-400'
  if (rate >= 70) return 'text-[var(--brand-1)]'
  return 'text-rose-400'
}

// Chart Data & Options
const chartData = computed(() => {
  const breakdown = props.stats?.daily_breakdown || []
  
  return {
    labels: breakdown.map(d => d.day),
    datasets: [
      {
        label: 'Completed',
        backgroundColor: '#10b981',
        borderRadius: 4,
        data: breakdown.map(d => d.completed)
      },
      {
        label: 'Failed',
        backgroundColor: '#f43f5e',
        borderRadius: 4,
        data: breakdown.map(d => d.failed)
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      mode: 'index',
      intersect: false,
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      titleColor: '#fff',
      bodyColor: '#fff',
      borderColor: 'rgba(255, 255, 255, 0.1)',
      borderWidth: 1
    }
  },
  scales: {
    x: {
      stacked: true,
      grid: {
        display: false
      },
      ticks: {
        color: '#9ca3af',
        font: {
          size: 10
        }
      }
    },
    y: {
      stacked: true,
      display: false,
      grid: {
        display: false
      }
    }
  }
}
</script>

