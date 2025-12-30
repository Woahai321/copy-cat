export const useAuth = () => {
  const token = useState<string | null>('auth-token', () => {
    if (process.client) {
      return localStorage.getItem('auth-token')
    }
    return null
  })

  const isAuthenticated = computed(() => !!token.value)

  const user = useState<any | null>('auth-user', () => null)

  const fetchUser = async () => {
    if (!token.value) return null
    const config = useRuntimeConfig()
    try {
      const u = await $fetch<any>(`${config.public.apiBase}/api/users/me`, {
        headers: { Authorization: `Bearer ${token.value}` }
      })
      user.value = u
      return u
    } catch (e) {
      user.value = null
      return null
    }
  }

  const login = async (username: string, password: string) => {
    const config = useRuntimeConfig()

    try {
      const response = await $fetch<{ access_token: string; token_type: string }>(
        `${config.public.apiBase}/api/auth/login`,
        {
          method: 'POST',
          body: { username, password }
        }
      )

      token.value = response.access_token

      if (process.client) {
        localStorage.setItem('auth-token', response.access_token)
      }

      // Fetch user details immediately after login
      await fetchUser()

      return true
    } catch (error) {
      console.error('Login failed:', error)
      return false
    }
  }

  const logout = () => {
    token.value = null
    user.value = null

    if (process.client) {
      localStorage.removeItem('auth-token')
    }
  }

  const getAuthHeaders = () => {
    if (!token.value) return {}
    return {
      Authorization: `Bearer ${token.value}`
    }
  }

  return {
    token,
    user,
    isAuthenticated,
    login,
    logout,
    fetchUser,
    getAuthHeaders
  }
}

