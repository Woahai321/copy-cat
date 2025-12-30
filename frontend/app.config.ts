export default defineAppConfig({
    ui: {
        primary: 'cyan',
        gray: 'neutral',
        card: {
            base: 'glass-panel transition-all duration-300',
            background: 'bg-transparent',
            divide: 'divide-white/10',
            ring: 'ring-1 ring-white/10',
            shadow: 'shadow-none',
            body: {
                base: 'text-white'
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
            base: 'bg-white/5 border-white/10 text-white focus:ring-cyan-500 focus:border-cyan-500 placeholder-white/30'
        }
    }
})
