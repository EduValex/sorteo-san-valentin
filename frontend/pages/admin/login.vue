<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-100 via-gray-200 to-gray-300 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md mx-auto">
      <!-- Logo/Header -->
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold text-gray-800 mb-2">
          Panel Administrador
        </h1>
        <p class="text-xl text-gray-600">CTS Turismo</p>
      </div>

      <!-- Login Form -->
      <div class="bg-white shadow-lg rounded-lg p-8">
        <h2 class="text-2xl font-semibold text-gray-800 mb-6 text-center">
          Iniciar Sesión
        </h2>

        <!-- Error Message -->
        <div v-if="errorMessage" class="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          {{ errorMessage }}
        </div>

        <form @submit.prevent="handleLogin">
          <div class="mb-4">
            <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
              Correo Electrónico
            </label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-500 focus:border-transparent"
              placeholder="admin@ctsturismo.cl"
            />
          </div>

          <div class="mb-6">
            <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
              Contraseña
            </label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-500 focus:border-transparent"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-gray-800 text-white py-3 px-4 rounded-lg font-semibold hover:bg-gray-900 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ loading ? 'Iniciando sesión...' : 'Ingresar' }}
          </button>
        </form>

        <!-- Link back to home -->
        <div class="mt-6 text-center">
          <NuxtLink to="/" class="text-sm text-gray-600 hover:text-gray-800">
            ← Volver al registro
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const api = useApi()
const router = useRouter()

const form = ref({
  email: '',
  password: ''
})

const loading = ref(false)
const errorMessage = ref('')

const handleLogin = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    const response: any = await api.loginAdmin(form.value.email, form.value.password)

    // Guardar tokens en localStorage
    localStorage.setItem('access_token', response.tokens.access)
    localStorage.setItem('refresh_token', response.tokens.refresh)
    localStorage.setItem('user', JSON.stringify(response.user))

    // Redirigir al dashboard
    router.push('/admin/dashboard')
  } catch (error: any) {
    errorMessage.value = error.message || 'Credenciales inválidas'
  } finally {
    loading.value = false
  }
}

// Redirigir si ya está autenticado
onMounted(() => {
  if (typeof window !== 'undefined' && localStorage.getItem('access_token')) {
    router.push('/admin/dashboard')
  }
})
</script>
