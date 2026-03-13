import { ref, onMounted, watch } from 'vue';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

const mapContainer = ref(null);
let map = null;
let markers = [];

const API_BASE = 'http://localhost:8000/api'

const setupMap = async () => {
  // Remove existing markers if any
  markers.forEach(marker => map.removeLayer(marker));
  markers = [];

  // Initialize the map
  map = L.map(mapContainer.value).setView([39.8283, -98.5795], 4);

  // Add OpenStreetMap tiles
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors'
  }).addTo(map);

  try {
    const response = await fetch(`${API_BASE}/map`);
    const result = await response.json();
    const data = result.data;

    data.forEach(location => {
      const [lat, lng, numImages] = location;

      const customPin = L.divIcon({
        className: 'custom-pin-wrapper',
        html: `<div class="pin-marker">
                 <span class="pin-text">${numImages}</span>
               </div>`,
        iconSize: [30, 42],
        iconAnchor: [15, 42]
      });

      const marker = L.marker([lat, lng], { icon: customPin }).addTo(map);
      markers.push(marker);
    });

  } catch (error) {
    console.error('Error fetching map data:', error);
  }
}

export { setupMap, mapContainer, markers }