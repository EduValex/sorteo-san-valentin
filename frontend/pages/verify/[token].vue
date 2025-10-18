<template>
  <div class="min-h-screen bg-gradient-to-br from-pink-100 via-red-100 to-pink-200 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md mx-auto">
      <!-- Logo/Header -->
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold text-red-600 mb-2">
          Sorteo San Valentín
        </h1>
        <p class="text-xl text-gray-700">CTS Turismo</p>
      </div>

      <div class="bg-white shadow-lg rounded-lg p-8">
        <!-- Loading State -->
        <div v-if="loading" class="text-center py-8">
          <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
          <p class="mt-4 text-gray-600">Verificando tu correo...</p>
        </div>

        <!-- Success State - Show Password Form -->
        <div v-else-if="verified && !passwordSet">
          <h2 class="text-2xl font-semibold text-gray-800 mb-6 text-center">
            ¡Correo Verificado!
          </h2>
          <p class="text-gray-600 mb-6 text-center">
            Ahora crea tu contraseña para confirmar tu participación en el sorteo.
          </p>

          <!-- Error Message -->
          <div v-if="errorMessage" class="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
            {{ errorMessage }}
          </div>

          <form @submit.prevent="handleSetPassword">
            <div class="mb-4">
              <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
                Contraseña *
              </label>
              <input
                id="password"
                v-model="passwordForm.password"
                type="password"
                required
                minlength="8"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                placeholder="Mínimo 8 caracteres"
              />
            </div>

            <div class="mb-6">
              <label for="password_confirm" class="block text-sm font-medium text-gray-700 mb-2">
                Confirmar Contraseña *
              </label>
              <input
                id="password_confirm"
                v-model="passwordForm.password_confirm"
                type="password"
                required
                minlength="8"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                placeholder="Repite tu contraseña"
              />
            </div>

            <button
              type="submit"
              :disabled="submitting"
              class="w-full bg-red-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-red-700 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ submitting ? 'Guardando...' : 'Confirmar Participación' }}
            </button>
          </form>
        </div>

        <!-- Password Set Success -->
        <div v-else-if="passwordSet" class="text-center py-8">
          <div class="text-green-600 mb-4">
            <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
          </div>
          <h2 class="text-2xl font-semibold text-gray-800 mb-4">
            ¡Participación Confirmada!
          </h2>
          <p class="text-gray-600 mb-6">
            Ya estás participando en el Sorteo de San Valentín. ¡Mucha suerte!
          </p>
          <NuxtLink
            to="/"
            class="inline-block bg-red-600 text-white py-2 px-6 rounded-lg font-semibold hover:bg-red-700 transition duration-200"
          >
            Volver al Inicio
          </NuxtLink>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="text-center py-8">
          <div class="text-red-600 mb-4">
            <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </div>
          <h2 class="text-2xl font-semibold text-gray-800 mb-4">
            Error de Verificación
          </h2>
          <p class="text-gray-600 mb-6">
            {{ error }}
          </p>
          <NuxtLink
            to="/"
            class="inline-block bg-red-600 text-white py-2 px-6 rounded-lg font-semibold hover:bg-red-700 transition duration-200"
          >
            Volver al Inicio
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const api = useApi()

const token = route.params.token as string

const loading = ref(true)
const verified = ref(false)
const passwordSet = ref(false)
const error = ref('')
const errorMessage = ref('')
const submitting = ref(false)

const passwordForm = ref({
  password: '',
  password_confirm: ''
})

// Verificar email al montar el componente
onMounted(async () => {
  try {
    await api.verifyEmail(token)
    verified.value = true
  } catch (err: any) {
    error.value = err.message || 'Token de verificación inválido o ya utilizado.'
  } finally {
    loading.value = false
  }
})

// Establecer contraseña
const handleSetPassword = async () => {
  if (passwordForm.value.password !== passwordForm.value.password_confirm) {
    errorMessage.value = 'Las contraseñas no coinciden.'
    return
  }

  submitting.value = true
  errorMessage.value = ''

  try {
    await api.setPassword({
      verification_token: token,
      ...passwordForm.value
    })
    passwordSet.value = true
  } catch (err: any) {
    errorMessage.value = err.message || 'Error al establecer la contraseña. Intenta nuevamente.'
  } finally {
    submitting.value = false
  }
}
</script>
