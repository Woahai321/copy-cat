<template>
  <div class="card card-interactive touch-target" @click="handleClick">
    <div class="p-4 sm:p-6">
      <div class="flex items-start gap-3 sm:gap-4">
        <div class="w-12 h-12 sm:w-14 sm:h-14 rounded-xl flex items-center justify-center flex-shrink-0" :class="iconBgClass">
          <UIcon :name="icon" class="w-6 h-6 sm:w-7 sm:h-7" :class="iconColorClass" />
        </div>
        
        <div class="flex-1 min-w-0">
          <h3 class="text-base sm:text-lg font-semibold text-slate-100 mb-1 sm:mb-2">
            {{ title }}
          </h3>
          <p class="text-xs sm:text-sm text-slate-400 leading-relaxed">
            {{ description }}
          </p>
        </div>

        <UIcon name="i-heroicons-arrow-right" class="w-5 h-5 text-slate-500 flex-shrink-0 mt-1 hidden sm:block" />
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
      return 'bg-emerald-500/20'
    case 'danger':
      return 'bg-rose-500/20'
    case 'warning':
      return 'bg-[var(--brand-1)]/20'
    default:
      return 'bg-slate-700/50'
  }
})

const iconColorClass = computed(() => {
  switch (props.variant) {
    case 'primary':
      return 'text-white'
    case 'success':
      return 'text-emerald-400'
    case 'danger':
      return 'text-rose-400'
    case 'warning':
      return 'text-[var(--brand-1)]'
    default:
      return 'text-slate-400'
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

