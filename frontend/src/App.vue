<template>
  <div class="app-layout">
    <aside class="sidebar">
      <h2>Search</h2>
      <div class="input-group">
        <label>Search Query</label>
        <input v-model="searchQuery" type="text" placeholder="Search your library..." />
      </div>
      
      <div class="input-group">
        <label>City</label>
        <input v-model="city" type="text" placeholder="Enter city name..." />
      </div>

      <hr />

      <h2>Date Range</h2>
      <div class="input-group">
        <label>Start Date</label>
        <input v-model="dateStart" type="date" />
      </div>
      
      <div class="input-group">
        <label>End Date</label>
        <input v-model="dateEnd" type="date" />
      </div>

      <button @click="performSearch" class="btn-primary" :disabled="loading">
        {{ loading ? 'Searching...' : 'Search' }}
      </button>
    </aside>

    <main class="main-content">
      <h1 class="page-title">{{ isSearching ? 'Search Results' : 'On This Day' }}</h1>

      <div v-if="loading" class="loader">Loading...</div>

      <div v-else-if="isSearching">
        <div v-if="images.length === 0" class="info-box">
          No images found for your search.
        </div>
        <div v-else>
          <div class="pagination">
            <button @click="isSearching = false" class="btn-nav btn-back">← Back to On This Day</button>
            <div class="pagination-center">
              <button @click="page--" :disabled="page === 0" class="btn-nav">← Previous</button>
              <span class="page-info">Page {{ page + 1 }} of {{ totalPages }}</span>
              <button @click="page++" :disabled="page >= totalPages - 1" class="btn-nav">Next →</button>
            </div>
          </div>

          <div class="image-grid">
            <div v-for="imgPath in paginatedImages" :key="imgPath" class="image-card" @click="loadDetails(imgPath)">
              <img :src="getImageUrl(imgPath)" loading="lazy" />
            </div>
          </div>
        </div>
      </div>

      <div v-else>
        <div v-if="!onThisDayImages || onThisDayImages.length === 0" class="info-box">
          No images found for today.
        </div>
        <div v-else class="on-this-day-list">
          <div v-for="yearData in onThisDayImages" :key="yearData[0]" class="year-section">
            <h3>{{ yearData[0] }}</h3>
            <div class="image-grid">
              <div v-for="imgPath in yearData[1]" :key="imgPath" class="image-card" @click="loadDetails(imgPath)">
                <img :src="getImageUrl(imgPath)" loading="lazy" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <aside class="details-panel" :class="{ 'collapsed': !showDetails }">
      <div class="details-header">
        <h3>Image Details</h3>
        <button @click="showDetails = !showDetails" class="btn-toggle-details">
          {{ showDetails ? '−' : '+' }}
        </button>
      </div>
      <div v-if="showDetails">
        <div v-if="currentImage">
          <div class="detail-item">
            <strong>File Path:</strong>
            <div class="file-path-container">
              <code>{{ currentImage }}</code>
              <button @click="copyFilePath" class="btn-copy" title="Copy file path">
                <i class="fa fa-copy"></i>
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
        <div v-else class="info-box">
          Click 'Details' on an image to see its details here.
        </div>
      </div>
    </aside>
  </div>
</template>

<script setup>
import {
  searchQuery,
  city,
  dateStart,
  dateEnd,
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
  copyFilePath,
  setupApp
} from './utils/app'

setupApp()
</script>