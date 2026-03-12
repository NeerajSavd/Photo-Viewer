import { ref, computed, onMounted } from 'vue'
import { copyToClipboard } from './clipboard'

const API_BASE = 'http://localhost:8000/api'

// State
const searchQuery = ref('')
const city = ref('')
const dateStart = ref('')
const dateEnd = ref('')
const showMore = ref(false)
const isSearching = ref(false)
const loading = ref(false)

const images = ref([])
const onThisDayImages = ref([])
const page = ref(0)
const IMAGES_PER_PAGE = 20

const currentImage = ref(null)
const currentDetails = ref({})
const showDetails = ref(false)

// Computed
const totalPages = computed(() => Math.ceil(images.value.length / IMAGES_PER_PAGE))
const paginatedImages = computed(() => {
  const start = page.value * IMAGES_PER_PAGE
  return images.value.slice(start, start + IMAGES_PER_PAGE)
})

// Methods
const getImageUrl = (path, size = 'thumb') => `${API_BASE}/image?path=${encodeURIComponent(path)}&size=${size}`

const loadOnThisDay = async () => {
  try {
    const res = await fetch(`${API_BASE}/on-this-day`)
    const data = await res.json()
    onThisDayImages.value = data.data
  } catch (err) {
    console.error("Failed to load On This Day:", err)
  }
}

const performSearch = async () => {
  isSearching.value = true
  loading.value = true
  page.value = 0
  
  const params = new URLSearchParams()
  if (searchQuery.value) params.append('query', searchQuery.value)
  if (city.value) params.append('city', city.value)
  if (dateStart.value) params.append('dateStart', dateStart.value)
  if (dateEnd.value) params.append('dateEnd', dateEnd.value)

  try {
    const res = await fetch(`${API_BASE}/search?${params.toString()}`)
    const data = await res.json()
    images.value = data.data || []
  } catch (err) {
    console.error("Search failed:", err)
  } finally {
    loading.value = false
  }
}

const loadDetails = async (imgPath) => {
  currentImage.value = imgPath
  showDetails.value = true
  try {
    const res = await fetch(`${API_BASE}/details?path=${encodeURIComponent(imgPath)}`)
    const data = await res.json()
    currentDetails.value = data.data
  } catch (err) {
    console.error("Failed to load details:", err)
  }
}

const closeModal = () => {
  showDetails.value = false
  currentImage.value = null
}

const copyFilePath = async () => {
  try {
    await copyToClipboard(currentImage.value)
  } catch (err) {
    console.error("Failed to copy:", err)
  }
}

const setupApp = () => {
  onMounted(() => {
    loadOnThisDay()
  })
}

export {
  searchQuery,
  city,
  dateStart,
  dateEnd,
  showMore,
  isSearching,
  loading,
  images,
  onThisDayImages,
  page,
  IMAGES_PER_PAGE,
  currentImage,
  currentDetails,
  showDetails,
  totalPages,
  paginatedImages,
  getImageUrl,
  loadOnThisDay,
  performSearch,
  loadDetails,
  closeModal,
  copyFilePath,
  setupApp
}