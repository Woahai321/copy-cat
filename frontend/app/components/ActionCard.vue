<template>
  <div class="card card-interactive touch-target" @click="handleClick">
    <div class="p-4 sm:p-6">
      <div class="flex items-start gap-3 sm:gap-4">
        <div class="w-12 h-12 sm:w-14 sm:h-14 rounded-xl flex items-center justify-center flex-shrink-0" :class="iconBgClass">
          <UIcon :name="icon" class="w-6 h-6 sm:w-7 sm:h-7" :class="iconColorClass" />
        </div>
        
        <div class="flex-1 min-w-0">
          <h3 class="text-base sm:text-lg font-semibold text-[var(--win-text-primary)] mb-1 sm:mb-2">
            {{ title }}
          </h3>
          <p class="text-xs sm:text-sm text-[var(--win-text-muted)] leading-relaxed">
            {{ description }}
          </p>
        </div>

        <UIcon name="i-heroicons-arrow-right" class="w-5 h-5 text-[var(--win-text-muted)] flex-shrink-0 mt-1 hidden sm:block" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  icon: string
  title: string
  description: string
  to?: string
  variant?: 'primary' | 'success' | 'danger' | 'warning' | 'default'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary'
})

const emit = defineEmits<{
  click: []
}>()

const iconBgClass = computed(() => {
  switch (props.variant) {
    case 'primary':
      return 'bg-gradient-cyan'
    case 'success':
      return 'bg-[var(--status-success)]/20'
    case 'danger':
      return 'bg-[var(--status-error)]/20'
    case 'warning':
      return 'bg-[var(--brand-1)]/20'
    default:
      return 'bg-[var(--glass-level-2-bg)]'
  }
})

const iconColorClass = computed(() => {
  switch (props.variant) {
    case 'primary':
      return 'text-[var(--win-bg-base)]'
    case 'success':
      return 'text-[var(--status-success)]'
    case 'danger':
      return 'text-[var(--status-error)]'
    case 'warning':
      return 'text-[var(--brand-1)]'
    default:
      return 'text-[var(--win-text-muted)]'
  }
})

const handleClick = () => {
  if (props.to) {
    navigateTo(props.to)
  } else {
    emit('click')
  }
}
</script>

<style scoped>
/* Card styles are in main.css */
</style>

