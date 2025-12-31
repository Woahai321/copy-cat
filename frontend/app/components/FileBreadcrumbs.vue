<template>
  <div class="flex items-center gap-1 overflow-x-auto no-scrollbar mask-gradient-right">
    <button 
        @click="$emit('navigate', '/')"
        class="p-1.5 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
        title="Root"
    >
        <UIcon name="i-heroicons-home" class="w-4 h-4" />
    </button>
    
    <template v-for="(segment, index) in segments" :key="index">
        <UIcon name="i-heroicons-chevron-right" class="w-3 h-3 text-gray-600 flex-shrink-0" />
        <button 
            @click="handleClick(index)"
            class="px-2 py-1 rounded-md text-xs font-medium whitespace-nowrap transition-colors border border-transparent"
            :class="index === segments.length - 1 ? 'bg-[var(--win-accent)]/10 text-[var(--win-accent)] border-[var(--win-accent)]/20 font-bold' : 'text-gray-400 hover:text-white hover:bg-white/5'"
        >
            {{ segment }}
        </button>
    </template>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
    currentPath: string
}>()

const emit = defineEmits<{
    navigate: [path: string]
}>()

const segments = computed(() => {
    return props.currentPath.split('/').filter(Boolean)
})

const handleClick = (index: number) => {
    // Reconstruct path up to index
    const newPath = '/' + segments.value.slice(0, index + 1).join('/')
    emit('navigate', newPath)
}
</script>

<style scoped>
.mask-gradient-right {
    mask-image: linear-gradient(to right, black 90%, transparent 100%);
}
</style>
