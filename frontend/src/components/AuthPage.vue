<template>
  <div class="auth-container">
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
          <option value="ko">{{ $t('lang_ko') }}</option>
          <option value="en">{{ $t('lang_en') }}</option>
          <option value="zh">{{ $t('lang_zh') }}</option>
          <option value="ja">{{ $t('lang_ja') }}</option>
        </select>
      </div>
      <div v-if="error" class="error-msg">{{ error }}</div>
      <button class="auth-btn" type="submit" :disabled="loading">
        {{ mode==='login' ? $t('login') : $t('signup') }}
      </button>
      <div class="divider">{{ $t('or') }}</div>
      <button class="google-btn" type="button" @click="googleLogin" :disabled="loading">
        <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" alt="Google" class="google-icon" />
        {{ $t('login_with_google') }}
      </button>
    </form>
    
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
            await fetch('http://localhost:5000/api/register_user', {
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
          this.$router.push('/');
        } else {
          await signInWithEmailAndPassword(auth, this.email, this.password);
          const user = auth.currentUser;
          if (user && user.email && user.email.toLowerCase() === 'admin@gmail.com') {
            this.$router.push('/management');
          } else {
            this.$router.push('/');
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
            this.$router.push('/');
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
        this.$router.push('/');
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
.auth-container {
  width: 480px;
  margin: 100px auto;
  padding: 48px 48px 56px 48px;
  border-radius: 32px;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-sizing: border-box;
}
.auth-tabs {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 2.5rem;
}
.auth-tabs button {
  font-size: 1.2rem;
  font-weight: 700;
  padding: 0.8rem 2.2rem;
  border: none;
  border-radius: 20px;
  background: #e2e8f0;
  color: #475569;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}
.auth-tabs button.active {
  background: #2563eb;
  color: #fff;
}
.auth-form {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
label {
  font-size: 1.05rem;
  font-weight: 600;
  color: #1e293b;
}
input[type="email"],
input[type="password"],
input[type="text"],
select {
  padding: 1rem 1.2rem;
  font-size: 1.1rem;
  border: 2px solid #cbd5e1;
  border-radius: 14px;
  background: #fff;
  color: #1e293b;
  outline: none;
  transition: border 0.2s;
}
input:focus, select:focus {
  border-color: #2563eb;
}
.auth-btn {
  width: 100%;
  padding: 1.2rem 0;
  background: #2563eb;
  color: #fff;
  font-size: 1.2rem;
  font-weight: 800;
  border: none;
  border-radius: 16px;
  cursor: pointer;
  transition: background 0.2s;
}
.auth-btn:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
}
.auth-btn:hover {
  background: #1d4ed8;
}
.divider {
  text-align: center;
  color: #64748b;
  margin: 1.2rem 0 0.5rem 0;
  font-size: 1rem;
}
.google-btn {
  width: 100%;
  padding: 1.1rem 0;
  background: #fff;
  color: #222;
  font-size: 1.1rem;
  font-weight: 700;
  border: 2px solid #cbd5e1;
  border-radius: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.7rem;
  transition: background 0.2s, border 0.2s;
}
.google-btn:disabled {
  background: #f1f5f9;
  color: #b0b0b0;
  cursor: not-allowed;
}
.google-btn:hover {
  background: #f1f5f9;
  border-color: #2563eb;
}
.google-icon {
  width: 24px;
  height: 24px;
}
.error-msg {
  color: #ef4444;
  font-size: 1rem;
  margin-bottom: -1rem;
  text-align: center;
}
</style> 