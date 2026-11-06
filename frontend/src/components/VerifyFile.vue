<template>
  <div class="d-flex flex-column gap-3 h-100">

    <div>
      <label class="form-label fw-semibold">
        <i class="bi bi-file-earmark-binary me-1"></i> Plik do weryfikacji
      </label>
      <input
          type="file"
          @change="onFileChange"
          class="form-control"
      />
      <div v-if="selectedFile" class="form-text text-body-secondary">
        <i class="bi bi-check2 me-1"></i> {{ selectedFile.name }}
      </div>
    </div>

    <div>
      <label class="form-label fw-semibold">
        <i class="bi bi-pen me-1"></i> Pliki podpisów (.sig)
      </label>
      <input
          type="file"
          multiple
          accept=".sig,.json"
          @change="onSignatureFilesChange"
          class="form-control"
      />
      <div v-if="signatureFiles.length" class="form-text text-body-secondary">
        <i class="bi bi-files me-1"></i> Wybrano plików: {{ signatureFiles.length }}
      </div>
    </div>

    <div v-if="allSignatures.length" class="bg-body-secondary p-3 rounded-3 border">
      <h6 class="h6 fw-bold mb-2 text-body-secondary">
        <i class="bi bi-eye me-1"></i> Znalezione podpisy:
      </h6>
      <div class="d-flex flex-wrap gap-2">
        <span
          v-for="(sig, i) in allSignatures"
          :key="i"
          class="badge bg-body border text-body shadow-sm fw-normal d-flex align-items-center"
        >
          <i class="bi bi-person-fill me-1 text-primary"></i>
          {{ sig.username || sig.user_id }}
        </span>
      </div>
    </div>

    <div v-if="error" class="alert alert-danger d-flex align-items-center mb-0" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      <div>{{ error }}</div>
    </div>

    <button
        @click="verifySignatures"
        class="btn btn-success w-100 py-2 mt-2"
        :disabled="loading || !selectedFile || !allSignatures.length"
    >
      <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
      <i v-else class="bi bi-shield-check me-2"></i>
      {{ loading ? 'Weryfikacja w toku...' : 'Zweryfikuj podpisy' }}
    </button>

    <div v-if="results.length" class="mt-4 animate-fade-in">
      <div class="d-flex align-items-center mb-3">
        <div class="bg-success bg-opacity-10 p-2 rounded me-2 text-success">
          <i class="bi bi-clipboard-data fs-5"></i>
        </div>
        <h5 class="mb-0 fw-bold">Raport weryfikacji</h5>
      </div>

      <div class="table-responsive rounded-3 border shadow-sm">
        <table class="table table-hover table-striped mb-0 align-middle">
          <thead class="table-light">
          <tr>
            <th scope="col" class="py-3 ps-3">Użytkownik</th>
            <th scope="col" class="py-3 text-center">Status</th>
            <th scope="col" class="py-3">Szczegóły</th>
          </tr>
          </thead>
          <tbody>
          <tr v-for="(r, i) in results" :key="i">
            <td class="ps-3 fw-medium">
              <i class="bi bi-person me-2 text-secondary"></i>
              {{ r.username || r.user_id }}
            </td>
            <td class="text-center">
              <span
                class="badge rounded-pill"
                :class="r.valid ? 'text-bg-success' : 'text-bg-danger'"
              >
                <i :class="r.valid ? 'bi bi-check-lg' : 'bi bi-x-lg'" class="me-1"></i>
                {{ r.valid ? 'Ważny' : 'Nieważny' }}
              </span>
            </td>
            <td class="small text-body-secondary">
              <span v-if="r.error" class="text-danger d-flex align-items-center">
                <i class="bi bi-info-circle me-1"></i> {{ r.error }}
              </span>
              <span v-else class="text-success">
                Podpis poprawny
              </span>
            </td>
          </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, defineProps } from "vue"
import { SignatureAPI } from "@/api"

const props = defineProps({
  darkMode: {
    type: Boolean,
    default: false
  }
})

const selectedFile = ref(null)
const signatureFiles = ref([])
const allSignatures = ref([])
const results = ref([])
const loading = ref(false)
const error = ref(null)

function onFileChange(event) {
  selectedFile.value = event.target.files[0] || null
  results.value = []
  error.value = null
}

async function onSignatureFilesChange(event) {
  signatureFiles.value = Array.from(event.target.files) || []
  allSignatures.value = []
  results.value = []
  error.value = null

  const readPromises = signatureFiles.value.map(async (file) => {
    try {
      const text = await file.text()
      const json = JSON.parse(text)
      return Array.isArray(json) ? json : [json]
    } catch (err) {
      console.warn(`Błąd odczytu pliku ${file.name}:`, err)
      return []
    }
  })

  try {
    const signaturesArrays = await Promise.all(readPromises)
    allSignatures.value = signaturesArrays.flat()

    if (allSignatures.value.length === 0 && signatureFiles.value.length > 0) {
      error.value = "Nie znaleziono poprawnych danych podpisów w wybranych plikach."
    }
  } catch (err) {
    error.value = "Błąd krytyczny podczas wczytywania plików."
  }
}

async function calculateHash(file) {
  const buffer = await file.arrayBuffer()
  const hashBuffer = await crypto.subtle.digest("SHA-256", buffer)
  const hashArray = Array.from(new Uint8Array(hashBuffer))
  return hashArray.map(b => b.toString(16).padStart(2, "0")).join("")
}

async function verifySignatures() {
  if (!selectedFile.value || !allSignatures.value.length) return
  loading.value = true
  error.value = null
  results.value = []

  try {
    const checksum = await calculateHash(selectedFile.value)

    const response = await SignatureAPI.verify({
      checksum,
      signatures: allSignatures.value
    })

    results.value = response.verification_results || []

    if (results.value.length === 0) {
       error.value = "Serwer nie zwrócił wyników weryfikacji."
    }

  } catch (err) {
    error.value = err.message || "Wystąpił błąd podczas weryfikacji."
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>