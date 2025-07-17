<template>
  <div class="home-container">
    <button v-if="isLoggedIn" class="logout-btn" @click="logout">{{ $t('logout') }}</button>
    <div :class="['home-content', { blurred: showLoginModal }]">
      <h1 class="welcome" v-html="$t('welcome').replace(/\\n/g, '<br>')"></h1>
      <div class="lang-select">
        <button v-for="lang in languages" :key="lang.code" :class="['lang-btn', { active: selectedLang === lang.code }]" @click="selectLang(lang.code)">
          {{ lang.label }}
        </button>
      </div>
      <button class="start-btn" @click="start">{{ $t('start') }}</button>
    </div>
    
    <!-- 언어 선택 모달 -->
    <div v-if="showLanguageModal" class="language-modal-overlay">
      <div class="language-modal">
        <!-- <h2 class="language-title">언어를 선택해주세요</h2> -->
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
    <div v-if="showLoginModal" class="modal-overlay">
      <div class="modal-box">
        <div class="modal-title" v-html="$t('login_required').replace(/\\n/g, '<br>')"></div>
        <div class="modal-actions">
          <button class="modal-btn" @click="goAuth">{{ $t('login_signup') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { onAuthStateChanged, signOut } from 'firebase/auth';
import { auth } from '../firebase';
import { i18nState, $t } from '../i18n';
import { getFirestore, doc, getDoc, updateDoc } from 'firebase/firestore';

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
        // Firestore에서 lang 조회
        try {
          const db = getFirestore();
          const userDoc = await getDoc(doc(db, 'users', user.uid));
          if (userDoc.exists()) {
            const userData = userDoc.data();
            console.log('Firestore에서 조회된 사용자 데이터:', userData);
            if (userData.lang) {
              i18nState.lang = userData.lang;
              this.selectedLang = userData.lang;
              console.log('언어 설정 적용:', userData.lang);
            } else {
              console.log('사용자 데이터에 언어 설정이 없음');
            }
          } else {
            console.log('Firestore에 사용자 데이터가 없음');
          }
        } catch (e) {
          console.error('Firestore 조회 실패:', e);
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
        
        // Firebase Firestore에도 직접 업데이트 (이중 보장)
        try {
          const db = getFirestore();
          await updateDoc(doc(db, 'users', uid), {
            lang: langCode,
            updatedAt: new Date()
          });
        } catch (firestoreError) {
          console.warn('Firestore 직접 업데이트 실패 (백엔드 API는 성공):', firestoreError);
        }
        
      } catch (error) {
        console.error('언어 설정 업데이트 실패:', error);
        
        // 백엔드 API 실패 시 Firestore에만 업데이트 시도
        try {
          const db = getFirestore();
          await updateDoc(doc(db, 'users', uid), {
            lang: langCode,
            updatedAt: new Date()
          });
          console.log('Firestore에 직접 언어 업데이트 성공');
        } catch (firestoreError) {
          console.error('Firestore 직접 업데이트도 실패:', firestoreError);
        }
      }
    },
    selectLang(code) {
      this.selectedLang = code;
      i18nState.lang = code;
    },
    start() {
      this.$router.push('/destination');
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
  },
};
</script>

<style scoped>
/* 전체 레이아웃 */
.home-container {
  width: 800px;
  margin: 60px auto;
  padding: 64px 80px 96px 80px;
  border-radius: 32px;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  position: relative;
}


.logout-btn {
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
.logout-btn:hover {
  background: #2563eb;
  color: #fff;
}
/* 환영 메시지 */
.welcome {
  color: #1e293b;
  font-size: 2.2rem;
  font-weight: 800;
  line-height: 1.5;
  margin-bottom: 3.5rem;
}

/* 언어 선택 버튼 그룹 */
.lang-select {
  display: flex;
  gap: 1.2rem;
  margin-bottom: 3.5rem;
}

/* 언어 선택 버튼 */
.lang-btn {
  padding: 1rem 0;
  border: 2px solid #e2e8f0;
  border-radius: 24px;
  background: #fff;
  color: #475569;
  font-size: 1.2rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  flex: 1;
}

.lang-btn:hover {
  border-color: #3b82f6;
  color: #3b82f6;
}

/* 활성화된 언어 버튼 */
.lang-btn.active {
  background: #3b82f6;
  border-color: #3b82f6;
  color: #fff;
}

/* 시작하기 버튼 (CTA) */
.start-btn {
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

.start-btn:hover {
  background: #1d4ed8;
  transform: translateY(-2px);
}

.start-btn:active {
  background: #1e40af;
  transform: translateY(0);
}

/* 모달 팝업 스타일 */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-box {
  background: #fff;
  border-radius: 20px;
  padding: 2.5rem 2.5rem 2rem 2.5rem;
  box-shadow: 0 2px 16px rgba(0,0,0,0.10);
  min-width: 320px;
  text-align: center;
}
.modal-title {
  font-size: 1.3rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 2rem;
}
.modal-actions {
  display: flex;
  gap: 1.2rem;
  justify-content: center;
}
.modal-btn {
  padding: 0.8rem 2.2rem;
  font-size: 1.1rem;
  font-weight: 700;
  border: none;
  border-radius: 12px;
  background: #2563eb;
  color: #fff;
  cursor: pointer;
  transition: background 0.2s;
}
.modal-btn:hover {
  background: #1d4ed8;
}
.home-content {
  transition: filter 0.2s;
}
.home-content.blurred {
  filter: blur(4px);
  pointer-events: none;
  user-select: none;
}

/* 언어 선택 모달 스타일 */
.language-modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.language-modal {
  background: #fff;
  border-radius: 24px;
  padding: 3rem 2.5rem 2.5rem 2.5rem;
  box-shadow: 0 8px 32px rgba(0,0,0,0.12);
  min-width: 400px;
  text-align: center;
}

.language-options {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.language-option {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.2rem 1.5rem;
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 1.1rem;
  font-weight: 700;
  color: #1e293b;
}
.language-option:hover {
  background: #2563eb;
  color: #fff;
  border-color: #2563eb;
}
.language-option:hover .flag,
.language-option:hover .lang-name {
  color: #fff;
}
.flag {
  font-size: 1.5rem;
  color: #1e293b;
}
.lang-name {
  flex: 1;
  text-align: left;
  color: #1e293b;
}
</style>