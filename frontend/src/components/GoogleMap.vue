<template>
  <div class="google-map-container">
    <div ref="mapContainer" class="map-container" @click="openGoogleMaps"></div>
    <div v-if="loading" class="map-loading">
      <div class="spinner"></div>
      <p>{{ $t('map_loading') }}</p>
    </div>
    <div v-if="error" class="map-error">
      <p>{{ error }}</p>
    </div>
    <div class="map-overlay" @click="openGoogleMaps">
      <div class="overlay-content">
        <span class="overlay-text">{{ $t('map_google_maps_view') }}</span>
        <span class="overlay-icon">🗺️</span>
      </div>
    </div>

  </div>
</template>

<script>
import { GOOGLE_MAPS_API_KEY, MAP_DEFAULT_CONFIG, MARKER_DEFAULT_CONFIG } from '../config/maps';
import { $t } from '../i18n';

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
      mapLoaded: false,
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
    $t,
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
          this.error = this.$t('map_api_key_error');
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
          this.error = this.$t('map_load_error');
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
            this.error = this.$t('map_address_not_found');
            this.loading = false;
          }
        });
             } catch (err) {
         console.error('지도 초기화 오류:', err);
         this.error = this.$t('map_error');
         this.loading = false;
       }
    },

         // 지도 새로고침 (주소 변경 시)
     refreshMap() {
       if (this.mapLoaded) {
         this.initializeMap();
       }
     },
     
     // Google Maps 앱/웹사이트로 이동
     openGoogleMaps() {
       try {
         // 주소를 URL 인코딩
         const encodedAddress = encodeURIComponent(this.address);
         
         // Google Maps URL 생성
         const googleMapsUrl = `https://www.google.com/maps/search/?api=1&query=${encodedAddress}`;
         
         // 새 탭에서 Google Maps 열기
         window.open(googleMapsUrl, '_blank');
         
         console.log('Google Maps로 이동:', googleMapsUrl);
       } catch (error) {
         console.error('Google Maps 열기 실패:', error);
         alert('Google Maps를 열 수 없습니다.');
       }
     },
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

/* Google Maps 오버레이 */
.map-overlay {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  padding: 8px 12px;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  transition: all 0.2s ease;
  z-index: 20;
  backdrop-filter: blur(4px);
}

.map-overlay:hover {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.overlay-content {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;
  color: #2563eb;
}

.overlay-text {
  white-space: nowrap;
}

.overlay-icon {
  font-size: 14px;
}

/* 모바일 반응형 */
@media (max-width: 768px) {
  .google-map-container {
    height: 250px;
  }
  
  .map-overlay {
    top: 8px;
    right: 8px;
    padding: 6px 10px;
  }
  
  .overlay-content {
    font-size: 11px;
    gap: 4px;
  }
  
  .overlay-icon {
    font-size: 12px;
  }
}



/* 모바일 반응형 */
@media (max-width: 768px) {
  .help-btn {
    width: 40px;
    height: 40px;
    top: 15px;
    left: 15px;
    border: 2px solid white;
    font-size: 16px;
  }

  .help-btn svg {
    width: 18px;
    height: 18px;
    stroke: white;
    fill: none;
  }
  
  .tutorial-modal {
    max-width: 95vw;
    max-height: 85vh;
  }
  
  .tutorial-content {
    padding: 16px 20px;
    max-height: 65vh;
  }
  
  .tutorial-step {
    gap: 12px;
    margin-bottom: 20px;
    padding-bottom: 16px;
  }
  
  .step-number {
    width: 28px;
    height: 28px;
    font-size: 13px;
  }
  
  .step-content h4 {
    font-size: 15px;
  }
  
  .step-content p {
    font-size: 13px;
  }
}
</style>
