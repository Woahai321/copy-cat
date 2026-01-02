<template>
  <button
    @click="$emit('select', theme)"
    class="group relative flex flex-col gap-4 text-left transition-all duration-500 transform rounded-[2rem] p-3 border"
    :class="[
      isActive 
        ? 'bg-[var(--glass-level-2-bg)] border-[var(--win-accent)] scale-[1.02] shadow-[0_20px_40px_-10px_rgba(0,0,0,0.5)]' 
        : 'bg-[var(--glass-level-1-bg)] border-white/5 hover:bg-[var(--glass-level-2-bg)] hover:border-white/10 hover:-translate-y-2 hover:shadow-2xl'
    ]"
  >
    <!-- Mini App Preview Container -->
    <div 
      class="w-full aspect-[16/10] rounded-2xl overflow-hidden relative shadow-inner isolate transition-all duration-500"
      :style="{ backgroundColor: theme.colors.background }"
    >
      <!-- Dynamic Background Elements -->
      <div class="absolute inset-0 opacity-20" :style="{ 
          backgroundImage: `linear-gradient(to right, ${theme.colors.accent}10 1px, transparent 1px)`,
          backgroundSize: '20px 100%' 
      }"></div>

       <!-- Glow Orb -->
      <div 
         class="absolute -top-10 -right-10 w-40 h-40 blur-3xl opacity-30 rounded-full transition-transform duration-700 group-hover:scale-110"
         :style="{ backgroundColor: theme.colors.accent }"
      ></div>

      <!-- Mini Interface Layout -->
      <div class="absolute inset-2 flex gap-2">
          <!-- Sidebar -->
          <div class="w-1/4 h-full rounded-xl flex flex-col gap-1.5 p-1.5 backdrop-blur-sm" :style="{ backgroundColor: theme.colors.secondaryBtn + '20' }">
              <!-- Brand -->
              <div class="h-1.5 w-1/2 rounded-full mb-1 opacity-80" :style="{ backgroundColor: theme.colors.text }"></div>
              
              <!-- Nav Items -->
              <div class="h-1 w-full rounded-full opacity-30" :style="{ backgroundColor: theme.colors.text }"></div>
              <div class="h-1 w-3/4 rounded-full opacity-30" :style="{ backgroundColor: theme.colors.text }"></div>
              <div class="mt-auto h-3 w-8 rounded-md opacity-20" :style="{ backgroundColor: theme.colors.text }"></div>
          </div>

          <!-- Main Content Area -->
          <div class="flex-1 flex flex-col gap-2">
              <!-- Header -->
              <div class="h-6 rounded-xl border flex items-center px-2" :style="{ borderColor: theme.colors.text + '10', backgroundColor: theme.colors.background }">
                   <div class="h-1.5 w-1/3 rounded-full opacity-90" :style="{ backgroundColor: theme.colors.text }"></div>
              </div>

              <!-- Grid Content -->
              <div class="flex-1 grid grid-cols-2 gap-1.5">
                  <!-- Mini Card 1 (Active/Primary) -->
                  <div class="rounded-lg p-1.5 border flex flex-col justify-end relative overflow-hidden" 
                       :style="{ 
                           backgroundColor: theme.colors.secondaryBtn + '40',
                           borderColor: theme.colors.accent + '30'
                       }">
                      <div class="h-1 w-3/4 rounded-full mb-1 opacity-90" :style="{ backgroundColor: theme.colors.text }"></div>
                      <div class="h-3 w-full rounded-md mt-1 flex items-center justify-center text-[4px] font-bold shadow-lg" 
                           :style="{ backgroundColor: theme.colors.primaryBtn, color: theme.colors.background }">
                           Action
                      </div>
                  </div>

                  <!-- Mini Card 2 (Secondary) -->
                  <div class="rounded-lg p-1.5 border flex flex-col justify-end" 
                       :style="{ 
                           backgroundColor: theme.colors.secondaryBtn + '10',
                           borderColor: theme.colors.text + '05'
                       }">
                       <div class="h-1 w-1/2 rounded-full mb-1 opacity-50" :style="{ backgroundColor: theme.colors.text }"></div>
                       <div class="h-3 w-8 rounded-md mt-1 opacity-10" :style="{ backgroundColor: theme.colors.text }"></div>
                  </div>
              </div>
          </div>
      </div>
    </div>

    <!-- Theme Label & Selection Indicator -->
    <div class="w-full flex items-center justify-between px-2 pb-1">
      <div class="flex flex-col">
          <span class="font-bold text-sm tracking-wide text-[var(--win-text-primary)] group-hover:text-[var(--win-accent)] transition-colors">{{ theme.name }}</span>

      </div>
      
      <div class="relative">
          <div 
            class="w-6 h-6 rounded-full border-2 transition-all duration-300 flex items-center justify-center"
            :class="isActive 
              ? 'bg-[var(--win-accent)] border-[var(--win-accent)] shadow-[0_0_15px_var(--win-accent)] scale-110' 
              : 'border-[var(--win-text-muted)] group-hover:border-[var(--win-text-primary)] scale-100'"
          >
            <UIcon v-if="isActive" name="i-heroicons-check" class="w-3.5 h-3.5 text-[var(--win-bg-base)]" />
          </div>
      </div>
    </div>
  </button>
</template>

<script setup lang="ts">
import type { Theme } from '@/utils/themes'

defineProps<{
  theme: Theme
  isActive: boolean
}>()

defineEmits<{
  (e: 'select', theme: Theme): void
}>()
</script>
