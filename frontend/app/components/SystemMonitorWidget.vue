<template>
  <div class="glass-panel p-6 bg-black/20 h-full flex flex-col">
    <h3 
      class="text-xs font-bold text-gray-500 uppercase tracking-widest mb-6 flex items-center justify-between cursor-pointer hover:text-white transition-colors"
      @click="navigateTo('/browse')"
    >
      <div class="flex items-center gap-2">
        <div class="w-2 h-2 rounded-full bg-[var(--win-accent)] shadow-[0_0_8px_rgba(96,205,255,0.6)] animate-pulse"></div>
        System Monitor
      </div>
      <span v-if="diskUsage?.zurg?.updated_at" class="text-[9px] font-medium opacity-50 lowercase">
        Updated: {{ formatRelativeInfo(diskUsage.zurg.updated_at) }}
      </span>
    </h3>

    <div class="space-y-8">
      <!-- Zurg Drive -->
      <div class="space-y-3">
        <div class="flex justify-between items-center">
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-cloud" class="w-4 h-4 text-[var(--brand-1)]" />
            <span class="text-gray-300 font-bold text-sm">Zurg (Source)</span>
            <span v-if="systemStatus?.zurg?.exists" class="text-[9px] font-bold text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">ONLINE</span>
            <span v-else class="text-[9px] font-bold text-red-400 bg-red-500/10 px-1.5 py-0.5 rounded border border-red-500/20">OFFLINE</span>
          </div>
          <div class="text-right">
            <div v-if="diskUsage?.zurg?.available" class="text-xs font-mono font-bold" :class="getUsageColor(diskUsage.zurg.percent)">
              {{ diskUsage.zurg.percent }}% Used
            </div>
          </div>
        </div>

        <div class="h-1.5 bg-white/5 rounded-full overflow-hidden border border-white/5 cursor-pointer hover:opacity-80 transition-opacity" @click="navigateTo('/browse?tab=source')">
          <div 
            v-if="diskUsage?.zurg?.available && systemStatus?.zurg?.exists"
            class="h-full transition-all duration-1000"
            :class="getBarClass(diskUsage.zurg.percent)"
            :style="{ width: `${diskUsage.zurg.percent}%` }"
          ></div>
          <div v-else-if="!systemStatus?.zurg?.exists" class="h-full w-full bg-red-500 opacity-20"></div>
        </div>

        <div class="flex items-center justify-between text-[10px] text-gray-500 font-medium px-0.5">
          <div class="flex items-center gap-3">
            <span class="flex items-center gap-1"><UIcon name="i-heroicons-document" class="w-3 h-3"/> {{ diskUsage?.zurg?.file_count || 0 }}</span>
            <span class="flex items-center gap-1"><UIcon name="i-heroicons-folder" class="w-3 h-3"/> {{ diskUsage?.zurg?.folder_count || 0 }}</span>
          </div>
          <span v-if="diskUsage?.zurg?.available">{{ diskUsage.zurg.used_formatted }} / {{ diskUsage.zurg.total_formatted }}</span>
        </div>
      </div>

      <!-- Harddrive -->
      <div class="space-y-3">
        <div class="flex justify-between items-center">
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-circle-stack" class="w-4 h-4 text-emerald-400" />
            <span class="text-gray-300 font-bold text-sm">16TB (Dest)</span>
            <span v-if="systemStatus?.harddrive?.exists" class="text-[9px] font-bold text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">ONLINE</span>
            <span v-else class="text-[9px] font-bold text-red-400 bg-red-500/10 px-1.5 py-0.5 rounded border border-red-500/20">OFFLINE</span>
          </div>
          <div class="text-right">
            <div v-if="diskUsage?.harddrive?.available" class="text-xs font-mono font-bold" :class="getUsageColor(diskUsage.harddrive.percent)">
              {{ diskUsage.harddrive.percent }}% Used
            </div>
          </div>
        </div>

        <div class="h-1.5 bg-white/5 rounded-full overflow-hidden border border-white/5 cursor-pointer hover:opacity-80 transition-opacity" @click="navigateTo('/browse?tab=destination')">
          <div 
            v-if="diskUsage?.harddrive?.available && systemStatus?.harddrive?.exists"
            class="h-full transition-all duration-1000"
            :class="getBarClass(diskUsage.harddrive.percent)"
            :style="{ width: `${diskUsage.harddrive.percent}%` }"
          ></div>
          <div v-else-if="!systemStatus?.harddrive?.exists" class="h-full w-full bg-red-500 opacity-20"></div>
        </div>

        <div class="flex items-center justify-between text-[10px] text-gray-500 font-medium px-0.5">
          <div class="flex items-center gap-3">
            <span class="flex items-center gap-1"><UIcon name="i-heroicons-document" class="w-3 h-3"/> {{ diskUsage?.harddrive?.file_count || 0 }}</span>
            <span class="flex items-center gap-1"><UIcon name="i-heroicons-folder" class="w-3 h-3"/> {{ diskUsage?.harddrive?.folder_count || 0 }}</span>
          </div>
          <span v-if="diskUsage?.harddrive?.available">{{ diskUsage.harddrive.used_formatted }} / {{ diskUsage.harddrive.total_formatted }}</span>
        </div>
      </div>
    </div>

    <!-- Warnings -->
    <div v-if="showWarning" class="mt-6 p-3 rounded-lg bg-[var(--brand-1)]/10 border border-[var(--brand-1)]/20 flex items-center gap-2">
      <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 text-[var(--brand-1)] flex-shrink-0" />
      <span class="text-[10px] text-[var(--brand-1)] leading-tight">{{ warningMessage }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  systemStatus: any
  diskUsage: any
}>()

const formatRelativeInfo = (dateString: string) => {
  if (!dateString) return ''
  const now = new Date()
  const then = new Date(dateString)
  const diffInSeconds = Math.floor((now.getTime() - then.getTime()) / 1000)
  if (diffInSeconds < 60) return 'just now'
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`
  return `${Math.floor(diffInSeconds / 3600)}h ago`
}

const getUsageColor = (percent: number) => {
  if (percent >= 90) return 'text-red-400'
  if (percent >= 70) return 'text-[var(--brand-1)]'
  return 'text-emerald-400'
}

const getBarClass = (percent: number) => {
  if (percent >= 90) return 'bg-gradient-to-r from-red-600 to-red-400 shadow-[0_0_15px_rgba(248,113,113,0.5)]'
  if (percent >= 70) return 'bg-gradient-to-r from-[var(--brand-1)] to-[var(--brand-5)] shadow-[0_0_15px_rgba(96,205,255,0.5)]'
  return 'bg-gradient-to-r from-emerald-600 to-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.5)]'
}

const showWarning = computed(() => {
  if (!props.diskUsage) return false
  return (props.diskUsage.harddrive?.available && props.diskUsage.harddrive.percent >= 85)
})

const warningMessage = computed(() => {
  if (!props.diskUsage?.harddrive) return ''
  if (props.diskUsage.harddrive.percent >= 95) return 'CRITICAL: Destination drive is almost full!'
  if (props.diskUsage.harddrive.percent >= 85) return 'WARNING: Destination drive is getting full.'
  return ''
})
</script>
