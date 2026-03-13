<template>
  <div class="app-layout">
    <aside class="sidebar">
      <nav class="sidebar-nav">
        <a href="#" class="nav-item" @click.prevent="currentPage = 'onThisDay'">
          <i class="fa fa-calendar nav-icon"></i>
          <span class="nav-text">On This Day</span>
        </a>
        <a href="#" class="nav-item" @click.prevent="currentPage = 'search'">
          <i class="fa fa-search nav-icon"></i>
          <span class="nav-text">Search</span>
        </a>
        <a href="#" class="nav-item" @click.prevent="currentPage = 'recent'">
          <i class="fa fa-folder nav-icon"></i>
          <span class="nav-text">Recent</span>
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
            <button @click="currentPage = 'onThisDay'" class="btn-nav btn-back">
              <svg class="arrow-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M15 18l-6-6 6-6"/>
              </svg>
              <span>Back</span>
            </button>
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
        <div v-if="!onThisDayImages || onThisDayImages.length === 0" class="info-box">
          No images found for today.
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

      <div v-else-if="currentPage === 'recent'">
        <h1 class="page-title">Recent Images</h1>
        <div class="info-box">Recent images will be displayed here</div>
      </div>

      <div v-else-if="currentPage === 'map'">
        <h1 class="page-title">Map</h1>
        <div class="map-container">
          <div id="map" ref="mapContainer"></div>
        </div>
      </div>

      <div v-else-if="currentPage === 'stats'">
        <h1 class="page-title">Stats</h1>
        <div class="info-box">Statistics will be displayed here</div>
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
            <strong>Camera Model:</strong> {{ currentDetails.camera_model || 'N/A' }}
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
    }
  })
})
</script>