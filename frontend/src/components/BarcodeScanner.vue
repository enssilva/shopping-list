<template>
  <div class="barcode-scanner">
    <!-- Live Camera Viewfinder -->
    <div v-show="isScanning" class="scanner-viewport">
      <video ref="videoRef" autoplay playsinline muted class="scanner-video"></video>

      <!-- Aiming Overlay -->
      <div class="scanner-overlay">
        <div class="scanner-mask-top"></div>
        <div class="scanner-middle-row">
          <div class="scanner-mask-side"></div>
          <div class="scanner-aim-box" :class="{ 'is-confirming': isConfirming }">
            <span class="corner corner-tl"></span>
            <span class="corner corner-tr"></span>
            <span class="corner corner-bl"></span>
            <span class="corner corner-br"></span>
            <div class="laser-line"></div>
          </div>
          <div class="scanner-mask-side"></div>
        </div>
        <div class="scanner-mask-bottom">
          <span class="scanner-hint">
            {{ isConfirming ? 'Confirming barcode...' : 'Align the barcode inside the frame' }}
          </span>
        </div>
      </div>

      <!-- Camera Controls Overlay -->
      <div class="scanner-controls-top">
        <q-btn
          v-if="hasTorch"
          round
          dense
          unelevated
          :color="torchEnabled ? 'amber-8' : 'dark'"
          :icon="torchEnabled ? 'flash_on' : 'flash_off'"
          aria-label="Toggle flashlight"
          @click="toggleTorch"
        />
        <q-btn
          v-if="availableCameras.length > 1"
          round
          dense
          unelevated
          color="dark"
          icon="cameraswitch"
          aria-label="Switch camera lens"
          @click="switchCamera"
        />
      </div>

      <div v-if="hasZoom" class="scanner-controls-bottom">
        <q-btn-group rounded unelevated class="zoom-pill-group">
          <q-btn
            v-for="preset in zoomPresets"
            :key="preset"
            dense
            no-caps
            size="sm"
            :label="`${preset}x`"
            :color="Math.abs(currentZoom - preset) < 0.15 ? 'primary' : 'dark'"
            @click="applyZoom(preset)"
          />
        </q-btn-group>
      </div>
    </div>

    <!-- Hidden File Input for Native Mobile Camera Photo Fallback -->
    <input
      ref="photoInputRef"
      type="file"
      accept="image/*"
      capture="environment"
      class="hidden"
      @change="handlePhotoSelected"
    />

    <!-- Action Buttons -->
    <div class="q-mt-md">
      <div class="row q-col-gutter-sm">
        <div class="col-12 col-sm-7">
          <q-btn
            v-if="!isScanning"
            color="primary"
            icon="qr_code_scanner"
            label="Start Scanner"
            :loading="isStartingCamera"
            @click="startScanner"
            class="full-width"
          />
          <q-btn
            v-else
            color="negative"
            icon="stop"
            label="Stop Scanner"
            @click="stopScanner"
            class="full-width"
          />
        </div>

        <div class="col-12 col-sm-5">
          <q-btn
            outline
            color="primary"
            icon="photo_camera"
            label="Scan from Photo"
            :loading="isProcessingPhoto"
            @click="triggerPhotoCapture"
            class="full-width"
          />
        </div>
      </div>

      <div class="text-center text-grey-7 q-my-sm">OR</div>

      <q-input
        v-model="manualBarcode"
        label="Manual Barcode Entry"
        outlined
        dense
        inputmode="numeric"
        mask="#############"
        unmasked-value
        :rules="[
          val =>
            !val ||
            val.length === 8 ||
            val.length === 12 ||
            val.length === 13 ||
            'Use 8, 12, or 13 digits'
        ]"
        lazy-rules
        @keyup.enter="handleManualSearch"
      >
        <template v-slot:append>
          <q-btn
            round
            flat
            icon="search"
            @click="handleManualSearch"
            :disable="!isValidLength"
          />
        </template>
      </q-input>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onBeforeUnmount } from 'vue'
import { useQuasar } from 'quasar'
import {
  BarcodeDetector as PonyfillBarcodeDetector,
  prepareZXingModule
} from 'barcode-detector/ponyfill'
import zxingWasmUrl from 'zxing-wasm/reader/zxing_reader.wasm?url'
import { api } from 'boot/axios'
import {
  SUPPORTED_BARCODE_FORMATS,
  isValidGtinCheckDigit,
  normalizeScannedBarcode
} from 'src/utils/barcode'

const PREFERRED_CAMERA_KEY = 'preferred_barcode_camera_id'
const SCAN_INTERVAL_MS = 100
const CONFIRM_WINDOW_MS = 1500
const MAX_PHOTO_DIMENSION = 1800

const emit = defineEmits(['detected'])
const $q = useQuasar()

const videoRef = ref(null)
const photoInputRef = ref(null)

const isScanning = ref(false)
const isStartingCamera = ref(false)
const isProcessingPhoto = ref(false)
const isConfirming = ref(false)
const manualBarcode = ref('')

const availableCameras = ref([])
const currentCameraIndex = ref(0)
const hasTorch = ref(false)
const torchEnabled = ref(false)
const hasZoom = ref(false)
const currentZoom = ref(1)
const zoomRange = ref({ min: 1, max: 1 })

let mediaStream = null
let activeTrack = null
let scanTimerId = null
let isDetectingFrame = false
let scanCanvas = null
let scanCtx = null
let lastCandidate = { code: '', timestamp: 0 }

let primaryDetectorPromise = null
let ponyfillDetectorPromise = null
let isUsingNativeDetector = false
let zxingPrepared = false

const isValidLength = computed(() => {
  const len = manualBarcode.value.length
  return len === 8 || len === 12 || len === 13
})

const zoomPresets = computed(() => {
  const { min, max } = zoomRange.value
  const presets = [1, 1.5, 2, 3].filter(z => z >= min && z <= max)
  if (!presets.length) return [Number(min.toFixed(1))]
  if (!presets.some(z => Math.abs(z - min) < 0.1)) {
    presets.unshift(Number(min.toFixed(1)))
  }
  return presets
})

const ensureZXingPrepared = () => {
  if (zxingPrepared) return
  zxingPrepared = true
  prepareZXingModule({
    overrides: {
      locateFile: (path, prefix) => {
        if (path.endsWith('.wasm')) {
          return zxingWasmUrl
        }
        return prefix + path
      }
    }
  })
}

const getPonyfillDetector = async () => {
  if (!ponyfillDetectorPromise) {
    ponyfillDetectorPromise = Promise.resolve().then(() => {
      ensureZXingPrepared()
      return new PonyfillBarcodeDetector({ formats: SUPPORTED_BARCODE_FORMATS })
    })
  }
  return ponyfillDetectorPromise
}

const getPrimaryDetector = async () => {
  if (!primaryDetectorPromise) {
    primaryDetectorPromise = (async () => {
      if (typeof window !== 'undefined' && 'BarcodeDetector' in window) {
        try {
          const supported = await window.BarcodeDetector.getSupportedFormats()
          const matching = SUPPORTED_BARCODE_FORMATS.filter(f => supported.includes(f))
          if (matching.includes('ean_13') && matching.includes('ean_8')) {
            isUsingNativeDetector = true
            return new window.BarcodeDetector({ formats: matching })
          }
        } catch {
          // Fall back to ZXing WASM ponyfill
        }
      }
      isUsingNativeDetector = false
      return getPonyfillDetector()
    })()
  }
  return primaryDetectorPromise
}

const extractValidBarcode = (detections) => {
  if (!Array.isArray(detections)) return null

  for (const item of detections) {
    const normalized = normalizeScannedBarcode(item.rawValue, item.format)
    if (isValidGtinCheckDigit(normalized)) {
      return normalized
    }
  }
  return null
}

const triggerFeedback = () => {
  if (typeof navigator !== 'undefined' && typeof navigator.vibrate === 'function') {
    navigator.vibrate(100)
  }
}

const processBarcode = async (barcode) => {
  try {
    const response = await api.get(`/products/barcode/${barcode}`)
    emit('detected', {
      exists: true,
      product: response.data
    })
    manualBarcode.value = ''
  } catch {
    emit('detected', {
      exists: false,
      barcode
    })
  }
}

const loadAvailableCameras = async (activeDeviceId) => {
  try {
    const devices = await navigator.mediaDevices.enumerateDevices()
    const videoInputs = devices.filter(d => d.kind === 'videoinput')

    // Prefer rear-facing cameras when labels are available
    const rearCameras = videoInputs.filter(d => !/front|user|selfie/i.test(d.label))
    const list = rearCameras.length > 0 ? rearCameras : videoInputs

    availableCameras.value = list
    const idx = list.findIndex(d => d.deviceId === activeDeviceId)
    currentCameraIndex.value = idx >= 0 ? idx : 0
  } catch {
    availableCameras.value = []
  }
}

const configureTrackCapabilities = async (track) => {
  hasTorch.value = false
  torchEnabled.value = false
  hasZoom.value = false
  currentZoom.value = 1
  zoomRange.value = { min: 1, max: 1 }

  if (!track || typeof track.getCapabilities !== 'function') return

  try {
    const capabilities = track.getCapabilities()
    const settings = typeof track.getSettings === 'function' ? track.getSettings() : {}

    if (Array.isArray(capabilities.focusMode) && capabilities.focusMode.includes('continuous')) {
      try {
        await track.applyConstraints({ advanced: [{ focusMode: 'continuous' }] })
      } catch {
        // Focus mode constraint not accepted by this device
      }
    }

    if (capabilities.torch) {
      hasTorch.value = true
    }

    if (
      capabilities.zoom &&
      typeof capabilities.zoom.min === 'number' &&
      typeof capabilities.zoom.max === 'number' &&
      capabilities.zoom.max > capabilities.zoom.min
    ) {
      hasZoom.value = true
      zoomRange.value = {
        min: capabilities.zoom.min,
        max: capabilities.zoom.max
      }
      currentZoom.value = typeof settings.zoom === 'number' ? settings.zoom : capabilities.zoom.min
    }
  } catch {
    // Device does not expose track capabilities
  }
}

const openCameraStream = async (deviceId = null) => {
  const baseVideo = deviceId
    ? { deviceId: { exact: deviceId } }
    : { facingMode: { ideal: 'environment' } }

  const constraintAttempts = [
    {
      video: {
        ...baseVideo,
        width: { ideal: 1920, min: 1280 },
        height: { ideal: 1080, min: 720 }
      },
      audio: false
    },
    {
      video: {
        ...baseVideo,
        width: { ideal: 1280 },
        height: { ideal: 720 }
      },
      audio: false
    },
    {
      video: { facingMode: { ideal: 'environment' } },
      audio: false
    },
    {
      video: true,
      audio: false
    }
  ]

  let lastError = null
  for (const constraints of constraintAttempts) {
    try {
      return await navigator.mediaDevices.getUserMedia(constraints)
    } catch (err) {
      lastError = err
      if (err?.name === 'NotAllowedError' || err?.name === 'SecurityError') {
        throw err
      }
    }
  }
  throw lastError || new Error('Unable to access camera')
}

const scheduleNextScan = () => {
  if (!isScanning.value) return
  scanTimerId = window.setTimeout(scanCurrentFrame, SCAN_INTERVAL_MS)
}

const scanCurrentFrame = async () => {
  if (!isScanning.value) return

  const video = videoRef.value
  if (!video || video.readyState < 2 || !video.videoWidth || !video.videoHeight || isDetectingFrame) {
    scheduleNextScan()
    return
  }

  isDetectingFrame = true
  try {
    const detector = await getPrimaryDetector()

    // Crop to central horizontal band where the aiming overlay sits
    const cropWidth = Math.floor(video.videoWidth * 0.92)
    const cropHeight = Math.floor(video.videoHeight * 0.44)
    const cropX = Math.floor((video.videoWidth - cropWidth) / 2)
    const cropY = Math.floor((video.videoHeight - cropHeight) / 2)

    if (!scanCanvas) {
      scanCanvas = document.createElement('canvas')
      scanCtx = scanCanvas.getContext('2d', { willReadFrequently: true })
    }
    if (scanCanvas.width !== cropWidth || scanCanvas.height !== cropHeight) {
      scanCanvas.width = cropWidth
      scanCanvas.height = cropHeight
    }

    scanCtx.drawImage(video, cropX, cropY, cropWidth, cropHeight, 0, 0, cropWidth, cropHeight)

    const detections = await detector.detect(scanCanvas)
    const validCode = extractValidBarcode(detections)
    const now = Date.now()

    if (validCode) {
      if (
        lastCandidate.code === validCode &&
        now - lastCandidate.timestamp <= CONFIRM_WINDOW_MS
      ) {
        // Confirmed by 2 consecutive valid reads
        isConfirming.value = false
        lastCandidate = { code: '', timestamp: 0 }
        triggerFeedback()
        stopScanner()
        await processBarcode(validCode)
        return
      }

      lastCandidate = { code: validCode, timestamp: now }
      isConfirming.value = true
    } else if (isConfirming.value && now - lastCandidate.timestamp > CONFIRM_WINDOW_MS) {
      isConfirming.value = false
      lastCandidate = { code: '', timestamp: 0 }
    }
  } catch (err) {
    // If native detector fails unexpectedly, switch to ZXing WASM ponyfill
    if (isUsingNativeDetector) {
      isUsingNativeDetector = false
      primaryDetectorPromise = getPonyfillDetector()
    } else {
      console.warn('Frame scan error:', err)
    }
  } finally {
    isDetectingFrame = false
    scheduleNextScan()
  }
}

const startScanner = async (requestedDeviceId = null) => {
  if (!navigator.mediaDevices?.getUserMedia) {
    $q.notify({
      message: 'Live camera requires HTTPS. Use "Scan from Photo" or enter the barcode manually.',
      color: 'warning',
      position: 'top',
      icon: 'warning',
      timeout: 4500
    })
    return
  }

  stopScanner()
  isStartingCamera.value = true
  lastCandidate = { code: '', timestamp: 0 }
  isConfirming.value = false

  try {
    // Warm up detector while requesting camera permission
    const detectorReady = getPrimaryDetector()

    const preferredId = requestedDeviceId || localStorage.getItem(PREFERRED_CAMERA_KEY)
    mediaStream = await openCameraStream(preferredId)

    const [track] = mediaStream.getVideoTracks()
    activeTrack = track || null

    if (videoRef.value) {
      videoRef.value.srcObject = mediaStream
      await videoRef.value.play()
    }

    const activeSettings = activeTrack?.getSettings?.() || {}
    if (activeSettings.deviceId) {
      localStorage.setItem(PREFERRED_CAMERA_KEY, activeSettings.deviceId)
    }

    await Promise.all([
      detectorReady,
      loadAvailableCameras(activeSettings.deviceId),
      configureTrackCapabilities(activeTrack)
    ])

    isScanning.value = true
    scheduleNextScan()
  } catch (err) {
    stopScanner()
    const isPermissionError = err?.name === 'NotAllowedError' || err?.name === 'SecurityError'
    $q.notify({
      message: isPermissionError
        ? 'Camera permission denied. Allow camera access or use "Scan from Photo".'
        : 'Could not start camera. Try "Scan from Photo" instead.',
      color: 'negative',
      position: 'top',
      icon: 'error'
    })
  } finally {
    isStartingCamera.value = false
  }
}

const stopScanner = () => {
  isScanning.value = false
  isConfirming.value = false
  lastCandidate = { code: '', timestamp: 0 }

  if (scanTimerId !== null) {
    clearTimeout(scanTimerId)
    scanTimerId = null
  }

  if (mediaStream) {
    mediaStream.getTracks().forEach(track => track.stop())
    mediaStream = null
  }

  activeTrack = null
  hasTorch.value = false
  torchEnabled.value = false
  hasZoom.value = false

  if (videoRef.value) {
    videoRef.value.srcObject = null
  }
}

const toggleTorch = async () => {
  if (!activeTrack || !hasTorch.value) return
  const nextState = !torchEnabled.value
  try {
    await activeTrack.applyConstraints({ advanced: [{ torch: nextState }] })
    torchEnabled.value = nextState
  } catch {
    $q.notify({
      message: 'Flashlight is not available on this camera lens.',
      color: 'warning',
      position: 'top'
    })
  }
}

const applyZoom = async (targetZoom) => {
  if (!activeTrack || !hasZoom.value) return
  const clamped = Math.min(Math.max(targetZoom, zoomRange.value.min), zoomRange.value.max)
  try {
    await activeTrack.applyConstraints({ advanced: [{ zoom: clamped }] })
    currentZoom.value = clamped
  } catch {
    // Zoom constraint rejected on this lens
  }
}

const switchCamera = async () => {
  if (availableCameras.value.length <= 1) return
  const nextIndex = (currentCameraIndex.value + 1) % availableCameras.value.length
  const nextCamera = availableCameras.value[nextIndex]
  if (nextCamera?.deviceId) {
    localStorage.setItem(PREFERRED_CAMERA_KEY, nextCamera.deviceId)
    await startScanner(nextCamera.deviceId)
  }
}

const triggerPhotoCapture = () => {
  if (photoInputRef.value) {
    photoInputRef.value.value = ''
    photoInputRef.value.click()
  }
}

const loadImageFromFile = async (file) => {
  if (typeof createImageBitmap === 'function') {
    return createImageBitmap(file)
  }
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file)
    const img = new Image()
    img.onload = () => {
      URL.revokeObjectURL(url)
      resolve(img)
    }
    img.onerror = (err) => {
      URL.revokeObjectURL(url)
      reject(err)
    }
    img.src = url
  })
}

const drawSourceToCanvas = (source, rotate90 = false) => {
  const srcWidth = source.width || source.naturalWidth
  const srcHeight = source.height || source.naturalHeight
  const scale = Math.min(1, MAX_PHOTO_DIMENSION / Math.max(srcWidth, srcHeight))
  const targetW = Math.max(1, Math.round(srcWidth * scale))
  const targetH = Math.max(1, Math.round(srcHeight * scale))

  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')

  if (rotate90) {
    canvas.width = targetH
    canvas.height = targetW
    ctx.translate(targetH, 0)
    ctx.rotate(Math.PI / 2)
    ctx.drawImage(source, 0, 0, targetW, targetH)
  } else {
    canvas.width = targetW
    canvas.height = targetH
    ctx.drawImage(source, 0, 0, targetW, targetH)
  }

  return canvas
}

const detectFromCanvasWithFallback = async (canvas, rotatedCanvas) => {
  const primary = await getPrimaryDetector()

  const pass1 = extractValidBarcode(await primary.detect(canvas))
  if (pass1) return pass1

  const pass2 = extractValidBarcode(await primary.detect(rotatedCanvas))
  if (pass2) return pass2

  // If native detector missed the photo, try ZXing WASM as a second opinion
  if (isUsingNativeDetector) {
    const ponyfill = await getPonyfillDetector()
    const pass3 = extractValidBarcode(await ponyfill.detect(canvas))
    if (pass3) return pass3

    const pass4 = extractValidBarcode(await ponyfill.detect(rotatedCanvas))
    if (pass4) return pass4
  }

  return null
}

const handlePhotoSelected = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return

  if (isScanning.value) {
    stopScanner()
  }

  isProcessingPhoto.value = true
  try {
    const source = await loadImageFromFile(file)
    try {
      const normalCanvas = drawSourceToCanvas(source, false)
      const rotatedCanvas = drawSourceToCanvas(source, true)

      const validCode = await detectFromCanvasWithFallback(normalCanvas, rotatedCanvas)

      if (validCode) {
        triggerFeedback()
        await processBarcode(validCode)
      } else {
        $q.notify({
          message: 'No valid barcode found in the photo. Try getting closer with good lighting.',
          color: 'warning',
          position: 'top',
          icon: 'warning',
          timeout: 4000
        })
      }
    } finally {
      if (typeof source.close === 'function') {
        source.close()
      }
    }
  } catch (err) {
    console.error('Photo barcode scan failed:', err)
    $q.notify({
      message: 'Failed to process photo. Please try again.',
      color: 'negative',
      position: 'top',
      icon: 'error'
    })
  } finally {
    isProcessingPhoto.value = false
    if (photoInputRef.value) {
      photoInputRef.value.value = ''
    }
  }
}

const handleManualSearch = () => {
  if (isValidLength.value) {
    processBarcode(manualBarcode.value)
  } else {
    $q.notify({
      message: 'Please enter a valid 8, 12, or 13 digit barcode',
      color: 'warning',
      position: 'top',
      icon: 'warning'
    })
  }
}

const reset = () => {
  manualBarcode.value = ''
  stopScanner()
}

defineExpose({ reset })

onBeforeUnmount(() => {
  stopScanner()
})
</script>

<style scoped>
.barcode-scanner {
  width: 100%;
  max-width: 500px;
  margin-left: auto;
  margin-right: auto;
}

.scanner-viewport {
  position: relative;
  width: 100%;
  aspect-ratio: 4 / 3;
  max-height: 360px;
  border-radius: 12px;
  overflow: hidden;
  background: #000;
}

.scanner-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.scanner-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  pointer-events: none;
}

.scanner-mask-top,
.scanner-mask-bottom {
  flex: 1;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
}

.scanner-mask-bottom {
  align-items: flex-start;
  padding-top: 10px;
}

.scanner-middle-row {
  display: flex;
  height: 44%;
}

.scanner-mask-side {
  width: 4%;
  background: rgba(0, 0, 0, 0.45);
}

.scanner-aim-box {
  position: relative;
  flex: 1;
  border-radius: 6px;
}

.corner {
  position: absolute;
  width: 22px;
  height: 22px;
  border-color: #ffffff;
  border-style: solid;
  transition: border-color 0.15s ease;
}

.scanner-aim-box.is-confirming .corner {
  border-color: #21ba45;
}

.corner-tl {
  top: 0;
  left: 0;
  border-width: 3px 0 0 3px;
}

.corner-tr {
  top: 0;
  right: 0;
  border-width: 3px 3px 0 0;
}

.corner-bl {
  bottom: 0;
  left: 0;
  border-width: 0 0 3px 3px;
}

.corner-br {
  bottom: 0;
  right: 0;
  border-width: 0 3px 3px 0;
}

.laser-line {
  position: absolute;
  left: 6%;
  right: 6%;
  top: 50%;
  height: 2px;
  background: rgba(244, 67, 54, 0.85);
  box-shadow: 0 0 6px rgba(244, 67, 54, 0.8);
  transition: background-color 0.15s ease, box-shadow 0.15s ease;
}

.scanner-aim-box.is-confirming .laser-line {
  background: rgba(33, 186, 69, 0.95);
  box-shadow: 0 0 8px rgba(33, 186, 69, 0.9);
}

.scanner-hint {
  color: #ffffff;
  font-size: 12px;
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
}

.scanner-controls-top {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  gap: 8px;
  z-index: 2;
}

.scanner-controls-bottom {
  position: absolute;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 2;
}

.zoom-pill-group {
  background: rgba(0, 0, 0, 0.55);
}

.hidden {
  display: none;
}
</style>
