<template>
  <div class="home-page">
    <div class="home-content">
      <h1 class="welcome" v-html="$t('welcome').replace(/\\n/g, '<br>')"></h1>
      
      <div class="lang-select">
        <button v-for="lang in languages" :key="lang.code" 
                :class="['lang-btn', { active: selectedLang === lang.code }]" 
                @click="selectLang(lang.code)">
          {{ lang.label }}
        </button>
      </div>
      
      <button class="start-btn" @click="start">{{ $t('start') }}</button>
      
      <div v-if="isLoggedIn" class="nav-buttons">
        <button class="nav-btn" @click="goToBookmarks">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
          </svg>
          {{ $t('bookmark_btn') }}
        </button>
        <button class="nav-btn" @click="goToCommunity">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
          {{ $t('community_btn') }}
        </button>
      </div>
    </div>
    
    <!-- 언어 선택 모달 -->
    <div v-if="showLanguageModal" class="language-modal-overlay" @click="closeLanguageModal">
      <div class="language-modal" @click.stop>
        <div class="modal-header">
          <h3>언어를 선택해주세요</h3>
          <button class="close-btn" @click="closeLanguageModal">×</button>
        </div>
        <div class="language-options">
          <button class="language-option" @click="selectLanguage('ko')">
            <span class="flag">🇰🇷</span>
            <span class="lang-name">한국어</span>
          </button>
          <button class="language-option" @click="selectLanguage('en')">
            <span class="flag">🇺🇸</span>
            <span class="lang-name">English</span>
          </button>
          <button class="language-option" @click="selectLanguage('zh')">
            <span class="flag">🇨🇳</span>
            <span class="lang-name">中文</span>
          </button>
          <button class="language-option" @click="selectLanguage('ja')">
            <span class="flag">🇯🇵</span>
            <span class="lang-name">日本語</span>
          </button>
        </div>
      </div>
    </div>
    
    <!-- 로그인 필요 모달 -->
    <div v-if="showLoginModal" class="modal-overlay" @click="closeLoginModal">
      <div class="modal-box" @click.stop>
        <div class="modal-header">
          <h3 v-html="$t('login_required').replace(/\\n/g, '<br>')"></h3>
          <button class="close-btn" @click="closeLoginModal">×</button>
        </div>
        <div class="modal-actions">
          <button class="modal-btn" @click="goAuth">{{ $t('login_signup') }}</button>
        </div>
      </div>
    </div>

    <!-- 로그아웃 버튼 -->
    <button v-if="isLoggedIn" class="logout-btn" @click="logout">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
        <polyline points="16,17 21,12 16,7" />
        <line x1="21" y1="12" x2="9" y2="12" />
      </svg>
      {{ $t('logout') }}
    </button>
  </div>
</template>

<script>
import { onAuthStateChanged, signOut } from 'firebase/auth';
import { auth } from '../firebase';
import { i18nState, $t } from '../i18n';

export default {
  name: 'Home',
  data() {
    return {
      languages: [
        { code: 'ko', label: '🇰🇷 한국어' },
        { code: 'zh', label: '🇨🇳 中文' },
        { code: 'ja', label: '🇯🇵 日本語' },
        { code: 'en', label: '🇺🇸 English' },
      ],
      selectedLang: 'ko',
      showLoginModal: false,
      showLanguageModal: true, // 첫 진입 시 언어 선택 모달 표시
      isLoggedIn: false,
    };
  },
  computed: {
    $t() { return $t; },
  },
  mounted() {
    onAuthStateChanged(auth, async (user) => {
      this.isLoggedIn = !!user;
      if (user) {
        console.log('사용자 로그인됨:', user.uid, user.email);
        // Backend API를 통해 사용자 언어 설정 조회
        try {
          const response = await fetch('http://localhost:5000/api/firebase/get-user-language', {
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
              this.selectedLang = result.language;
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
        this.showLoginModal = false;
        i18nState.lang = 'ko';
        this.selectedLang = 'ko';
      }
    });
  },
  methods: {
    selectLanguage(langCode) {
      this.selectedLang = langCode;
      i18nState.lang = langCode;
      this.showLanguageModal = false; // 언어 선택 후 모달 닫기
      
      // 로그인된 사용자의 경우 Firestore에 언어 설정 업데이트
      const user = auth.currentUser;
      if (user) {
        this.updateUserLanguage(user.uid, langCode);
      } else {
        // 언어 선택 후 로그인 상태 확인
        this.showLoginModal = true;
      }
    },
    async updateUserLanguage(uid, langCode) {
      try {
        // 백엔드 API로 언어 설정 업데이트
        const response = await fetch('http://localhost:5000/api/update_user_language', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            uid: uid,
            lang: langCode
          })
        });
        
        if (!response.ok) {
          throw new Error('Failed to update user language via API');
        }
        
        // Backend API가 성공했으므로 추가 작업 불필요
        
      } catch (error) {
        console.error('언어 설정 업데이트 실패:', error);
        
        // Backend API 실패 시 에러 처리
        console.error('언어 설정 업데이트가 실패했습니다. 잠시 후 다시 시도해주세요.');
      }
    },
    selectLang(code) {
      this.selectedLang = code;
      i18nState.lang = code;
    },
    start() {
      this.$router.push('/preference');
    },
    goToBookmarks() {
      this.$router.push('/bookmarks');
    },
    goToCommunity() {
      this.$router.push('/community');
    },
    goAuth() {
      this.showLoginModal = false;
      this.$router.push('/auth');
    },
    async logout() {
      await signOut(auth);
      this.isLoggedIn = false;
      this.selectedLang = 'ko';
      i18nState.lang = 'ko';
      this.$router.push('/');
    },
    closeLanguageModal() {
      this.showLanguageModal = false;
    },
    closeLoginModal() {
      this.showLoginModal = false;
    }
  },
};
</script>

<style scoped>
/* 네이버 지식iN 스타일 - Community.vue 베이스 */
.home-page {
  min-height: 100vh;
  background: #F7F8FA;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  width: 100vw;
  max-width: 100vw;
  overflow-x: hidden;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.home-content {
  width: 100%;
  max-width: 480px;
  background: white;
  border-radius: 16px;
  padding: 40px 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  text-align: center;
  box-sizing: border-box;
}

.logout-btn {
  position: fixed;
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

.logout-btn:hover {
  background: #4A69E2;
  color: white;
}
/* 환영 메시지 */
.welcome {
  color: #212529;
  font-size: 24px;
  font-weight: 700;
  line-height: 1.4;
  margin-bottom: 32px;
}

/* 언어 선택 버튼 그룹 */
.lang-select {
  display: flex;
  gap: 8px;
  margin-bottom: 32px;
  flex-wrap: wrap;
}

/* 언어 선택 버튼 */
.lang-btn {
  flex: 1;
  min-width: 80px;
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

.lang-btn:hover {
  background: #e9ecef;
  color: #212529;
}

/* 활성화된 언어 버튼 */
.lang-btn.active {
  background: #4A69E2;
  border-color: #4A69E2;
  color: white;
}

/* 시작하기 버튼 (CTA) */
.start-btn {
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
  margin-bottom: 24px;
}

.start-btn:hover {
  background: #3B5BC7;
  transform: translateY(-1px);
}

.start-btn:active {
  transform: translateY(0);
}

/* 네비게이션 버튼들 */
.nav-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.nav-btn {
  background: #f8f9fa;
  color: #495057;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.nav-btn:hover {
  background: #4A69E2;
  color: white;
  border-color: #4A69E2;
}

/* 모달 팝업 스타일 - Community.vue 베이스 */
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
}

.close-btn:hover {
  color: #212529;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 20px 24px 24px 24px;
}

.modal-btn {
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  border: none;
  background: #4A69E2;
  color: white;
  font-weight: 500;
  transition: all 0.2s ease;
}

.modal-btn:hover {
  background: #3B5BC7;
}
.home-content {
  transition: filter 0.2s;
}
.home-content.blurred {
  filter: blur(4px);
  pointer-events: none;
  user-select: none;
}

/* 언어 선택 모달 스타일 - Community.vue 베이스 */
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

.language-options {
  padding: 20px 24px 24px 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.language-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 16px;
  font-weight: 500;
  color: #212529;
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
  text-align: left;
  color: inherit;
}

/* 반응형 */
@media (max-width: 768px) {
  .home-content {
    padding: 32px 20px;
    margin: 0 12px;
  }
  
  .welcome {
    font-size: 20px;
    margin-bottom: 24px;
  }
  
  .lang-select {
    gap: 6px;
    margin-bottom: 24px;
  }
  
  .lang-btn {
    padding: 10px 12px;
    font-size: 13px;
  }
  
  .start-btn {
    padding: 14px;
    font-size: 15px;
  }
  
  .nav-buttons {
    gap: 8px;
  }
  
  .nav-btn {
    padding: 10px 12px;
    font-size: 13px;
  }
  
  .modal-overlay,
  .language-modal-overlay {
    padding: 12px;
  }
}
</style>