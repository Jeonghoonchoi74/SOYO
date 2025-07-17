<template>
  <div class="language-setup-modal-overlay">
    <div class="language-setup-modal">
      <h2 class="modal-title">{{ $t('welcome_google_user') }}</h2>
      <p class="modal-subtitle">{{ $t('select_language_for_setup') }}</p>
      
      <div class="language-options">
        <button 
          v-for="lang in languages" 
          :key="lang.code" 
          class="language-option" 
          :class="{ active: selectedLang === lang.code }"
          @click="selectLanguage(lang.code)"
        >
          <span class="flag">{{ lang.flag }}</span>
          <span class="lang-name">{{ lang.label }}</span>
        </button>
      </div>
      
      <div class="modal-actions">
        <button 
          class="setup-btn" 
          :disabled="!selectedLang" 
          @click="completeSetup"
        >
          {{ $t('complete_setup') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { i18nState, $t } from '../i18n';
import { getFirestore, doc, setDoc } from 'firebase/firestore';

export default {
  name: 'LanguageSetupModal',
  props: {
    user: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      selectedLang: '',
      languages: [
        { code: 'ko', label: '한국어', flag: '🇰🇷' },
        { code: 'en', label: 'English', flag: '🇺🇸' },
        { code: 'zh', label: '中文', flag: '🇨🇳' },
        { code: 'ja', label: '日本語', flag: '🇯🇵' },
      ]
    };
  },
  computed: {
    $t() { return $t; },
  },
  methods: {
    selectLanguage(langCode) {
      this.selectedLang = langCode;
    },
    async completeSetup() {
      if (!this.selectedLang) return;
      
      try {
        // 1. 백엔드 API로 사용자 정보 저장
        const response = await fetch('http://localhost:5000/api/register_user', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            uid: this.user.uid,
            name: this.user.displayName || this.user.email?.split('@')[0] || 'User',
            lang: this.selectedLang,
            email: this.user.email,
            provider: 'google'
          })
        });
        
        if (!response.ok) {
          throw new Error('Failed to save user info via API');
        }
        
        // 2. Firebase Firestore에도 직접 저장 (이중 보장)
        try {
          const db = getFirestore();
          await setDoc(doc(db, 'users', this.user.uid), {
            name: this.user.displayName || this.user.email?.split('@')[0] || 'User',
            lang: this.selectedLang,
            email: this.user.email,
            provider: 'google',
            createdAt: new Date(),
            updatedAt: new Date()
          }, { merge: true }); // merge: true로 기존 데이터와 병합
        } catch (firestoreError) {
          console.warn('Firestore 직접 저장 실패 (백엔드 API는 성공):', firestoreError);
          // Firestore 저장 실패는 경고만 하고 계속 진행
        }
        
        // i18n 상태 업데이트
        i18nState.lang = this.selectedLang;
        
        // 모달 닫기 이벤트 발생
        this.$emit('setup-complete', this.selectedLang);
        
      } catch (error) {
        console.error('사용자 정보 저장 실패:', error);
        
        // 백엔드 API 실패 시 Firestore에만 저장 시도
        try {
          const db = getFirestore();
          await setDoc(doc(db, 'users', this.user.uid), {
            name: this.user.displayName || this.user.email?.split('@')[0] || 'User',
            lang: this.selectedLang,
            email: this.user.email,
            provider: 'google',
            createdAt: new Date(),
            updatedAt: new Date()
          }, { merge: true });
          console.log('Firestore에 직접 저장 성공');
        } catch (firestoreError) {
          console.error('Firestore 직접 저장도 실패:', firestoreError);
        }
        
        // 에러가 발생해도 언어는 설정하고 진행
        i18nState.lang = this.selectedLang;
        this.$emit('setup-complete', this.selectedLang);
      }
    }
  }
};
</script>

<style scoped>
.language-setup-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.language-setup-modal {
  background: #fff;
  border-radius: 24px;
  padding: 3rem 2.5rem 2.5rem 2.5rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  min-width: 450px;
  text-align: center;
}

.modal-title {
  font-size: 1.8rem;
  font-weight: 800;
  color: #1e293b;
  margin-bottom: 1rem;
}

.modal-subtitle {
  font-size: 1.1rem;
  color: #64748b;
  margin-bottom: 2.5rem;
}

.language-options {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 2.5rem;
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
  background: #e0e7ff;
  border-color: #3b82f6;
}

.language-option.active {
  background: #2563eb;
  color: #fff;
  border-color: #2563eb;
}

.language-option.active .flag,
.language-option.active .lang-name {
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

.modal-actions {
  display: flex;
  justify-content: center;
}

.setup-btn {
  padding: 1rem 2.5rem;
  font-size: 1.2rem;
  font-weight: 700;
  border: none;
  border-radius: 16px;
  background: #2563eb;
  color: #fff;
  cursor: pointer;
  transition: all 0.2s;
}

.setup-btn:hover:not(:disabled) {
  background: #1d4ed8;
  transform: translateY(-2px);
}

.setup-btn:disabled {
  background: #cbd5e1;
  color: #94a3b8;
  cursor: not-allowed;
  transform: none;
}
</style> 