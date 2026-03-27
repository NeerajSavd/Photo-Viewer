import { ref, computed, onMounted } from 'vue'
import { copyToClipboard } from './clipboard'

const API_BASE = 'http://localhost:8000/api'

// State
const searchQuery = ref('')
const city = ref('')
const dateStart = ref('')
const dateEnd = ref('')
const showMore = ref(false)
const currentPage = ref('library') // 'onThisDay', 'search', 'library', 'map', 'stats'
const loading = ref(false)
const selectedDate = ref(new Date().toISOString().split('T')[0])
const statsLoading = ref(false)
const libraryStats = ref({})

const images = ref([])
const onThisDayImages = ref([])
const recentImages = ref([])
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

// Past 7 days date buttons
const past7Days = computed(() => {
  const days = []
  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
  const today = new Date()
  
  for (let i = 6; i >= 0; i--) {
    const date = new Date(today)
    date.setDate(today.getDate() - i)
    
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const fullDate = `${month}/${day}`
    
    days.push({
      date: fullDate,
      dayName: dayNames[date.getDay()],
      fullDate: fullDate
    })
  }
  
  return days
})

// Methods
const getImageUrl = (path, size = 'thumb') => `${API_BASE}/image?path=${encodeURIComponent(path)}&size=${size}`

const loadOnThisDay = async (date = null) => {
  try {
    const url = date ? `${API_BASE}/on-this-day?date=${date}` : `${API_BASE}/on-this-day`
    const res = await fetch(url)
    const data = await res.json()
    onThisDayImages.value = data.data
  } catch (err) {
    console.error("Failed to load On This Day:", err)
  }
}

const loadRecent = async () => {
  try {
    const res = await fetch(`${API_BASE}/recent`)
    const data = await res.json()
    recentImages.value = data.data || []
  } catch (err) {
    console.error("Failed to load recent images:", err)
  }
}

const performSearch = async () => {
  currentPage.value = 'search'
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

const loadStats = async () => {
  statsLoading.value = true
  try {
    const res = await fetch(`${API_BASE}/stats`)
    const data = await res.json()
    libraryStats.value = data.data || {}
  } catch (err) {
    console.error("Failed to load stats:", err)
  } finally {
    statsLoading.value = false
  }
}

const syncLibrary = async () => {
  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/sync`, { method: 'POST' })
    const data = await res.json()
    if (data.error) {
      alert('Sync failed: ' + data.error)
    } else {
      alert('Sync successful!')
      loadStats()
    }
  } catch (err) {
    console.error("Sync failed:", err)
    alert('Sync failed')
  } finally {
    loading.value = false
  }
}

const setupApp = () => {
  onMounted(() => {
    loadOnThisDay()
    loadRecent()
  })
}

const selectDate = (date) => {
  selectedDate.value = date
  loadOnThisDay(date)
}

const isSelectedDate = (date) => {
  return selectedDate.value === date
}

export {
  searchQuery,
  city,
  dateStart,
  dateEnd,
  showMore,
  currentPage,
  loading,
  statsLoading,
  libraryStats,
  images,
  onThisDayImages,
  recentImages,
  page,
  IMAGES_PER_PAGE,
  currentImage,
  currentDetails,
  showDetails,
  totalPages,
  paginatedImages,
  getImageUrl,
  loadOnThisDay,
  loadRecent,
  performSearch,
  loadDetails,
  closeModal,
  copyFilePath,
  loadStats,
  syncLibrary,
  setupApp,
  past7Days,
  selectDate,
  isSelectedDate
}