<template>
  <div class="auth-page">

    <div class="auth-content">
      <div class="auth-tabs">
        <button :class="{active: mode==='login'}" @click="mode='login'">{{ $t('login') }}</button>
        <button :class="{active: mode==='signup'}" @click="mode='signup'">{{ $t('signup') }}</button>
      </div>
      
      <form class="auth-form" @submit.prevent="onSubmit">
        <div class="form-group">
          <label for="email">{{ $t('email') }}</label>
          <input id="email" v-model="email" type="email" required :placeholder="$t('input_email')" />
        </div>
        
        <div class="form-group">
          <label for="password">{{ $t('password') }}</label>
          <input id="password" v-model="password" type="password" required :placeholder="$t('input_password')" />
        </div>
        
        <div v-if="mode==='signup'" class="form-group">
          <label for="name">{{ $t('name') }}</label>
          <input id="name" v-model="name" type="text" required :placeholder="$t('input_name')" />
        </div>
        
        <div v-if="mode==='signup'" class="form-group">
          <label for="password2">{{ $t('password_confirm') }}</label>
          <input id="password2" v-model="password2" type="password" required :placeholder="$t('input_password_confirm')" />
        </div>
        
        <div v-if="mode==='signup'" class="form-group">
          <label for="lang">{{ $t('select_language') }}</label>
          <select id="lang" v-model="signupLang" required>
            <option value="ko">🇰🇷 {{ $t('lang_ko') }}</option>
            <option value="en">🇺🇸 {{ $t('lang_en') }}</option>
            <option value="ja">🇯🇵 {{ $t('lang_ja') }}</option>
            <option value="zh">🇨🇳 {{ $t('lang_zh') }}</option>
          </select>
        </div>
        
        <div v-if="error" class="error-msg">{{ error }}</div>
        
        <button class="auth-btn" type="submit" :disabled="loading">
          {{ mode==='login' ? $t('login') : $t('signup') }}
        </button>
        
        
        <button class="google-btn" type="button" @click="googleLogin" :disabled="loading">
          <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" alt="Google" class="google-icon" />
          {{ $t('login_with_google') }}
        </button>
      </form>
    </div>
    
    <!-- Google 로그인 후 언어 설정 모달 -->
    <LanguageSetupModal 
      v-if="showLanguageSetupModal" 
      :user="googleUser"
      @setup-complete="onLanguageSetupComplete"
    />

  </div>
</template>

<script>
import { auth } from '../firebase';
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  GoogleAuthProvider,
  signInWithPopup,
  updateProfile,
} from 'firebase/auth';
import { i18nState, $t } from '../i18n';
import LanguageSetupModal from './LanguageSetupModal.vue';

export default {
  name: 'AuthPage',
  components: {
    LanguageSetupModal
  },
  data() {
    return {
      mode: 'login',
      email: '',
      password: '',
      name: '',
      password2: '',
      signupLang: i18nState.lang,
      error: '',
      loading: false,
      showLanguageSetupModal: false,
      googleUser: null,
    };
  },
  computed: {
    $t() { return $t; },
  },
  watch: {
    // 언어가 바뀌면 select도 동기화
    'i18nState.lang': {
      handler(newLang) {
        this.signupLang = newLang;
      },
      immediate: true,
    },
  },
  methods: {
    async onSubmit() {
      this.error = '';
      this.loading = true;
      try {
        if (this.mode === 'signup') {
          if (!this.name.trim()) {
            this.error = this.$t('error_name_required');
            this.loading = false;
            return;
          }
          if (this.password !== this.password2) {
            this.error = this.$t('error_password_mismatch');
            this.loading = false;
            return;
          }
          const userCredential = await createUserWithEmailAndPassword(auth, this.email, this.password);
          await updateProfile(userCredential.user, { displayName: this.name });
          // Flask API로 uid, name, lang 전송
          try {
            await fetch('/api/register_user', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                uid: userCredential.user.uid,
                name: this.name,
                lang: this.signupLang
              })
            });
          } catch (apiErr) {
            this.error = '서버에 사용자 정보 저장 실패';
            this.loading = false;
            return;
          }
          this.$router.push('/main');
        } else {
          await signInWithEmailAndPassword(auth, this.email, this.password);
          const user = auth.currentUser;
          if (user && user.email && user.email.toLowerCase() === 'admin@gmail.com') {
            this.$router.push('/management');
          } else {
            this.$router.push('/main');
          }
        }
      } catch (e) {
        this.error = this.friendlyError(e);
      } finally {
        this.loading = false;
      }
    },
    async googleLogin() {
      this.error = '';
      this.loading = true;
      try {
        const provider = new GoogleAuthProvider();
        const result = await signInWithPopup(auth, provider);
        
        // Google 로그인 성공 후 사용자 정보 저장
        const user = result.user;
        const isNewUser = result._tokenResponse?.isNewUser;
        
        if (isNewUser) {
          // 새 사용자인 경우 언어 설정 모달 표시
          this.googleUser = user; // 모달에 사용할 사용자 객체 저장
          this.showLanguageSetupModal = true;
        } else {
          // 기존 사용자인 경우 바로 홈으로 이동
          if (user.email && user.email.toLowerCase() === 'admin@gmail.com') {
            this.$router.push('/management');
          } else {
            this.$router.push('/main');
          }
        }
      } catch (e) {
        this.error = this.friendlyError(e);
      } finally {
        this.loading = false;
      }
    },
    onLanguageSetupComplete() {
      this.showLanguageSetupModal = false;
      this.googleUser = null; // 모달 닫으면 사용자 객체 초기화
      const user = auth.currentUser;
      if (user && user.email && user.email.toLowerCase() === 'admin@gmail.com') {
        this.$router.push('/management');
      } else {
        this.$router.push('/main');
      }
    },
    friendlyError(e) {
      if (e.code === 'auth/email-already-in-use') return this.$t('error_email_in_use');
      if (e.code === 'auth/invalid-email') return this.$t('error_invalid_email');
      if (e.code === 'auth/weak-password') return this.$t('error_weak_password');
      if (e.code === 'auth/user-not-found' || e.code === 'auth/wrong-password') return this.$t('error_user_not_found');
      if (e.code === 'auth/popup-closed-by-user') return this.$t('error_popup_closed');
      return e.message || this.$t('error_unknown');
    },
    i18nState,
  },
};
</script>

<style scoped>
/* 네이버 지식iN 스타일 - Community.vue 베이스 */
.auth-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
  background-attachment: fixed;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  width: 100vw;
  max-width: 100vw;
  overflow-x: hidden;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.auth-content {
  width: 100%;
  max-width: 480px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 40px 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  box-sizing: border-box;
}
.auth-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 32px;
}

.auth-tabs button {
  flex: 1;
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

.auth-tabs button.active {
  background: #4A69E2;
  border-color: #4A69E2;
  color: white;
}
.auth-form {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

label {
  font-size: 14px;
  font-weight: 500;
  color: #212529;
}

input[type="email"],
input[type="password"],
input[type="text"],
select {
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

input:focus, select:focus {
  border-color: #4A69E2;
  background: white;
  box-shadow: 0 0 0 3px rgba(74, 105, 226, 0.1);
}
.auth-btn {
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

.auth-btn:disabled {
  background: #adb5bd;
  cursor: not-allowed;
}

.auth-btn:hover:not(:disabled) {
  background: #3B5BC7;
}

.google-btn {
  width: 100%;
  padding: 14px;
  background: white;
  color: #212529;
  font-size: 14px;
  font-weight: 500;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s ease;
}

.google-btn:disabled {
  background: #f8f9fa;
  color: #adb5bd;
  cursor: not-allowed;
}

.google-btn:hover:not(:disabled) {
  background: #f8f9fa;
  border-color: #ff6b35;
}

.google-icon {
  width: 20px;
  height: 20px;
}

.error-msg {
  color: #dc3545;
  font-size: 14px;
  text-align: center;
  padding: 8px;
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 6px;
}

/* 반응형 */
@media (max-width: 768px) {
  .auth-page {
    padding: 12px;
  }
  
  .auth-content {
    padding: 32px 20px;
  }
  
  .auth-tabs {
    gap: 6px;
    margin-bottom: 24px;
  }
  
  .auth-tabs button {
    padding: 10px 12px;
    font-size: 13px;
  }
  
  .auth-form {
    gap: 16px;
  }
  
  .form-group {
    gap: 6px;
  }
  
  label {
    font-size: 13px;
  }
  
  input[type="email"],
  input[type="password"],
  input[type="text"],
  select {
    padding: 12px;
    font-size: 13px;
  }
  
  .auth-btn {
    padding: 14px;
    font-size: 15px;
  }
  
  .google-btn {
    padding: 12px;
    font-size: 13px;
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

/* 모달 팝업 스타일 */
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
  
}
</style> 