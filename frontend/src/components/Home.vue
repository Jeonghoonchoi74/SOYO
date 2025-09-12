<template>
  <div class="home-page">
    <div class="white-container">
      <div class="image-container">
        <img 
          :src="currentImage" 
          :key="currentImage"
          alt="Search" 
          class="search-image"
        />
      </div>
      <div class="welcome-text">
        <h2 class="main-title">{{ $t('home_title') }}</h2>
        <p class="sub-title">{{ $t('home_subtitle') }}</p>
      </div>
      <button class="start-btn" @click="goToMain">{{ $t('start') }}</button>
    </div>
    
    <!-- 언어 선택 모달 -->
    <div v-if="showLanguageModal" class="language-modal-overlay" @click="closeLanguageModal">
      <div class="language-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ $t('select_language_for_setup') }}</h3>
          <button class="close-btn" @click="closeLanguageModal">×</button>
        </div>
        <div class="language-options">
          <button class="language-option" @click="selectLanguage('ko')">
            <span class="flag">🇰🇷</span>
            <span class="lang-name">{{ $t('lang_ko') }}</span>
          </button>
          <button class="language-option" @click="selectLanguage('en')">
            <span class="flag">🇺🇸</span>
            <span class="lang-name">{{ $t('lang_en') }}</span>
          </button>
          <button class="language-option" @click="selectLanguage('ja')">
            <span class="flag">🇯🇵</span>
            <span class="lang-name">{{ $t('lang_ja') }}</span>
          </button>
          <button class="language-option" @click="selectLanguage('zh')">
            <span class="flag">🇨🇳</span>
            <span class="lang-name">{{ $t('lang_zh') }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { onAuthStateChanged } from 'firebase/auth';
import { auth } from '../firebase';
import { i18nState, $t } from '../i18n';
import search1 from '../assets/search1.png';
import search2 from '../assets/search2.png';

export default {
  name: 'Home',
  data() {
    return {
      currentImageIndex: 0,
      images: [search1, search2],
      intervalId: null,
      showLanguageModal: true, // 첫 진입 시 언어 선택 모달 표시
      isLoggedIn: false,
    };
  },
  computed: {
    $t() { return $t; },
    currentImage() {
      return this.images[this.currentImageIndex];
    }
  },
  mounted() {
    this.startImageRotation();
    
    // Firebase 인증 상태 확인
    onAuthStateChanged(auth, async (user) => {
      this.isLoggedIn = !!user;
      if (user) {
        console.log('사용자 로그인됨:', user.uid, user.email);
        // Backend API를 통해 사용자 언어 설정 조회
        try {
          const response = await fetch('/api/firebase/get-user-language', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              uid: user.uid
            }),
          });

          if (response.ok) {
            const result = await response.json();
            console.log('Backend에서 조회된 사용자 언어:', result.language);
            if (result.language) {
              i18nState.lang = result.language;
              console.log('언어 설정 적용:', result.language);
            } else {
              console.log('사용자 데이터에 언어 설정이 없음');
            }
          } else {
            console.log('사용자 언어 조회 실패');
          }
        } catch (e) {
          console.error('사용자 언어 조회 실패:', e);
        }
        this.showLanguageModal = false; // 이미 로그인된 경우 언어 선택 팝업 숨김
      } else {
        console.log('사용자 로그아웃됨');
        // 언어 선택 모달이 우선적으로 뜨도록
        this.showLanguageModal = true;
        i18nState.lang = 'ko';
      }
    });
  },
  beforeUnmount() {
    this.stopImageRotation();
  },
  methods: {
    selectLanguage(langCode) {
      i18nState.lang = langCode;
      this.showLanguageModal = false; // 언어 선택 후 모달 닫기
      
      // sessionStorage에 언어 설정 저장
      sessionStorage.setItem('userLanguage', langCode);
      console.log('언어 설정을 sessionStorage에 저장:', langCode);
      
      // 로그인된 사용자의 경우 Firestore에 언어 설정 업데이트
      const user = auth.currentUser;
      if (user) {
        this.updateUserLanguage(user.uid, langCode);
      }
    },
    async updateUserLanguage(uid, langCode) {
      try {
        console.log('Firebase 언어 업데이트 시작:', { uid, langCode });
        
        // 백엔드 API로 언어 설정 업데이트
        const response = await fetch('/api/update_user_language', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            uid: uid,
            lang: langCode
          })
        });
        
        console.log('API 응답 상태:', response.status);
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error('API 응답 에러:', errorText);
          throw new Error(`Failed to update user language via API: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('Firebase 언어 업데이트 성공:', result);
        
      } catch (error) {
        console.error('언어 설정 업데이트 실패:', error);
        console.error('언어 설정 업데이트가 실패했습니다. 잠시 후 다시 시도해주세요.');
      }
    },
    goToMain() {
      this.$router.push('/main');
    },
    startImageRotation() {
      this.intervalId = setInterval(() => {
        this.currentImageIndex = (this.currentImageIndex + 1) % this.images.length;
      }, 500); // 0.5초마다 이미지 변경
    },
    stopImageRotation() {
      if (this.intervalId) {
        clearInterval(this.intervalId);
        this.intervalId = null;
      }
    },
    closeLanguageModal() {
      this.showLanguageModal = false;
    }
  },
};
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
  background-attachment: fixed;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.white-container {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 30px;
  max-width: 400px;
  width: 100%;
}

.image-container {
  width: 200px;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0;
}

.search-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.welcome-text {
  text-align: center;
  margin-bottom: 5px;
  margin-top: 0;
}

.main-title {
  font-size: 20px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 8px 0;
  line-height: 1.3;
}

.sub-title {
  font-size: 16px;
  font-weight: 500;
  color: #6b7280;
  margin: 0;
  line-height: 1.4;
}

.start-btn {
  padding: 20px 40px;
  background: #4A69E2;
  color: white;
  font-size: 18px;
  font-weight: 600;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 25px rgba(74, 105, 226, 0.3);
}

.start-btn:hover {
  background: #3B5BC7;
  transform: translateY(-2px);
  box-shadow: 0 12px 35px rgba(74, 105, 226, 0.4);
}

.start-btn:active {
  transform: translateY(0);
}

/* 반응형 */
@media (max-width: 768px) {
  .white-container {
    padding: 30px;
    max-width: 350px;
  }
  
  .image-container {
    width: 150px;
    height: 150px;
  }
  
  .main-title {
    font-size: 18px;
  }
  
  .sub-title {
    font-size: 14px;
  }
  
  .start-btn {
    padding: 16px 32px;
    font-size: 16px;
  }
}

@media (max-width: 480px) {
  .white-container {
    padding: 24px;
    max-width: 300px;
    margin: 0 12px;
  }
  
  .image-container {
    width: 120px;
    height: 120px;
  }
  
  .main-title {
    font-size: 16px;
  }
  
  .sub-title {
    font-size: 13px;
  }
  
  .start-btn {
    padding: 14px 28px;
    font-size: 15px;
  }
}

/* 언어 선택 모달 스타일 */
.language-modal-overlay {
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

.language-modal {
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
}

.close-btn:hover {
  color: #212529;
}

.language-options {
  padding: 20px 24px 24px 24px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.language-option {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px 12px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  font-weight: 500;
  color: #212529;
  width: 100%;
  text-align: center;
}

.language-option:hover {
  background: #4A69E2;
  color: white;
  border-color: #4A69E2;
}

.flag {
  font-size: 20px;
  color: inherit;
}

.lang-name {
  flex: 1;
  text-align: center;
  color: inherit;
}

/* 반응형 */
@media (max-width: 768px) {
  .language-modal-overlay {
    padding: 12px;
  }
  
  .language-options {
    padding: 16px 20px 20px 20px;
    gap: 10px;
    grid-template-columns: 1fr 1fr;
  }
  
  .language-option {
    padding: 12px 8px;
    font-size: 13px;
    gap: 6px;
    justify-content: center;
    text-align: center;
  }
  
  .lang-name {
    text-align: center;
  }
}
</style>