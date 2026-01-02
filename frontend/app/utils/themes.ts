export interface Theme {
    id: string
    name: string
    category: 'default' | 'dark' | 'light' | 'tech'
    colors: {
        text: string
        background: string
        primaryBtn: string
        secondaryBtn: string
        accent: string
    }
}

export const THEMES: Theme[] = [
    {
        id: 'default',
        name: 'Default (Aurora)',
        category: 'default',
        colors: {
            text: '#ffffff',
            background: '#0f0f0f',
            primaryBtn: '#60cdff',
            secondaryBtn: '#2a2a2a',
            accent: '#60cdff'
        }
    },

    // 🌑 The Dark Collection (Optimized)
    {
        id: 'listsync-purple',
        name: 'ListSync Purple',
        category: 'dark',
        colors: {
            text: '#ededed',
            background: '#0a0a0a',
            primaryBtn: '#9d34da',
            secondaryBtn: '#262626',
            accent: '#bd73e8'
        }
    },
    {
        id: 'obsidian-crimson',
        name: 'Obsidian Crimson',
        category: 'dark',
        colors: {
            text: '#f5f5f5',
            background: '#121212',
            primaryBtn: '#d92b2b',
            secondaryBtn: '#2c2c2c',
            accent: '#ff4d4d'
        }
    },
    {
        id: 'galactic-neon',
        name: 'Galactic Neon',
        category: 'dark',
        colors: {
            text: '#e0e0ff',
            background: '#0f0b1f',
            primaryBtn: '#5829ff',
            secondaryBtn: '#1e1a2e',
            accent: '#b95ce6'
        }
    },
    {
        id: 'retro-console',
        name: 'Retro Console',
        category: 'dark',
        colors: {
            text: '#e6ffe6',
            background: '#0d0d0d',
            primaryBtn: '#2eb82e',
            secondaryBtn: '#262626',
            accent: '#ffaa33'
        }
    },
    {
        id: 'abyssal-cyan',
        name: 'Abyssal Cyan',
        category: 'dark',
        colors: {
            text: '#e0f7fa',
            background: '#080b12',
            primaryBtn: '#00e5ff',
            secondaryBtn: '#1c2533',
            accent: '#80deea'
        }
    },
    {
        id: 'deep-sea-data',
        name: 'Deep Sea Data',
        category: 'dark',
        colors: {
            text: '#f0f8ff',
            background: '#050a14',
            primaryBtn: '#00b4d8',
            secondaryBtn: '#0b2830',
            accent: '#48cae4'
        }
    },
    {
        id: 'graphite-mint',
        name: 'Graphite Mint',
        category: 'dark',
        colors: {
            text: '#e6e6e6',
            background: '#2d2d2d',
            primaryBtn: '#5e6ad2',
            secondaryBtn: '#3f4d43',
            accent: '#69f0ae'
        }
    },
    {
        id: 'midnight-launch',
        name: 'Midnight Launch',
        category: 'dark',
        colors: {
            text: '#ffffff',
            background: '#1f1f1f',
            primaryBtn: '#4c6ef5',
            secondaryBtn: '#333333',
            accent: '#dbe300'
        }
    },
    {
        id: 'code-editor',
        name: 'Code Editor',
        category: 'dark',
        colors: {
            text: '#abb2bf',
            background: '#1e2127',
            primaryBtn: '#98c379',
            secondaryBtn: '#3e4452',
            accent: '#e5c07b'
        }
    },
    {
        id: 'magma-dark',
        name: 'Magma Dark',
        category: 'dark',
        colors: {
            text: '#fafafa',
            background: '#1a1a1a',
            primaryBtn: '#ff5722',
            secondaryBtn: '#2d2d2d',
            accent: '#81c784'
        }
    },
    {
        id: 'concrete-jungle',
        name: 'Concrete Jungle',
        category: 'dark',
        colors: {
            text: '#e0e0e0',
            background: '#2b2b2b',
            primaryBtn: '#00e676',
            secondaryBtn: '#424242',
            accent: '#ffd600'
        }
    },
    {
        id: 'slate-rose',
        name: 'Slate Rose',
        category: 'dark',
        colors: {
            text: '#fff0f5',
            background: '#263238',
            primaryBtn: '#f06292',
            secondaryBtn: '#37474f',
            accent: '#f8bbd0'
        }
    },

    // ☀️ The Light Collection (Optimized)
    {
        id: 'mint-focus',
        name: 'Mint Focus',
        category: 'light',
        colors: {
            text: '#1f2937',
            background: '#ffffff',
            primaryBtn: '#10b981',
            secondaryBtn: '#ecfdf5',
            accent: '#34d399'
        }
    },
    {
        id: 'bluebird-sky',
        name: 'Bluebird Sky',
        category: 'light',
        colors: {
            text: '#0f1419',
            background: '#ffffff',
            primaryBtn: '#1d9bf0',
            secondaryBtn: '#eff3f4',
            accent: '#8ecdf7'
        }
    },
    {
        id: 'editorial-mono',
        name: 'Editorial Mono',
        category: 'light',
        colors: {
            text: '#202020',
            background: '#f9f9f9',
            primaryBtn: '#202020',
            secondaryBtn: '#e0e0e0',
            accent: '#f5a623'
        }
    },
    {
        id: 'indigo-video',
        name: 'Indigo Video',
        category: 'light',
        colors: {
            text: '#2b1c50',
            background: '#ffffff',
            primaryBtn: '#625aff',
            secondaryBtn: '#ebeaff',
            accent: '#b2a7f0'
        }
    },
    {
        id: 'huddle-up',
        name: 'Huddle Up',
        category: 'light',
        colors: {
            text: '#1d1c1d',
            background: '#ffffff',
            primaryBtn: '#611f69',
            secondaryBtn: '#f2ebf5',
            accent: '#e01e5a'
        }
    },
    {
        id: 'berry-cream',
        name: 'Berry Cream',
        category: 'light',
        colors: {
            text: '#4a3b32',
            background: '#f5f2f0',
            primaryBtn: '#d81b60',
            secondaryBtn: '#fce4ec',
            accent: '#880e4f'
        }
    },
    {
        id: 'mystic-lavender',
        name: 'Mystic Lavender',
        category: 'light',
        colors: {
            text: '#2e235e',
            background: '#fff5f8',
            primaryBtn: '#7b68ee',
            secondaryBtn: '#f3e5f5',
            accent: '#ba68c8'
        }
    },
    {
        id: 'iris-day',
        name: 'Iris Day',
        category: 'light',
        colors: {
            text: '#311b92',
            background: '#ffffff',
            primaryBtn: '#651fff',
            secondaryBtn: '#ede7f6',
            accent: '#b388ff'
        }
    },
    {
        id: 'warm-rose',
        name: 'Warm Rose',
        category: 'light',
        colors: {
            text: '#5d4037',
            background: '#fff8f5',
            primaryBtn: '#d84315',
            secondaryBtn: '#fbe9e7',
            accent: '#ff8a65'
        }
    },
    {
        id: 'dusty-pink',
        name: 'Dusty Pink',
        category: 'light',
        colors: {
            text: '#37474f',
            background: '#ffffff',
            primaryBtn: '#bc6c76',
            secondaryBtn: '#eceff1',
            accent: '#dbaeb5'
        }
    },
    {
        id: 'golden-hour',
        name: 'Golden Hour',
        category: 'light',
        colors: {
            text: '#212121',
            background: '#ffffff',
            primaryBtn: '#f44336',
            secondaryBtn: '#fff8e1',
            accent: '#fbc02d'
        }
    },
    {
        id: 'clean-mint',
        name: 'Clean Mint',
        category: 'light',
        colors: {
            text: '#212121',
            background: '#fafafa',
            primaryBtn: '#80cbc4',
            secondaryBtn: '#f5f5f5',
            accent: '#ffab91'
        }
    },

    // 🌐 The Big Tech Collection (Optimized)
    {
        id: 'broadcast-red',
        name: 'Broadcast Red',
        category: 'tech',
        colors: {
            text: '#f9f9f9',
            background: '#0f0f0f',
            primaryBtn: '#cc0000',
            secondaryBtn: '#272727',
            accent: '#3ea6ff'
        }
    },
    {
        id: 'streamer-purple',
        name: 'Streamer Purple',
        category: 'tech',
        colors: {
            text: '#efeff1',
            background: '#18181b', // Twitch
            primaryBtn: '#9146ff',
            secondaryBtn: '#2f2f35',
            accent: '#a970ff'
        }
    },
    {
        id: 'developer-dim',
        name: 'Developer Dim',
        category: 'tech',
        colors: {
            text: '#c9d1d9',
            background: '#0d1117', // GitHub
            primaryBtn: '#238636',
            secondaryBtn: '#21262d',
            accent: '#58a6ff'
        }
    },
    {
        id: 'social-chat',
        name: 'Social Chat',
        category: 'tech',
        colors: {
            text: '#dbdee1',
            background: '#313338', // Discord
            primaryBtn: '#5865f2',
            secondaryBtn: '#2b2d31',
            accent: '#23a559'
        }
    },
    {
        id: 'audio-wave',
        name: 'Audio Wave',
        category: 'tech',
        colors: {
            text: '#ffffff',
            background: '#121212', // Spotify
            primaryBtn: '#1db954',
            secondaryBtn: '#282828',
            accent: '#1ed760'
        }
    },
    {
        id: 'cinematic-chill',
        name: 'Cinematic Chill',
        category: 'tech',
        colors: {
            text: '#e5e5e5',
            background: '#141414', // Netflix
            primaryBtn: '#e50914',
            secondaryBtn: '#333333',
            accent: '#f40612'
        }
    },
    {
        id: 'issue-tracker',
        name: 'Issue Tracker',
        category: 'tech',
        colors: {
            text: '#eeeeee',
            background: '#0f1012', // Linear
            primaryBtn: '#5e6ad2',
            secondaryBtn: '#222326',
            accent: '#7e86e6'
        }
    },
    {
        id: 'host-coral',
        name: 'Host Coral',
        category: 'tech',
        colors: {
            text: '#222222',
            background: '#ffffff', // Airbnb
            primaryBtn: '#ff385c',
            secondaryBtn: '#f7f7f7',
            accent: '#008489'
        }
    },
    {
        id: 'language-bird',
        name: 'Language Bird',
        category: 'tech',
        colors: {
            text: '#3c3c3c',
            background: '#ffffff', // Duolingo
            primaryBtn: '#58cc02',
            secondaryBtn: '#e5e5e5',
            accent: '#1cb0f6'
        }
    },
    {
        id: 'cloud-payment',
        name: 'Cloud Payment',
        category: 'tech',
        colors: {
            text: '#0a2540',
            background: '#f6f9fc', // Stripe
            primaryBtn: '#635bff',
            secondaryBtn: '#ffffff',
            accent: '#00d4ff'
        }
    },
    {
        id: 'board-master',
        name: 'Board Master',
        category: 'tech',
        colors: {
            text: '#172b4d',
            background: '#f4f5f7', // Trello
            primaryBtn: '#0079bf',
            secondaryBtn: '#eaecf0',
            accent: '#eb5a46'
        }
    },
    {
        id: 'pin-board',
        name: 'Pin Board',
        category: 'tech',
        colors: {
            text: '#111111',
            background: '#ffffff', // Pinterest
            primaryBtn: '#e60023',
            secondaryBtn: '#efefef',
            accent: '#0074e8'
        }
    }
]
