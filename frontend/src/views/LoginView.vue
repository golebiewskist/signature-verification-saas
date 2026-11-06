<template>
  <div class="min-vh-100 d-flex align-items-center justify-content-center bg-light">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-6 col-lg-4">

          <div class="card shadow-lg border-0 rounded-4">
            <div class="card-body p-4 p-md-5">

              <div class="text-center mb-4">
                <div class="mb-3 text-primary">
                  <i class="bi bi-shield-lock display-4"></i>
                </div>
                <h1 class="h3 fw-bold text-dark">Logowanie</h1>
                <p class="text-muted">Zaloguj się do systemu podpisywania</p>
              </div>

              <form @submit.prevent="handleLogin">
                <div class="mb-3">
                  <div class="input-group input-group-lg group-focus-wrapper">
                    <span class="input-group-text bg-white border-end-0 text-muted">
                      <i class="bi bi-person"></i>
                    </span>
                    <input
                        v-model="username"
                        type="text"
                        placeholder="Nazwa użytkownika"
                        class="form-control border-start-0 ps-0 shadow-none"
                        required
                    />
                  </div>
                </div>

                <div class="mb-4">
                  <div class="input-group input-group-lg group-focus-wrapper">
                    <span class="input-group-text bg-white border-end-0 text-muted">
                      <i class="bi bi-lock"></i>
                    </span>
                    <input
                        v-model="password"
                        type="password"
                        placeholder="Hasło"
                        class="form-control border-start-0 ps-0 shadow-none"
                        required
                    />
                  </div>
                </div>

                <button
                    type="submit"
                    class="btn btn-primary btn-lg w-100 py-3 fw-semibold shadow-sm"
                    :disabled="loading"
                >
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  <i v-else class="bi bi-box-arrow-in-right me-2"></i>
                  {{ loading ? 'Logowanie...' : 'Zaloguj się' }}
                </button>
              </form>

              <div v-if="error" class="alert alert-danger d-flex align-items-center mt-3 mb-0" role="alert">
                <i class="bi bi-exclamation-triangle-fill me-2"></i>
                <div>{{ error }}</div>
              </div>

            </div>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router';
import { ref } from 'vue';
import { AuthAPI } from "@/api.js";

export default {
  setup() {
    const router = useRouter();
    const username = ref('');
    const password = ref('');
    const error = ref('');
    const loading = ref(false);

    const handleLogin = async () => {
      if (!username.value || !password.value) {
        error.value = 'Proszę wypełnić wszystkie pola';
        return;
      }

      loading.value = true;
      error.value = '';

      try {
        await AuthAPI.login(username.value, password.value);
        router.push('/dashboard');
      } catch (err) {
        error.value = err.response?.data?.message || 'Logowanie nie powiodło się';
      } finally {
        loading.value = false;
      }
    };

    return {
      username,
      password,
      error,
      loading,
      handleLogin,
    };
  }
};
</script>

<style scoped>

.input-group-text {
  transition: border-color 0.15s ease-in-out;
}


.group-focus-wrapper:focus-within .input-group-text,
.group-focus-wrapper:focus-within .form-control {
  border-color: var(--bs-primary);
  box-shadow: none;
}

.group-focus-wrapper:focus-within .input-group-text {
  color: var(--bs-primary) !important;
}

.btn-primary {
  transition: all 0.2s;
}
.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 .5rem 1rem rgba(0,0,0,.15)!important;
}
</style>