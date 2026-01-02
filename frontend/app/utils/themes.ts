export interface Theme {
    id: string
    name: string
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
        colors: {
            text: '#ffffff',
            background: '#0f0f0f',
            primaryBtn: '#60cdff',
            secondaryBtn: '#2a2a2a',
            accent: '#60cdff'
        }
    },
    // Part 1: Curated Styles
    {
        id: 'sandy-coastline',
        name: 'Sandy Coastline',
        colors: {
            text: '#f0ebd8',
            background: '#264653',
            primaryBtn: '#e76f51',
            secondaryBtn: '#2a9d8f',
            accent: '#e9c46a'
        }
    },
    {
        id: 'mint-focus',
        name: 'Mint Focus',
        colors: {
            text: '#0e101a',
            background: '#ffffff',
            primaryBtn: '#0d8065',
            secondaryBtn: '#f0f2fc',
            accent: '#aff2ea'
        }
    },
    {
        id: 'nautical-americana',
        name: 'Nautical Americana',
        colors: {
            text: '#1d3557',
            background: '#f1faee',
            primaryBtn: '#e63946',
            secondaryBtn: '#a8dadc',
            accent: '#7ab6d9'
        }
    },
    {
        id: 'midnight-launch',
        name: 'Midnight Launch',
        colors: {
            text: '#ffffff',
            background: '#191919',
            primaryBtn: '#405bff',
            secondaryBtn: '#212121',
            accent: '#ebff38'
        }
    },
    {
        id: 'acid-gamer',
        name: 'Acid Gamer',
        colors: {
            text: '#eeeeee',
            background: '#000000',
            primaryBtn: '#44d62c',
            secondaryBtn: '#222222',
            accent: '#ff9c07'
        }
    },
    {
        id: 'orchid-intelligence',
        name: 'Orchid Intelligence',
        colors: {
            text: '#e9ffe8',
            background: '#193718',
            primaryBtn: '#ff8bff',
            secondaryBtn: '#5eaa67',
            accent: '#ff8bff'
        }
    },
    {
        id: 'bluebird-sky',
        name: 'Bluebird Sky',
        colors: {
            text: '#0f1419',
            background: '#ffffff',
            primaryBtn: '#1d9bf0',
            secondaryBtn: '#f7f7f7',
            accent: '#8ecdf7'
        }
    },
    {
        id: 'retro-sport',
        name: 'Retro Sport',
        colors: {
            text: '#fbf5d4',
            background: '#0099ab',
            primaryBtn: '#5a39d0',
            secondaryBtn: '#006374',
            accent: '#fbf5d4'
        }
    },
    {
        id: 'editorial-mono',
        name: 'Editorial Mono',
        colors: {
            text: '#050505',
            background: '#ffffff',
            primaryBtn: '#121212',
            secondaryBtn: '#f6f5f4',
            accent: '#ffb600'
        }
    },
    {
        id: 'indigo-video',
        name: 'Indigo Video',
        colors: {
            text: '#2b1c50',
            background: '#ffffff',
            primaryBtn: '#565add',
            secondaryBtn: '#d1d1f7',
            accent: '#9f92ec'
        }
    },
    {
        id: 'huddle-up',
        name: 'Huddle Up',
        colors: {
            text: '#000000',
            background: '#ffffff',
            primaryBtn: '#611f69',
            secondaryBtn: '#f4ede4',
            accent: '#ecb22e'
        }
    },
    {
        id: 'marketing-heat',
        name: 'Marketing Heat',
        colors: {
            text: '#171a22',
            background: '#ffffff',
            primaryBtn: '#ff622d',
            secondaryBtn: '#421983',
            accent: '#ff622d'
        }
    },
    {
        id: 'lovebirds',
        name: 'Lovebirds',
        colors: {
            text: '#e3d7c6',
            background: '#2c440c',
            primaryBtn: '#d75628',
            secondaryBtn: '#496506',
            accent: '#e2904e'
        }
    },
    {
        id: 'code-editor',
        name: 'Code Editor',
        colors: {
            text: '#ffffff',
            background: '#131417',
            primaryBtn: '#47cf73',
            secondaryBtn: '#444857',
            accent: '#ffdd40'
        }
    },
    {
        id: 'glacial-expedition',
        name: 'Glacial Expedition',
        colors: {
            text: '#e5fffd',
            background: '#0b0c12',
            primaryBtn: '#66fcf1',
            secondaryBtn: '#202833',
            accent: '#c5c6c8'
        }
    },
    // Part 2: AI Originals (Dark Modes)
    {
        id: 'cyberpunk-neon',
        name: 'Cyberpunk Neon',
        colors: {
            text: '#e0e0e0',
            background: '#0b0014',
            primaryBtn: '#00f3ff',
            secondaryBtn: '#2d1b36',
            accent: '#ff0099'
        }
    },
    {
        id: 'bioluminescence',
        name: 'Bioluminescence',
        colors: {
            text: '#e6f1ff',
            background: '#021017',
            primaryBtn: '#00ff9d',
            secondaryBtn: '#0a2e36',
            accent: '#00bcd4'
        }
    },
    {
        id: 'mars-colony',
        name: 'Mars Colony',
        colors: {
            text: '#ffdcb8',
            background: '#1a0f0d',
            primaryBtn: '#ff5e3a',
            secondaryBtn: '#422119',
            accent: '#ffae42'
        }
    },
    {
        id: 'royal-velvet',
        name: 'Royal Velvet',
        colors: {
            text: '#fdf5e6',
            background: '#1a0509',
            primaryBtn: '#d4af37',
            secondaryBtn: '#3d0e15',
            accent: '#ffdf80'
        }
    },
    {
        id: 'toxic-waste',
        name: 'Toxic Waste',
        colors: {
            text: '#ffffff',
            background: '#121212',
            primaryBtn: '#ccff00',
            secondaryBtn: '#333333',
            accent: '#ccff00'
        }
    },
    {
        id: 'draculas-castle',
        name: 'Dracula\'s Castle',
        colors: {
            text: '#f8f8f2',
            background: '#282a36',
            primaryBtn: '#ff5555',
            secondaryBtn: '#44475a',
            accent: '#bd93f9'
        }
    },
    {
        id: 'matcha-dark',
        name: 'Matcha Dark',
        colors: {
            text: '#e8f5e9',
            background: '#111512',
            primaryBtn: '#66bb6a',
            secondaryBtn: '#1e2621',
            accent: '#a5d6a7'
        }
    },
    {
        id: 'sunset-vapor',
        name: 'Sunset Vapor',
        colors: {
            text: '#fff0f5',
            background: '#100b1c',
            primaryBtn: '#ff7e67',
            secondaryBtn: '#2a1a38',
            accent: '#ce93d8'
        }
    },
    {
        id: 'slate-copper',
        name: 'Slate & Copper',
        colors: {
            text: '#ecf0f1',
            background: '#1c2329',
            primaryBtn: '#cd7f32',
            secondaryBtn: '#2c3e50',
            accent: '#e67e22'
        }
    },
    {
        id: 'monolith',
        name: 'Monolith',
        colors: {
            text: '#ffffff',
            background: '#000000',
            primaryBtn: '#333333',
            secondaryBtn: '#1a1a1a',
            accent: '#808080'
        }
    },
    // Part 3: Expansion Pack (New Additions)
    // Dark Themes (+3)
    {
        id: 'abyss',
        name: 'Abyss',
        colors: {
            text: '#e0f7fa',
            background: '#050510',
            primaryBtn: '#00f0ff',
            secondaryBtn: '#0a0a20',
            accent: '#00bcd4'
        }
    },
    {
        id: 'crimson-ops',
        name: 'Crimson Ops',
        colors: {
            text: '#e0e0e0',
            background: '#1a1a1a',
            primaryBtn: '#ff2a2a',
            secondaryBtn: '#333333',
            accent: '#ff5252'
        }
    },
    // Coloured Themes (+2)
    {
        id: 'nordic-berry',
        name: 'Nordic Berry',
        colors: {
            text: '#fdeff9',
            background: '#2e2a39',
            primaryBtn: '#ff7eb6',
            secondaryBtn: '#4a4459',
            accent: '#d8a0c2'
        }
    },
    {
        id: 'sahara',
        name: 'Sahara',
        colors: {
            text: '#fff1e6',
            background: '#3d261e',
            primaryBtn: '#f4a261',
            secondaryBtn: '#5c3a2e',
            accent: '#e76f51'
        }
    },
    // Light Themes (+5)
    {
        id: 'lavender-mist',
        name: 'Lavender Mist',
        colors: {
            text: '#4a4063',
            background: '#f8f7ff',
            primaryBtn: '#9d86ff',
            secondaryBtn: '#eaddff',
            accent: '#bfaaff'
        }
    },
    {
        id: 'arctic-frost',
        name: 'Arctic Frost',
        colors: {
            text: '#2c3e50',
            background: '#f0f8ff',
            primaryBtn: '#00b4d8',
            secondaryBtn: '#caf0f8',
            accent: '#90e0ef'
        }
    },
    {
        id: 'paperback',
        name: 'Paperback',
        colors: {
            text: '#4a4036',
            background: '#f9f5e6',
            primaryBtn: '#d4a373',
            secondaryBtn: '#faedcd',
            accent: '#e3d5ca'
        }
    },
    {
        id: 'cherry-blossom',
        name: 'Cherry Blossom',
        colors: {
            text: '#592e38',
            background: '#fff0f5',
            primaryBtn: '#ff69b4',
            secondaryBtn: '#ffe4e1',
            accent: '#ffb7b2'
        }
    },
    {
        id: 'listsync-purple',
        name: 'ListSync Purple',
        colors: {
            text: '#ffffff',
            background: '#000000',
            primaryBtn: '#9d34da',
            secondaryBtn: '#1a1a1a',
            accent: '#bd73e8'
        }
    },
    {
        id: 'corporate-grey',
        name: 'Corporate Grey',
        colors: {
            text: '#2c3e50',
            background: '#f5f7fa',
            primaryBtn: '#5d6d7e',
            secondaryBtn: '#dfe6e9',
            accent: '#34495e'
        }
    }
]
