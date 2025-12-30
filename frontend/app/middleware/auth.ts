export default defineNuxtRouteMiddleware((to, from) => {
  const { isAuthenticated } = useAuth()

  // If the route is login, allow access
  if (to.path === '/login') {
    return
  }

  // If not authenticated, redirect to login
  if (!isAuthenticated.value) {
    return navigateTo('/login')
  }

  // Strict Password Change Enforcement
  const auth = useAuth()
  if (auth.user.value?.require_password_change && to.path !== '/change-password' && to.path !== '/setup-paths') {
    return navigateTo('/change-password')
  }
})

