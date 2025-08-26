<template>
  <div class="google-map-container">
    <div ref="mapContainer" class="map-container"></div>
    <div v-if="loading" class="map-loading">
      <div class="spinner"></div>
      <p>지도를 불러오는 중...</p>
    </div>
    <div v-if="error" class="map-error">
      <p>{{ error }}</p>
    </div>
  </div>
</template>

<script>
import { GOOGLE_MAPS_API_KEY, MAP_DEFAULT_CONFIG, MARKER_DEFAULT_CONFIG } from '../config/maps';

export default {
  name: 'GoogleMap',
  props: {
    address: {
      type: String,
      required: true
    },
    title: {
      type: String,
      default: ''
    },
    zoom: {
      type: Number,
      default: 15
    }
  },
  data() {
    return {
      map: null,
      marker: null,
      geocoder: null,
      loading: true,
      error: null,
      mapLoaded: false
    };
  },
  async mounted() {
    await this.loadGoogleMapsAPI();
  },
  beforeUnmount() {
    // 컴포넌트 언마운트 시 정리
    if (this.map) {
      // Google Maps 인스턴스 정리
      this.map = null;
    }
  },
  methods: {
    // Google Maps API 로드
    loadGoogleMapsAPI() {
      return new Promise((resolve, reject) => {
        // 이미 로드되어 있는지 확인
        if (window.google && window.google.maps) {
          this.mapLoaded = true;
          this.initializeMap();
          resolve();
          return;
        }

        // API 키가 설정되어 있는지 확인
        if (!GOOGLE_MAPS_API_KEY || GOOGLE_MAPS_API_KEY === 'YOUR_GOOGLE_MAPS_API_KEY') {
          this.error = 'Google Maps API 키가 설정되지 않았습니다.';
          this.loading = false;
          reject(new Error('API key not configured'));
          return;
        }

        // Google Maps API 스크립트 로드
        const script = document.createElement('script');
        script.src = `https://maps.googleapis.com/maps/api/js?key=${GOOGLE_MAPS_API_KEY}&libraries=places`;
        script.async = true;
        script.defer = true;
        
        script.onload = () => {
          this.mapLoaded = true;
          this.initializeMap();
          resolve();
        };
        
        script.onerror = () => {
          this.error = 'Google Maps API를 불러오는데 실패했습니다.';
          this.loading = false;
          reject(new Error('Failed to load Google Maps API'));
        };
        
        document.head.appendChild(script);
      });
    },

    // 지도 초기화
    initializeMap() {
      try {
        this.loading = true;
        this.error = null;

        // Geocoder 초기화
        this.geocoder = new google.maps.Geocoder();
        
        // 주소를 좌표로 변환
        this.geocoder.geocode({ address: this.address }, (results, status) => {
          if (status === 'OK' && results[0]) {
            const location = results[0].geometry.location;
            
            // 지도 생성
            this.map = new google.maps.Map(this.$refs.mapContainer, {
              ...MAP_DEFAULT_CONFIG,
              center: location,
              zoom: this.zoom
            });

            // 마커 생성
            this.marker = new google.maps.Marker({
              ...MARKER_DEFAULT_CONFIG,
              animation: google.maps.Animation.DROP, // 동적으로 애니메이션 설정
              position: location,
              map: this.map,
              title: this.title || this.address
            });

            // 정보창 생성 (선택사항)
            if (this.title) {
              const infoWindow = new google.maps.InfoWindow({
                content: `<div style="padding: 10px;"><strong>${this.title}</strong><br>${this.address}</div>`
              });

              // 마커 클릭 시 정보창 표시
              this.marker.addListener('click', () => {
                infoWindow.open(this.map, this.marker);
              });
            }

            this.loading = false;
          } else {
            this.error = '주소를 찾을 수 없습니다.';
            this.loading = false;
          }
        });
      } catch (err) {
        console.error('지도 초기화 오류:', err);
        this.error = '지도를 불러오는데 실패했습니다.';
        this.loading = false;
      }
    },

    // 지도 새로고침 (주소 변경 시)
    refreshMap() {
      if (this.mapLoaded) {
        this.initializeMap();
      }
    }
  },
  watch: {
    // 주소가 변경되면 지도 새로고침
    address() {
      this.refreshMap();
    }
  }
};
</script>

<style scoped>
.google-map-container {
  position: relative;
  width: 100%;
  height: 300px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.map-container {
  width: 100%;
  height: 100%;
  background: #f8f9fa;
}

.map-loading {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.map-loading .spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top: 4px solid #2563eb;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

.map-loading p {
  color: #64748b;
  font-size: 14px;
  margin: 0;
}

.map-error {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #fef2f2;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  border: 1px solid #fecaca;
  border-radius: 12px;
}

.map-error p {
  color: #dc2626;
  font-size: 14px;
  text-align: center;
  margin: 0;
  padding: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 모바일 반응형 */
@media (max-width: 768px) {
  .google-map-container {
    height: 250px;
  }
}
</style>
