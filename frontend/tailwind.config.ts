import type { Config } from 'tailwindcss'

export default <Config>{
    theme: {
        extend: {
            colors: {
                brand: {
                    50: 'color-mix(in srgb, var(--brand-1), white 90%)',
                    100: 'color-mix(in srgb, var(--brand-1), white 80%)',
                    200: 'color-mix(in srgb, var(--brand-1), white 60%)',
                    300: 'color-mix(in srgb, var(--brand-1), white 40%)',
                    400: 'color-mix(in srgb, var(--brand-1), white 20%)',
                    500: 'var(--brand-1)',
                    600: 'color-mix(in srgb, var(--brand-1), black 10%)',
                    700: 'color-mix(in srgb, var(--brand-1), black 30%)',
                    800: 'color-mix(in srgb, var(--brand-1), black 50%)',
                    900: 'color-mix(in srgb, var(--brand-1), black 70%)',
                    950: 'color-mix(in srgb, var(--brand-1), black 85%)',
                }
            }
        }
    }
}
