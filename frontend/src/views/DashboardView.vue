<template>
  <div class="min-vh-100 d-flex flex-column bg-body-tertiary transition-base">

    <nav class="navbar navbar-expand-lg bg-body shadow-sm sticky-top">
      <div class="container-fluid px-4">
        <span class="navbar-brand mb-0 h1 fw-bold d-flex align-items-center">
          <i class="bi bi-columns-gap me-2 text-primary"></i>
          Dashboard
        </span>

        <div class="d-flex align-items-center gap-3">
          <div class="form-check form-switch mb-0 fs-5">
            <input
                class="form-check-input cursor-pointer"
                type="checkbox"
                role="switch"
                id="darkModeSwitch"
                v-model="darkMode"
                @change="toggleDarkMode"
            >
            <label class="form-check-label ms-1" for="darkModeSwitch">
              <i :class="darkMode ? 'bi bi-moon-stars-fill text-warning' : 'bi bi-sun-fill text-warning'"></i>
            </label>
          </div>

          <div class="vr h-100 mx-2 d-none d-lg-block"></div>

          <button
              @click="handleLogout"
              class="btn btn-outline-danger btn-sm d-flex align-items-center"
          >
            <i class="bi bi-box-arrow-right me-2"></i>
            <span class="d-none d-sm-inline">Wyloguj</span>
          </button>
        </div>
      </div>
    </nav>

    <main class="flex-grow-1 p-4">
      <div class="container-fluid h-100">
        <div class="row g-4 h-100">

          <div class="col-12 col-lg-6">
            <div class="card h-100 border-0 shadow-sm rounded-4 hover-card">
              <div class="card-header bg-transparent border-0 pt-4 px-4 pb-0">
                <div class="d-flex align-items-center">
                  <div class="bg-primary bg-opacity-10 p-2 rounded-3 me-3 text-primary">
                    <i class="bi bi-pen-fill fs-4"></i>
                  </div>
                  <h3 class="h5 mb-0 fw-bold">Podpisywanie pliku</h3>
                </div>
              </div>
              <div class="card-body p-4">
                <sign-file :dark-mode="darkMode" />
              </div>
            </div>
          </div>

          <div class="col-12 col-lg-6">
            <div class="card h-100 border-0 shadow-sm rounded-4 hover-card">
              <div class="card-header bg-transparent border-0 pt-4 px-4 pb-0">
                <div class="d-flex align-items-center">
                  <div class="bg-success bg-opacity-10 p-2 rounded-3 me-3 text-success">
                    <i class="bi bi-shield-check fs-4"></i>
                  </div>
                  <h3 class="h5 mb-0 fw-bold">Weryfikacja podpisów</h3>
                </div>
              </div>
              <div class="card-body p-4">
                <verify-file :dark-mode="darkMode" />
              </div>
            </div>
          </div>

        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { useRouter } from 'vue-router';
import { AuthAPI } from "@/api.js";
import SignFile from "@/components/SignFile.vue";
import VerifyFile from "@/components/VerifyFile.vue";
import { onMounted, ref } from "vue";

export default {
  components: { VerifyFile, SignFile },
  setup() {
    const router = useRouter();
    const darkMode = ref(false);

    onMounted(() => {
      const savedMode = localStorage.getItem('darkMode');
      if (savedMode) {
        darkMode.value = JSON.parse(savedMode);
      } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        darkMode.value = true;
      }
      applyDarkMode(darkMode.value);
    });

    const toggleDarkMode = () => {
      localStorage.setItem('darkMode', JSON.stringify(darkMode.value));
      applyDarkMode(darkMode.value);
    };

    const applyDarkMode = (isDark) => {
      document.documentElement.setAttribute('data-bs-theme', isDark ? 'dark' : 'light');
    };

    const handleLogout = () => {
      AuthAPI.logout();
      router.push('/login');
    };

    return {
      darkMode,
      toggleDarkMode,
      handleLogout
    };
  }
};
</script>

<style scoped>

.transition-base,
.card,
.navbar {
  transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
}

.cursor-pointer {
  cursor: pointer;
}

</style>