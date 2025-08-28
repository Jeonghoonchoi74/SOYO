<template>
  <div class="preference-page">
    <div class="preference-content">
      <div class="preference-header">
        <button class="bookmark-btn" @click="goBookmark">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
          </svg>
          {{ $t('bookmark_btn') }}
        </button>
        <h2 class="title">{{ $t('pref_title') }}</h2>
        <p class="subtitle">{{ $t('pref_subtitle') }}</p>
      </div>
      
      <div class="preference-form">
        <div class="form-group">
          <label class="section-label">{{ $t('pref_section_region') }}</label>
          <select v-model="selectedRegion" class="region-dropdown" @change="onRegionChange">
            <option value="" disabled>{{ $t('pref_region_placeholder') }}</option>
            <option v-for="region in regionOptions" :key="region.value" :value="region.value">
              {{ $t(region.label) }}
            </option>
          </select>
        </div>
        
        <div v-if="selectedRegion" class="form-group">
          <label class="section-label">{{ $t('pref_section_category') }}</label>
          <div class="category-selector">
            <button 
              v-for="category in availableCategories" 
              :key="category" 
              :class="['category-btn', { active: selectedCategory === category }]" 
              @click="selectCategory(category)"
            >
              {{ getCategoryDisplayName(category) }}
            </button>
          </div>
        </div>
        


        <div v-if="selectedCategory" class="form-group">
          <label class="section-label">{{ $t('pref_section_free') }}</label>
          <textarea
            v-model="freeText"
            class="free-input"
            :placeholder="$t('pref_free_placeholder')"
            rows="3"
          />
        </div>
  
        <button class="recommend-btn" :disabled="!canProceed || isSaving" @click="recommend">
          {{ isSaving ? $t('location_modal_saving') : $t('pref_recommend_btn') }}
        </button>
      </div>
    </div>

    <!-- 위치 권한 요청 모달 -->
    <div v-if="showLocationModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ $t('location_modal_title') }}</h3>
          <button class="close-btn" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <h4>{{ $t('location_modal_subtitle') }}</h4>
          <div class="benefit-item">
            <span class="benefit-icon">✅</span>
            <span>{{ $t('location_modal_benefit') }}</span>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="denyLocation">{{ $t('location_modal_later') }}</button>
          <button class="btn-primary" @click="requestLocation">{{ $t('location_modal_allow') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { i18nState, $t } from '../i18n';
import { getAuth } from 'firebase/auth';
import { getFirestore, doc, getDoc } from 'firebase/firestore';
import { getRegionOptions, getAvailableCategories, getCategoryLabel } from '../utils/regionMapping';

export default {
  name: 'PreferenceInput',
  data() {
    return {
      regionOptions: getRegionOptions(),
      selectedRegion: '',
      selectedCategory: '',
      availableCategories: [],
      freeText: '',
      isSaving: false,
      showLocationModal: false,
      locationPermission: null,
    };
  },
  computed: {
    canProceed() {
      // 지역 선택과 카테고리 선택이 필요함
      return this.selectedRegion && this.selectedCategory;
    },
    $t() { return $t; },
  },

  mounted() {
    this.selectedRegion = '';
    this.selectedCategory = '';
    this.availableCategories = [];
    this.freeText = '';
    
    // 위치 권한 확인
    this.checkLocationPermission();
  },

  methods: {
    $t,
    // 북마크 페이지로 이동
    goBookmark() {
      this.$router.push('/bookmarks');
    },


    onRegionChange() {
      this.selectedCategory = ''; // 지역 변경 시 카테고리 초기화
      this.availableCategories = getAvailableCategories(this.selectedRegion);
    },
    selectCategory(category) {
      this.selectedCategory = category;
    },
    getCategoryDisplayName(category) {
      return this.$t(getCategoryLabel(category));
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

    async savePreferences() {
      const auth = getAuth();
      const user = auth.currentUser;
      
      if (!user) {
        console.error('사용자가 로그인되지 않았습니다.');
        return false;
      }

      const preferences = {
        region: this.selectedRegion,
        category: this.selectedCategory,
        freeText: this.freeText,
      };

      try {
        this.isSaving = true;
        
        const response = await fetch('http://localhost:5000/api/save_user_preferences', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            uid: user.uid,
            preferences: preferences
          }),
        });

        const result = await response.json();
        
        if (result.success) {
          console.log('사용자 선호도가 성공적으로 저장되었습니다.');
          return true;
        } else {
          console.error('선호도 저장 실패:', result.error);
          return false;
        }
      } catch (error) {
        console.error('선호도 저장 중 오류 발생:', error);
        return false;
      } finally {
        this.isSaving = false;
      }
    },

    async recommend() {
      if (this.isSaving) return;
      
      // Free Text가 있고 사용자 언어가 한국어가 아닐 때만 번역 API 호출
      if (this.freeText && this.freeText.trim()) {
        const userLanguage = await this.getUserLanguage();
        if (userLanguage && userLanguage !== 'ko') {
          await this.translateFreeText();
        } else {
          console.log('사용자 언어가 한국어이므로 번역을 건너뜁니다.');
        }
      }
      
      const saved = await this.savePreferences();
      if (saved) {
        this.$router.push({
          path: '/recommend',
          query: { 
            region: this.selectedRegion,
            category: this.selectedCategory
          }
        });
      } else {
        // 저장 실패 시에도 추천 페이지로 이동 (선택사항)
        this.$router.push({
          path: '/recommend',
          query: { 
            region: this.selectedRegion,
            category: this.selectedCategory
          }
        });
      }
    },

    // 사용자 언어 설정 가져오기
    async getUserLanguage() {
      const auth = getAuth();
      const user = auth.currentUser;
      
      if (!user) {
        console.error('사용자가 로그인되지 않았습니다.');
        return null;
      }

      try {
        // Firestore에서 사용자 언어 설정 조회
        const db = getFirestore();
        const userDoc = await getDoc(doc(db, 'users', user.uid));
        
        if (userDoc.exists()) {
          const userData = userDoc.data();
          const userLanguage = userData.lang;
          console.log('사용자 언어 설정:', userLanguage);
          return userLanguage;
        } else {
          console.log('Firestore에 사용자 데이터가 없음');
          return null;
        }
      } catch (error) {
        console.error('사용자 언어 설정 조회 중 오류:', error);
        return null;
      }
    },

    // Free Text 번역 함수
    async translateFreeText() {
      const auth = getAuth();
      const user = auth.currentUser;
      
      if (!user) {
        console.error('사용자가 로그인되지 않았습니다.');
        return;
      }

      try {
        console.log('번역 요청 시작:', this.freeText);
        
        const response = await fetch('http://localhost:5001/translate', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            text: this.freeText,
            target_lang: 'ko',
            uid: user.uid
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        
        if (result.translated_text) {
          console.log('원본 텍스트:', this.freeText);
          console.log('번역된 텍스트 (한국어):', result.translated_text);
        } else {
          console.error('번역 결과가 없습니다:', result);
        }
        
      } catch (error) {
        console.error('번역 API 호출 중 오류 발생:', error);
      }
    },
  },
};
</script>

<style scoped>
/* 네이버 지식iN 스타일 - Community.vue 베이스 */
.preference-page {
  min-height: 100vh;
  background: #F7F8FA;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  width: 100vw;
  max-width: 100vw;
  overflow-x: hidden;
  box-sizing: border-box;
  padding: 20px;
}

.preference-content {
  width: 100%;
  max-width: 480px;
  background: white;
  border-radius: 16px;
  padding: 40px 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  box-sizing: border-box;
  margin: 0 auto;
}

.preference-header {
  text-align: center;
  margin-bottom: 32px;
  position: relative;
}

.bookmark-btn {
  position: absolute;
  top: -20px;
  right: -20px;
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
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 8px;
  color: #212529;
}

.subtitle {
  font-size: 16px;
  color: #6c757d;
  margin-bottom: 0;
}

.preference-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-label {
  font-size: 16px;
  font-weight: 600;
  color: #212529;
}

.region-dropdown {
  width: 100%;
  padding: 14px;
  font-size: 14px;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  background: #F7F8FA;
  color: #212529;
  outline: none;
  transition: all 0.2s ease;
  font-family: inherit;
}

.region-dropdown:focus {
  border-color: #4A69E2;
  background: white;
  box-shadow: 0 0 0 3px rgba(74, 105, 226, 0.1);
}

.region-dropdown option {
  padding: 8px;
  font-size: 14px;
}

.category-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.category-btn {
  flex: 1;
  min-width: 120px;
  padding: 12px 16px;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  background: #f8f9fa;
  color: #495057;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.category-btn:hover {
  background: #e9ecef;
  color: #212529;
}

.category-btn.active {
  background: #4A69E2;
  border-color: #4A69E2;
  color: white;
}

.toggle-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.toggle-btn {
  flex: 1;
  min-width: 100px;
  padding: 12px 16px;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  background: #F7F8FA;
  color: #495057;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.toggle-btn:hover {
  background: #e9ecef;
  color: #212529;
}

.toggle-btn.active {
  background: #4A69E2;
  border-color: #4A69E2;
  color: white;
}

.free-input {
  width: 100%;
  padding: 14px;
  font-size: 14px;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  background: #F7F8FA;
  color: #212529;
  outline: none;
  transition: all 0.2s ease;
  font-family: inherit;
  resize: vertical;
  min-height: 80px;
  box-sizing: border-box;
}

.free-input:focus {
  border-color: #4A69E2;
  background: white;
  box-shadow: 0 0 0 3px rgba(74, 105, 226, 0.1);
}

.free-input::placeholder {
  color: #adb5bd;
}

.recommend-btn {
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
  margin-top: 8px;
}

.recommend-btn:hover:not(:disabled) {
  background: #3B5BC7;
  transform: translateY(-1px);
}

.recommend-btn:active {
  transform: translateY(0);
}

.recommend-btn:disabled {
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
  background: #F7F8FA;
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
  .preference-page {
    padding: 12px;
  }
  
  .preference-content {
    padding: 32px 20px;
  }
  
  .preference-header {
    margin-bottom: 24px;
  }
  
  .title {
    font-size: 20px;
    margin-bottom: 6px;
  }
  
  .subtitle {
    font-size: 14px;
  }
  
  .preference-form {
    gap: 20px;
  }
  
  .form-group {
    gap: 8px;
  }
  
  .section-label {
    font-size: 15px;
  }
  
  .region-dropdown {
    padding: 12px;
    font-size: 13px;
  }
  
  .category-btn {
    padding: 10px 12px;
    font-size: 13px;
    min-width: 100px;
  }
  
  .toggle-btn {
    padding: 10px 12px;
    font-size: 13px;
    min-width: 80px;
  }
  
  .free-input {
    padding: 12px;
    font-size: 13px;
  }
  
  .recommend-btn {
    padding: 14px;
    font-size: 15px;
  }

  .bookmark-btn {
    position: relative;
    top: 0;
    right: 0;
    margin-bottom: 16px;
    align-self: flex-end;
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
</style>