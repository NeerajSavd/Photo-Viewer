<template>
  <div class="app-layout">
    <aside class="sidebar">
      <nav class="sidebar-nav">
        <a href="#" class="nav-item" @click.prevent="currentPage = 'library'">
          <i class="fa fa-folder nav-icon"></i>
          <span class="nav-text">Library</span>
        </a>
        <a href="#" class="nav-item" @click.prevent="currentPage = 'onThisDay'">
          <i class="fa fa-calendar nav-icon"></i>
          <span class="nav-text">On This Day</span>
        </a>
        <a href="#" class="nav-item" @click.prevent="currentPage = 'search'">
          <i class="fa fa-search nav-icon"></i>
          <span class="nav-text">Search</span>
        </a>
        <a href="#" class="nav-item" @click.prevent="currentPage = 'map'">
          <i class="fa fa-map nav-icon"></i>
          <span class="nav-text">Map</span>
        </a>
        <a href="#" class="nav-item" @click.prevent="currentPage = 'stats'">
          <i class="fa fa-bar-chart nav-icon"></i>
          <span class="nav-text">Stats</span>
        </a>
      </nav>
    </aside>
    <main class="main-content">
      <div class="search-inputs">
        <input v-model="searchQuery" type="text" placeholder="Search your library..." />
        <button @click="showMore = !showMore" class="btn-secondary">
          {{ showMore ? 'Less' : 'More' }}
        </button>
        <button @click="performSearch" class="btn-primary" :disabled="loading">
          {{ loading ? 'Searching...' : 'Search' }}
        </button>
      </div>
      <div v-if="showMore" class="advanced-search">
        <input v-model="city" type="text" placeholder="Enter city name..." />
        <span>From: </span>
        <input v-model="dateStart" type="date" />
        <span>To: </span>
        <input v-model="dateEnd" type="date" />
      </div>

      <div v-if="loading" class="loader">Loading...</div>

      <div v-else-if="currentPage === 'search'">
        <h1 class="page-title">Search Results</h1>
        <div v-if="images.length === 0" class="info-box">
          No images found for your search.
        </div>
        <div v-else>
          <div class="pagination">
            <div class="pagination-center">
              <button @click="page--" :disabled="page === 0" class="btn-nav">
                <svg class="arrow-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M15 18l-6-6 6-6"/>
                </svg>
                <span>Previous</span>
              </button>
              <span class="page-info">Page {{ page + 1 }} of {{ totalPages }}</span>
              <button @click="page++" :disabled="page >= totalPages - 1" class="btn-nav">
                <span>Next</span>
                <svg class="arrow-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M9 18l6-6-6-6"/>
                </svg>
              </button>
            </div>
          </div>

          <div class="image-grid">
            <div v-for="imgPath in paginatedImages" :key="imgPath" class="image-card" @click="loadDetails(imgPath)">
              <img :src="getImageUrl(imgPath)" loading="lazy" />
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="currentPage === 'onThisDay'">
        <h1 class="page-title">On This Day</h1>
        <div class="date-buttons-container">
          <button
            v-for="day in past7Days"
            :key="day.date"
            @click="selectDate(day.date)"
            :class="{ 'active': isSelectedDate(day.date) }"
            class="date-btn"
          >
            <div class="date-day">{{ day.dayName }}</div>
            <div class="date-full">{{ day.fullDate }}</div>
          </button>
        </div>
        <div v-if="!onThisDayImages || onThisDayImages.length === 0" class="info-box">
          No images found for the selected date.
        </div>
        <div v-else class="on-this-day-list">
          <div v-for="yearData in onThisDayImages" :key="yearData[0]" class="year-section">
            <h2>{{ yearData[0] }}</h2>
            <div class="image-grid">
              <div v-for="imgPath in yearData[1]" :key="imgPath" class="image-card" @click="loadDetails(imgPath)">
                <img :src="getImageUrl(imgPath)" loading="lazy" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="currentPage === 'library'">
        <h1 class="page-title">Library</h1>
        <div v-if="recentImages.length === 0" class="info-box">
          No recent images found.
        </div>
        <div v-else class="image-grid">
          <div v-for="imgPath in recentImages" :key="imgPath" class="image-card" @click="loadDetails(imgPath)">
            <img :src="getImageUrl(imgPath)" loading="lazy" />
          </div>
        </div>
      </div>

      <div v-else-if="currentPage === 'map'">
        <h1 class="page-title">Map</h1>
        <div class="map-container">
          <div id="map" ref="mapContainer"></div>
        </div>
      </div>

      <div v-else-if="currentPage === 'stats'">
        <h1 class="page-title">Stats</h1>
        <div class="stats-container">
          <div v-for="(value, key) in libraryStats" :key="key" class="stats-section">
            <h3>{{ formatStatKey(key) }}</h3>
            <div v-if="Array.isArray(value)" class="list-container">
              <span v-for="(item, idx) in value" :key="idx" class="list-item">
                {{ formatStatValue(item) }}
              </span>
            </div>
            <div v-else-if="typeof value === 'object'" class="object-container">
              <span v-for="(val, k) in value" :key="k" class="object-item">
                {{ k }}: {{ val }}
              </span>
            </div>
            <div v-else class="value-container">
              {{ value }}
            </div>
          </div>
        </div>
        <button @click="syncLibrary" class="btn-primary" :disabled="loading">
          {{ loading ? 'Syncing...' : 'Sync' }}
        </button>
      </div>
    </main>

    <div v-if="showDetails && currentImage" class="image-modal">
      <button @click="closeModal" class="btn-close-modal">&times;</button>
      <div class="modal-content">
        <div class="modal-image-container">
          <img :src="getImageUrl(currentImage, 'full')" class="full-image" />
        </div>
        <div class="modal-details">
          <h3>Image Details</h3>
          <div class="detail-item">
            <strong>File Path:</strong>
            <div class="file-path-container">
              <code>{{ currentImage }}</code>
              <button @click="copyFilePath" class="btn-copy" title="Copy file path">
                <i class="fa fa-clipboard"></i>
              </button>
            </div>
          </div>
          <div class="detail-item">
            <strong>Timestamp:</strong> {{ currentDetails.timestamp || 'N/A' }}
          </div>
          <div class="detail-item">
            <strong>Camera:</strong> {{ currentDetails.camera_model || 'N/A' }}
          </div>
          <div class="detail-item">
            <strong>Latitude:</strong> {{ currentDetails.latitude || 'N/A' }}
          </div>
          <div class="detail-item">
            <strong>Longitude:</strong> {{ currentDetails.longitude || 'N/A' }}
          </div>
          <div class="detail-item">
            <strong>Tags:</strong>
            <ul v-if="currentDetails.tags && currentDetails.tags.length">
              <li v-for="tag in currentDetails.tags" :key="tag">{{ tag }}</li>
            </ul>
            <span v-else><em>No tags found</em></span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
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
  currentImage,
  currentDetails,
  showDetails,
  totalPages,
  paginatedImages,
  getImageUrl,
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
} from './utils/app'
import { setupMap, mapContainer, markers } from './utils/map'
import { onMounted, watch } from 'vue'

setupApp()

onMounted(() => {
  watch(currentPage, (newPage) => {
    if (newPage === 'map') {
      setTimeout(() => {
        setupMap()
      }, 100)
    } else if (newPage === 'stats') {
      loadStats()
    }
  })
})

const formatStatKey = (key) => {
  return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatStatValue = (item) => {
  if (Array.isArray(item)) {
    return `${item[0]} (${item[1]})`
  }
  return item
}
</script>