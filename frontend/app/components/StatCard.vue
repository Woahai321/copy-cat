<template>
  <div class="card card-interactive touch-target" @click="handleClick">
    <div class="p-4 sm:p-6">
      <div class="flex items-center justify-between mb-3 sm:mb-4">
        <div class="w-10 h-10 sm:w-12 sm:h-12 rounded-lg flex items-center justify-center flex-shrink-0" :class="iconBgClass">
          <UIcon :name="icon" class="w-5 h-5 sm:w-6 sm:h-6" :class="iconColorClass" />
        </div>
        <UBadge v-if="badge" :color="badgeColor" variant="soft" size="sm">
          {{ badge }}
        </UBadge>
      </div>
      
      <div class="mb-2">
        <div class="text-3xl sm:text-4xl font-bold text-[var(--win-text-primary)] mb-1">
          {{ value }}
        </div>
        <div class="text-sm font-medium text-[var(--win-text-muted)]">
          {{ label }}
        </div>
      </div>
      
      <div v-if="description" class="text-xs text-[var(--win-text-muted)]">
        {{ description }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  icon: string
  value: string | number
  label: string
  description?: string
  badge?: string
  badgeColor?: 'cyan' | 'green' | 'red' | 'gray'
  variant?: 'primary' | 'success' | 'danger' | 'warning' | 'default'
  to?: string
}

const props = withDefaults(defineProps<Props>(), {
  badgeColor: 'cyan',
  variant: 'primary'
})

const emit = defineEmits<{
  click: []
}>()

const iconBgClass = computed(() => {
  switch (props.variant) {
    case 'primary':
      return 'bg-[var(--win-accent)]/10'
    case 'success':
      return 'bg-[var(--status-success)]/10'
    case 'danger':
      return 'bg-[var(--status-error)]/10'
    case 'warning':
      return 'bg-[var(--brand-1)]/10'
    default:
      return 'bg-[var(--glass-level-2-bg)]'
  }
})

const iconColorClass = computed(() => {
  switch (props.variant) {
    case 'primary':
      return 'text-[var(--win-accent)]'
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

