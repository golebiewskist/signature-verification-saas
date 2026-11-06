<template>
  <div class="d-flex flex-column gap-3 h-100">

    <div>
      <label class="form-label fw-semibold">Wybierz plik do podpisu</label>
      <input
        type="file"
        @change="onFileChange"
        class="form-control"
      />
    </div>

    <div v-if="selectedFile" class="card shadow-sm border-0 bg-body-tertiary">
      <div class="card-body">
        <div class="d-flex align-items-center mb-3">
          <i class="bi bi-file-earmark-text fs-4 text-primary me-2"></i>
          <div>
            <div class="small text-body-secondary">Wybrany plik:</div>
            <div class="fw-medium text-break">{{ selectedFile.name }}</div>
          </div>
        </div>

        <div class="border rounded overflow-hidden mb-3 position-relative bg-body">
          <VueSignaturePad
              ref="signaturePad"
              :maxWidth="3"
              :minWidth="1"
              :options="signatureOptions"
              height="160px"
              class="w-100"
              @begin="saveSignature"
              @end="saveSignature"
          />
          <div class="position-absolute bottom-0 end-0 p-2 opacity-50 small pe-none user-select-none text-body-secondary">
            Miejsce na podpis
          </div>
        </div>

        <div class="d-flex gap-2">
          <button
              @click="clearSignature"
              class="btn btn-outline-secondary btn-sm"
          >
            <i class="bi bi-eraser me-1"></i> Wyczyść
          </button>
          <button
              @click="signFile"
              class="btn btn-primary btn-sm flex-grow-1"
              :disabled="loading || !selectedFile"
          >
            <span v-if="loading" class="spinner-border spinner-border-sm me-1"></span>
            <i v-else class="bi bi-pen me-1"></i>
            {{ loading ? 'Przetwarzanie...' : 'Podpisz plik' }}
          </button>
        </div>
      </div>
    </div>

    <div>
      <label class="form-label fw-semibold mt-2">
        <i class="bi bi-paperclip me-1"></i>Dołącz istniejące podpisy (.sig)
      </label>
      <input
        type="file"
        accept=".sig"
        @change="onSigFileChange"
        class="form-control"
      />

      <div v-if="existingSignatures.length" class="mt-2">
        <div class="alert alert-info d-flex align-items-center py-2 mb-0">
          <i class="bi bi-info-circle me-2"></i>
          <span class="small">Załadowano {{ existingSignatures.length }} podpis(ów)</span>
        </div>
        <ul class="list-group list-group-flush mt-2 small">
          <li v-for="(sig, idx) in existingSignatures" :key="idx" class="list-group-item bg-transparent px-0 py-1">
            <i class="bi bi-person-check me-2 text-success"></i>
            {{ sig.username || sig.user_id }}
          </li>
        </ul>
      </div>
    </div>

    <div v-if="error" class="alert alert-danger d-flex align-items-center mt-2" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      <div>{{ error }}</div>
    </div>

    <div v-if="signatureData" class="mt-auto">
      <div class="card border-success mb-3">
        <div class="card-header bg-success text-white py-2">
          <i class="bi bi-check-circle-fill me-2"></i>Sukces
        </div>
        <div class="card-body">
          <h6 class="card-subtitle mb-2 text-body-secondary small">Podpisano jako:</h6>
          <p class="card-text fw-bold">{{ signatureData.username }}</p>

          <div class="bg-body-secondary p-2 rounded border font-monospace small text-break mb-3" style="max-height: 100px; overflow-y: auto;">
            {{ signatureData.signature }}
          </div>

          <button @click="downloadSignature" class="btn btn-success w-100">
            <i class="bi bi-download me-2"></i>Pobierz .sig
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, defineProps, watch } from "vue"
import { SignatureAPI } from "@/api"
import { VueSignaturePad } from "@selemondev/vue3-signature-pad"

const props = defineProps({
  darkMode: {
    type: Boolean,
    default: false
  }
})

const selectedFile = ref(null)
const signatureData = ref(null)
const existingSignatures = ref([])
const loading = ref(false)
const error = ref(null)
const signaturePad = ref(null)
const drawnSignature = ref(null)

const signatureOptions = computed(() => ({
  backgroundColor: props.darkMode ? '#2b3035' : 'rgb(255, 255, 255)',
  penColor: props.darkMode ? '#f8f9fa' : '#212529'
}))

watch(() => props.darkMode, () => {});

function onFileChange(event) {
  selectedFile.value = event.target.files[0] || null
  signatureData.value = null
  error.value = null
  existingSignatures.value = []
}

function onSigFileChange(event) {
  const file = event.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = e => {
    try {
      const json = JSON.parse(e.target.result)
      existingSignatures.value = Array.isArray(json) ? json : [json]
    } catch {
      error.value = "Nieprawidłowy plik .sig"
    }
  }
  reader.readAsText(file)
}

async function calculateHash(file) {
  const buffer = await file.arrayBuffer()
  const hashBuffer = await crypto.subtle.digest("SHA-256", buffer)
  const hashArray = Array.from(new Uint8Array(hashBuffer))
  return hashArray.map(b => b.toString(16).padStart(2, "0")).join("")
}

function saveSignature() {
  drawnSignature.value = signaturePad.value?.saveSignature()
}

async function signFile() {
  if (!selectedFile.value) return

  loading.value = true
  error.value = null

  try {
    const checksum = await calculateHash(selectedFile.value)

    const payload = {
      file_name: selectedFile.value.name,
      checksum: checksum,
      signature_image: signaturePad.value?.saveSignature()
    }

    signatureData.value = await SignatureAPI.sign(payload)
  } catch (err) {
    console.error("Błąd podpisywania:", err)
    error.value = err.message || "Nie udało się podpisać pliku"
  } finally {
    loading.value = false
  }
}

function downloadSignature() {
  if (!signatureData.value || !selectedFile.value) return

  const jsonContent = JSON.stringify([signatureData.value], null, 2)
  const originalName = selectedFile.value.name
  const baseName = originalName.replace(/\.[^/.]+$/, "")

  const blob = new Blob([jsonContent], { type: "application/json" })
  const link = document.createElement("a")
  link.href = URL.createObjectURL(blob)
  link.download = `${baseName}.sig`
  link.click()
  URL.revokeObjectURL(link.href)
}

function clearSignature() {
  signaturePad.value?.clearCanvas()
  drawnSignature.value = null
}
</script>

<style scoped>
</style>