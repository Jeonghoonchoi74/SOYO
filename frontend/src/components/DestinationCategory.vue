<template>
  <div class="destcat-container">
    <button class="bookmark-btn" @click="goBookmark">좋아요/북마크</button>
    <h2 class="title">{{ $t('dest_title') }}</h2>
    <p class="subtitle">{{ $t('dest_subtitle') }}</p>
    <input
      v-model="destination"
      class="destination-input"
      type="text"
      :placeholder="$t('dest_input_placeholder')"
    />
    <div class="category-grid">
      <label v-for="cat in categories" :key="cat.value" class="category-item" :class="{ active: selectedCategories.includes(cat.value) }">
        <input type="checkbox" v-model="selectedCategories" :value="cat.value" class="hidden-checkbox" />
        <span class="icon">{{ cat.icon }}</span>
        <span>{{ cat.label }}</span>
      </label>
    </div>
    <button class="next-btn" :disabled="!canProceed" @click="next">{{ $t('dest_next_btn') }}</button>
  </div>

  <!-- 위치 권한 요청 모달 -->
  <div v-if="showLocationModal" class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>위치 정보 요청</h3>
        <button class="close-btn" @click="closeModal">&times;</button>
      </div>
      <div class="modal-body">
        <h4>원활한 사용을 위해 위치 정보를 요구합니다</h4>
        <!--<p>현재 위치를 기반으로 더 정확한 여행 추천을 제공하고, 방문한 장소를 자동으로 확인할 수 있습니다.</p>-->
        
        <!--<div class="benefits">
          <div class="benefit-item">
            <span class="benefit-icon">🎯</span>
            <span>현재 위치 기반 맞춤 추천</span>
          </div>-->
          <div class="benefit-item">
            <span class="benefit-icon">✅</span>
            <span>방문한 장소 자동 확인</span>
          </div>
         <!-- <div class="benefit-item">
            <span class="benefit-icon">🗺️</span>
            <span>근처 관광지 알림</span>
          </div>
        </div>-->
      </div>
      <div class="modal-footer">
        <button class="btn-secondary" @click="denyLocation">나중에</button>
        <button class="btn-primary" @click="requestLocation">위치 정보 허용</button>
      </div>
    </div>
  </div>
</template>

<script>
import { i18nState, $t } from '../i18n';
export default {
  name: 'DestinationCategory',
  data() {
    return {
      destination: '',
      categories: [
        { value: 'food', label: $t('dest_category_food'), icon: '🍔' },
        { value: 'shopping', label: $t('dest_category_shopping'), icon: '🛍️' },
        { value: 'culture', label: $t('dest_category_culture'), icon: '🏛️' },
        { value: 'transport', label: $t('dest_category_transport'), icon: '🚌' },
      ],
      selectedCategories: [],
      showLocationModal: false,
      locationPermission: null,
    };
  },
  computed: {
    canProceed() {
      return this.destination.trim() && this.selectedCategories.length > 0;
    },
    $t() { return $t; },
  },
  async mounted() {
    await this.checkLocationPermission();
    // 권한이 이미 허용된 경우 위도/경도 콘솔 출력
    if (this.locationPermission === 'granted') {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition((position) => {
          console.log('[테스트] 현재 위도:', position.coords.latitude);
          console.log('[테스트] 현재 경도:', position.coords.longitude);
        });
      }
    }
  },
  methods: {
    goBookmark() {
      this.$router.push('/bookmarks');
    },
    next() {
      this.$router.push('/preference');
    },
    
    // 위치 권한 확인
    async checkLocationPermission() {
      if (!navigator.geolocation) {
        console.log('브라우저가 위치 정보를 지원하지 않습니다.');
        return;
      }

      try {
        // 권한 상태 확인 (Chrome 50+, Firefox 55+)
        if (navigator.permissions && navigator.permissions.query) {
          const permission = await navigator.permissions.query({ name: 'geolocation' });
          this.locationPermission = permission.state;
          
          // 권한 변화 감지
          permission.onchange = () => {
            if (permission.state === 'granted') {
              window.location.reload(); // 새로고침(모달 자동 닫힘)
            }
          };

          if (permission.state === 'granted') {
            console.log('이미 위치 권한이 허용되어 있습니다.');
            return;
          } else if (permission.state === 'denied') {
            console.log('위치 권한이 거부되어 있습니다.');
            return;
          }
        }
        
        // 권한 상태를 확인할 수 없는 경우 모달 표시
        this.showLocationModal = true;
      } catch (error) {
        console.log('권한 상태 확인 중 오류:', error);
        // 오류 발생 시 모달 표시
        this.showLocationModal = true;
      }
    },
    
    // 위치 권한 요청
    async requestLocation() {
      try {
        const position = await this.getCurrentPosition();
        console.log('위치 권한 허용됨:', position);
        this.showLocationModal = false;
        
        // 위치 정보를 로컬 스토리지에 저장
        localStorage.setItem('locationPermission', 'granted');
        localStorage.setItem('userLocation', JSON.stringify({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          timestamp: position.timestamp
        }));
        
      } catch (error) {
        console.error('위치 권한 요청 실패:', error);
        this.showLocationModal = false;
        
        if (error.code === 1) {
          alert('위치 접근이 거부되었습니다. 브라우저 설정에서 위치 접근을 허용해주세요.');
        }
      }
    },
    
    // 현재 위치 가져오기
    getCurrentPosition() {
      return new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(
          resolve,
          reject,
          {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 60000
          }
        );
      });
    },
    
    // 위치 권한 거부
    denyLocation() {
      this.showLocationModal = false;
      localStorage.setItem('locationPermission', 'denied');
      console.log('사용자가 위치 권한을 거부했습니다.');
    },
    
    // 모달 닫기
    closeModal() {
      this.showLocationModal = false;
    }
  },
};
</script>

<style scoped>
.destcat-container {
  width: 800px;
  margin: 60px auto;
  padding: 64px 80px 96px 80px;
  border-radius: 32px;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.bookmark-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background: #fff;
  color: #2563eb;
  border: 2px solid #2563eb;
  border-radius: 10px;
  padding: 0.7rem 1.5rem;
  font-size: 1.05rem;
  font-weight: 700;
  cursor: pointer;
  z-index: 10;
}
.bookmark-btn:hover {
  background: #2563eb;
  color: #fff;
}

.title {
  font-size: 2rem;
  font-weight: 800;
  margin-bottom: 3rem;
  text-align: center;
  color: #1e293b;
}

.subtitle {
  font-size: 1rem;
  color: #64748b;
  margin-bottom: 2.5rem;
}

/* 목적지 입력창 */
.destination-input {
  width: 100%;
  max-width: 500px;
  padding: 1.2rem 1.5rem;
  font-size: 1.2rem;
  border: 2px solid #cbd5e1;
  border-radius: 14px;
  margin-bottom: 2.5rem;
  background: #fff;
  box-sizing: border-box;
  color: #1e293b;
}

.destination-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

.destination-input::placeholder {
  color: #64748b;
  opacity: 1;
}

/* 카테고리 선택 영역 */
.category-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  width: 100%;
  max-width: 360px;
  margin-bottom: 3rem;
}

.category-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #fff;
  border: 1.5px solid #e2e8f0;
  border-radius: 16px;
  padding: 1.5rem 1rem;
  font-size: 1rem;
  font-weight: 600;
  color: #334155;
  cursor: pointer;
  user-select: none;
  transition: all 0.2s ease-in-out;
}

.category-item:hover {
  border-color: #a5b4fc;
  transform: translateY(-2px);
}

.category-item.active {
  background-color: #e0e7ff; /* 연한 파란색 배경 */
  border-color: #3b82f6; /* 파란색 테두리 */
  color: #1e3a8a; /* 진한 파란색 텍스트 */
}

.icon {
  font-size: 1.8rem;
  margin-bottom: 0.5rem;
}

.hidden-checkbox {
  display: none; /* 실제 체크박스는 숨김 */
}

/* 다음 버튼 */
.next-btn {
  width: 100%;
  max-width: 420px;
  padding: 1.4rem 0;
  background: #2563eb;
  color: #fff;
  font-size: 1.3rem;
  font-weight: 800;
  border: none;
  border-radius: 16px;
  box-shadow: 0 6px 24px rgba(37,99,235,0.12);
  cursor: pointer;
  transition: all 0.2s;
}

.next-btn:hover {
  background: #1d4ed8;
  transform: translateY(-2px);
}
.next-btn:active {
  background: #1e40af;
  transform: translateY(0);
}
.next-btn:disabled {
  background: #cbd5e1;
  color: #fff;
  cursor: not-allowed;
}

/* 모달 스타일 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: white;
  border-radius: 20px;
  padding: 0;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-50px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 700;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.8rem;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.modal-body {
  padding: 24px;
  text-align: center;
}

.location-icon {
  font-size: 3rem;
  margin-bottom: 16px;
}

.modal-body h4 {
  margin: 0 0 12px 0;
  font-size: 1.3rem;
  color: #1e293b;
  font-weight: 600;
}

.modal-body p {
  margin: 0 0 24px 0;
  color: #64748b;
  line-height: 1.6;
  font-size: 1rem;
}

.benefits {
  background: #f8fafc;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
}

.benefit-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  font-size: 0.95rem;
  color: #475569;
}

.benefit-item:last-child {
  margin-bottom: 0;
}

.benefit-icon {
  font-size: 1.2rem;
  margin-right: 12px;
  width: 24px;
  text-align: center;
}

.modal-footer {
  padding: 20px 24px;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
}

.btn-secondary {
  background: #e2e8f0;
  color: #475569;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #cbd5e1;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.btn-primary:active {
  transform: translateY(0);
}

/* 모바일 반응형 */
@media (max-width: 768px) {
  .modal-content {
    width: 95%;
    margin: 20px;
  }
  
  .modal-header {
    padding: 16px 20px;
  }
  
  .modal-body {
    padding: 20px;
  }
  
  .modal-footer {
    padding: 16px 20px;
    flex-direction: column;
  }
  
  .btn-secondary,
  .btn-primary {
    width: 100%;
    padding: 14px 20px;
  }
}
</style>