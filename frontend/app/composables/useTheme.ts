import { ref } from 'vue'
import { type Theme, THEMES } from '../utils/themes'

const currentTheme = ref<Theme>(THEMES[0]!)

export const useTheme = () => {
    const applyTheme = (theme: Theme) => {
        const root = document.documentElement

        // Set CSS variables
        root.style.setProperty('--win-bg-base', theme.colors.background)
        root.style.setProperty('--win-text-primary', theme.colors.text)
        root.style.setProperty('--win-accent', theme.colors.accent)
        root.style.setProperty('--brand-1', theme.colors.primaryBtn)

        // Derived colors logic would ideally be in CSS color-mix, but we set base vars here
        // We can also set specific button variables if we create them in main.css
        root.style.setProperty('--theme-btn-secondary-bg', theme.colors.secondaryBtn)

        // Update state
        currentTheme.value = theme

        // Persist
        if (import.meta.client) {
            localStorage.setItem('copycat-theme-id', theme.id)
        }
    }

    const initTheme = () => {
        if (import.meta.client) {
            const savedId = localStorage.getItem('copycat-theme-id')
            if (savedId) {
                const found = THEMES.find(t => t.id === savedId)
                if (found) {
                    applyTheme(found)
                    return
                }
            }
            // Apply default if no saved theme
            applyTheme(THEMES[0]!)
        }
    }

    return {
        currentTheme,
        themes: THEMES,
        setTheme: applyTheme,
        initTheme
    }
}
