<template>
  <div class="space-y-12">
    
    <!-- Default / Current -->
    <div v-if="defaultThemes.length > 0" class="space-y-6">
        <div class="flex items-center gap-3 pb-2 border-b border-white/5">
            <div class="p-2 rounded-lg bg-white/5">
              <UIcon name="i-heroicons-sparkles" class="w-5 h-5 text-[var(--win-accent)]" />
            </div>
            <h3 class="text-lg font-bold text-[var(--win-text-primary)]">Default</h3>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            <SettingsThemeCard v-for="theme in defaultThemes" :key="theme.id" :theme="theme" :is-active="currentTheme?.id === theme.id" @select="setTheme(theme)" />
        </div>
    </div>

    <!-- Dark Collection -->
    <div v-if="darkThemes.length > 0" class="space-y-6">
      <div class="flex items-center gap-3 pb-2 border-b border-white/5">
        <div class="p-2 rounded-lg bg-white/5">
          <UIcon name="i-heroicons-moon" class="w-5 h-5 text-[var(--win-accent)]" />
        </div>
        <h3 class="text-lg font-bold text-[var(--win-text-primary)]">The Dark Collection</h3>
        <span class="text-xs font-mono text-[var(--win-text-muted)] bg-white/5 px-2 py-0.5 rounded-full">{{ darkThemes.length }}</span>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <SettingsThemeCard v-for="theme in darkThemes" :key="theme.id" :theme="theme" :is-active="currentTheme?.id === theme.id" @select="setTheme(theme)" />
      </div>
    </div>

    <!-- Big Tech Collection -->
    <div v-if="techThemes.length > 0" class="space-y-6">
      <div class="flex items-center gap-3 pb-2 border-b border-white/5">
        <div class="p-2 rounded-lg bg-white/5">
           <UIcon name="i-heroicons-globe-alt" class="w-5 h-5 text-[var(--win-accent)]" />
        </div>
        <h3 class="text-lg font-bold text-[var(--win-text-primary)]">The Big Tech Collection</h3>
        <span class="text-xs font-mono text-[var(--win-text-muted)] bg-white/5 px-2 py-0.5 rounded-full">{{ techThemes.length }}</span>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <SettingsThemeCard v-for="theme in techThemes" :key="theme.id" :theme="theme" :is-active="currentTheme?.id === theme.id" @select="setTheme(theme)" />
      </div>
    </div>

    <!-- Light Collection -->
    <div v-if="lightThemes.length > 0" class="space-y-6">
      <div class="flex items-center gap-3 pb-2 border-b border-white/5">
        <div class="p-2 rounded-lg bg-white/5">
           <UIcon name="i-heroicons-sun" class="w-5 h-5 text-[var(--win-accent)]" />
        </div>
        <h3 class="text-lg font-bold text-[var(--win-text-primary)]">The Light Collection</h3>
        <span class="text-xs font-mono text-[var(--win-text-muted)] bg-white/5 px-2 py-0.5 rounded-full">{{ lightThemes.length }}</span>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <SettingsThemeCard v-for="theme in lightThemes" :key="theme.id" :theme="theme" :is-active="currentTheme?.id === theme.id" @select="setTheme(theme)" />
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const { themes, currentTheme, setTheme } = useTheme()

const defaultThemes = computed(() => themes.filter(t => t.category === 'default'))
const darkThemes = computed(() => themes.filter(t => t.category === 'dark'))
const lightThemes = computed(() => themes.filter(t => t.category === 'light'))
const techThemes = computed(() => themes.filter(t => t.category === 'tech'))
</script>
