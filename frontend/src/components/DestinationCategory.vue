<template>
  <div class="destination-page">
    <!-- 도움말 버튼 -->
    <button class="help-btn" @click="showTutorial">
      ?
    </button>

    <div class="destination-content">
      <div class="destination-header">
        <button class="bookmark-btn" @click="goBookmark">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
          </svg>
          좋아요/북마크
        </button>
        <h2 class="title">{{ $t('dest_title') }}</h2>
        <p class="subtitle">{{ $t('dest_subtitle') }}</p>
      </div>
      
      <div class="destination-form">
        <div class="form-group">
          <label for="destination">여행지</label>
          <input
            id="destination"
            v-model="destination"
            class="destination-input"
            type="text"
            :placeholder="$t('dest_input_placeholder')"
          />
        </div>
        
        <div class="form-group">
          <label>관심 카테고리</label>
          <div class="category-grid">
            <label v-for="cat in categories" :key="cat.value" class="category-item" :class="{ active: selectedCategories.includes(cat.value) }">
              <input type="checkbox" v-model="selectedCategories" :value="cat.value" class="hidden-checkbox" />
              <span class="icon">{{ cat.icon }}</span>
              <span class="label">{{ cat.label }}</span>
            </label>
          </div>
        </div>
        
        <button class="next-btn" :disabled="!canProceed" @click="next">
          {{ $t('dest_next_btn') }}
        </button>
      </div>
    </div>

    <!-- 위치 권한 요청 모달 -->
    <div v-if="showLocationModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>위치 정보 요청</h3>
          <button class="close-btn" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <h4>원활한 사용을 위해 위치 정보를 요구합니다</h4>
          <div class="benefit-item">
            <span class="benefit-icon">✅</span>
            <span>방문한 장소 자동 확인</span>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="denyLocation">나중에</button>
          <button class="btn-primary" @click="requestLocation">위치 정보 허용</button>
        </div>
      </div>
    </div>

    <!-- 튜토리얼 팝업 -->
    <div v-if="showTutorialModal" class="modal-overlay" @click="closeTutorial">
      <div class="modal-box tutorial-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ $t('tutorial_title') }}</h3>
          <button class="close-btn" @click="closeTutorial">×</button>
        </div>
        <div class="tutorial-content">
          <div class="tutorial-step" v-for="(step, index) in tutorialSteps" :key="index">
            <div class="step-number">{{ index + 1 }}</div>
            <div class="step-content">
              <h4>{{ $t(step.title) }}</h4>
              <p>{{ $t(step.description) }}</p>
            </div>
          </div>
        </div>
        <div class="modal-actions">
          <button class="modal-btn primary" @click="closeTutorial">{{ $t('tutorial_got_it') }}</button>
        </div>
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
      showTutorialModal: false,
      tutorialSteps: [
        {
          title: 'tutorial_step1_title',
          description: 'tutorial_step1_desc'
        },
        {
          title: 'tutorial_step2_title',
          description: 'tutorial_step2_desc'
        },
        {
          title: 'tutorial_step3_title',
          description: 'tutorial_step3_desc'
        },
        {
          title: 'tutorial_step4_title',
          description: 'tutorial_step4_desc'
        },
        {
          title: 'tutorial_step5_title',
          description: 'tutorial_step5_desc'
        },
        {
          title: 'tutorial_step6_title',
          description: 'tutorial_step6_desc'
        },
        {
          title: 'tutorial_step7_title',
          description: 'tutorial_step7_desc'
        }
      ]
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
    },
    showTutorial() {
      this.showTutorialModal = true;
    },
    closeTutorial() {
      this.showTutorialModal = false;
    }
  },
};
</script>

<style scoped>
/* 네이버 지식iN 스타일 - Community.vue 베이스 */
.destination-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
  background-attachment: fixed;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  width: 100vw;
  max-width: 100vw;
  overflow-x: hidden;
  box-sizing: border-box;
  padding: 20px;
}

.destination-content {
  width: 100%;
  max-width: 480px;
  background: white;
  border-radius: 16px;
  padding: 40px 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  box-sizing: border-box;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.destination-header {
  width: 100%;
  text-align: center;
  margin-bottom: 32px;
}

.bookmark-btn {
  position: absolute;
  top: 20px;
  right: 20px;
  background: white;
  color: #4A69E2;
  border: 1px solid #4A69E2;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  z-index: 1000;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.bookmark-btn:hover {
  background: #4A69E2;
  color: white;
}

.title {
  font-size: 2rem;
  font-weight: 800;
  margin-bottom: 1rem;
  text-align: center;
  color: #1e293b;
}

.subtitle {
  font-size: 16px;
  color: #6c757d;
  margin-bottom: 32px;
}

.destination-form {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #212529;
}

/* 목적지 입력창 */
.destination-input {
  width: 100%;
  padding: 14px;
  font-size: 14px;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
  background-attachment: fixed;
  box-sizing: border-box;
  color: #212529;
  font-family: inherit;
  transition: all 0.2s ease;
}

.destination-input:focus {
  outline: none;
  border-color: #4A69E2;
  background: white;
  box-shadow: 0 0 0 3px rgba(74, 105, 226, 0.1);
}

.destination-input::placeholder {
  color: #adb5bd;
}

/* 카테고리 선택 영역 */
.category-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  width: 100%;
}

.category-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #F7F8FA;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 16px 12px;
  font-size: 14px;
  font-weight: 500;
  color: #495057;
  cursor: pointer;
  user-select: none;
  transition: all 0.2s ease;
}

.category-item:hover {
  border-color: #4A69E2;
  background-color: #F0F4FF;
}

.category-item.active {
  background-color: #4A69E2;
  border-color: #4A69E2;
  color: white;
}

.icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.label {
  font-size: 13px;
  color: inherit;
}

.hidden-checkbox {
  display: none; /* 실제 체크박스는 숨김 */
}

/* 다음 버튼 */
.next-btn {
  width: 100%;
  padding: 16px;
  background: #4A69E2;
  color: white;
  font-size: 16px;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.next-btn:hover:not(:disabled) {
  background: #3B5BC7;
  transform: translateY(-1px);
}

.next-btn:active {
  transform: translateY(0);
}

.next-btn:disabled {
  background: #adb5bd;
  color: white;
  cursor: not-allowed;
}

/* 모달 스타일 - Community.vue 베이스 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3000;
  padding: 20px;
  color: #212529;
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 480px;
  max-height: 85vh;
  overflow-y: auto;
  color: #212529;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  position: relative;
  z-index: 3001;
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 20px 24px;
  border-bottom: 1px solid #f1f3f4;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #212529;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #adb5bd;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.close-btn:hover {
  color: #212529;
}

.modal-body {
  padding: 20px 24px;
  text-align: center;
}

.modal-body h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #212529;
  font-weight: 600;
}

.benefit-item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 14px;
  color: #495057;
  margin-bottom: 16px;
}

.benefit-icon {
  font-size: 16px;
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

.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 20px 24px 24px 24px;
}

.btn-primary {
  background: #4A69E2;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background: #3B5BC7;
}

.btn-secondary {
  background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
  background-attachment: fixed;
  color: #495057;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: #e9ecef;
  border-color: #adb5bd;
}

/* 반응형 */
@media (max-width: 768px) {
  .destination-page {
    padding: 12px;
  }
  
  .destination-content {
    padding: 32px 20px;
  }
  
  .destination-header {
    margin-bottom: 24px;
  }
  
  .title {
    font-size: 20px;
    margin-bottom: 8px;
  }
  
  .subtitle {
    font-size: 14px;
    margin-bottom: 24px;
  }
  
  .destination-form {
    gap: 20px;
  }
  
  .form-group {
    gap: 6px;
  }
  
  .form-group label {
    font-size: 13px;
  }
  
  .destination-input {
    padding: 12px;
    font-size: 13px;
  }
  
  .category-grid {
    gap: 8px;
  }
  
  .category-item {
    padding: 12px 8px;
    font-size: 13px;
  }
  
  .icon {
    font-size: 20px;
    margin-bottom: 6px;
  }
  
  .label {
    font-size: 12px;
  }
  
  .next-btn {
    padding: 14px;
    font-size: 15px;
  }
  
  .modal-overlay {
    padding: 12px;
  }
  
  .modal-header {
    padding: 20px 20px 16px 20px;
  }
  
  .modal-body {
    padding: 16px 20px;
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

/* 도움말 버튼 */
.help-btn {
  position: fixed;
  top: 20px;
  left: 20px;
  background: rgba(255, 255, 255, 0.9);
  color: #333;
  border: 2px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  width: 45px;
  height: 45px;
  font-size: 20px;
  font-weight: bold;
  cursor: pointer;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.help-btn:hover {
  background: rgba(255, 255, 255, 1);
  color: #333;
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.help-btn svg {
  width: 20px;
  height: 20px;
  stroke: white;
  fill: none;
}

/* 튜토리얼 모달 스타일 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3000;
  padding: 20px;
  color: #212529;
}

.modal-box {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 480px;
  max-height: 85vh;
  overflow-y: auto;
  color: #212529;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  position: relative;
  z-index: 3001;
}

.modal-header {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px 24px 20px 24px;
  text-align: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #212529;
  text-align: center;
  flex: 1;
}

.modal-content {
  padding: 0 24px;
}

.modal-actions {
  display: flex;
  justify-content: center;
  padding: 20px 24px 24px 24px;
}

.modal-btn {
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  border: none;
  font-weight: 500;
  transition: all 0.2s ease;
  min-width: 120px;
}

.modal-btn.primary {
  background: #4A69E2;
  color: white;
}

.modal-btn.primary:hover {
  background: #3B5BC7;
}

/* 튜토리얼 팝업 스타일 */
.tutorial-modal {
  max-width: 600px;
  max-height: 80vh;
}

.tutorial-content {
  padding: 20px 24px;
  max-height: 60vh;
  overflow-y: auto;
}

.tutorial-step {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f1f3f4;
}

.tutorial-step:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.step-number {
  background: #4A69E2;
  color: white;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
}

.step-content h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #212529;
}

.step-content p {
  margin: 0;
  font-size: 14px;
  color: #6b7280;
  line-height: 1.5;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #adb5bd;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.close-btn:hover {
  color: #212529;
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