export default defineAppConfig({
    ui: {
        primary: 'brand',
        gray: 'neutral',
        card: {
            base: 'glass-panel transition-all duration-300',
            background: 'bg-transparent',
            divide: 'divide-white/10',
            ring: 'ring-1 ring-white/10',
            shadow: 'shadow-none',
            body: {
                base: 'text-[var(--win-text-primary)]'
            },
            header: {
                base: 'border-b border-white/10'
            }
        },
        button: {
            rounded: 'rounded-lg',
            font: 'font-semibold',
            default: {
                size: 'md'
            }
        },
        input: {
            rounded: 'rounded-lg',
            base: 'bg-[var(--glass-level-1-bg)] border-white/10 text-[var(--win-text-primary)] focus:ring-cyan-500 focus:border-cyan-500 placeholder-[var(--win-text-muted)]'
        }
    }
})
