<template>
  <div class="mypage-page">
    <button class="back-btn" @click="goBack">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M19 12H5M12 19l-7-7 7-7"/>
      </svg>
      {{ $t('back') }}
    </button>
    
    <div class="mypage-content">
      <div class="mypage-header">
        <h2 class="title">{{ $t('mypage_title') }}</h2>
        <p class="subtitle">{{ $t('mypage_subtitle') }}</p>
      </div>
      
      <div class="user-info">
        <div class="user-avatar">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
            <circle cx="12" cy="7" r="4" />
          </svg>
        </div>
        <div class="user-details">
          <div class="user-name-section">
            <h3 class="user-name" v-if="!isEditingName">{{ userName || '사용자' }}</h3>
            <div class="name-edit-container" v-else>
              <input 
                v-model="editingName" 
                class="name-input" 
                :placeholder="$t('enter_name')"
                @keyup.enter="saveUserName"
                @keyup.escape="cancelEditName"
                ref="nameInput"
              />
            </div>
            <button class="edit-name-btn" @click="toggleNameEdit" v-if="!isEditingName">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
              </svg>
            </button>
            <div class="name-edit-actions" v-if="isEditingName">
              <button class="save-btn" @click="saveUserName">{{ $t('save') }}</button>
              <button class="cancel-btn" @click="cancelEditName">{{ $t('cancel') }}</button>
            </div>
          </div>
          <p class="user-email">{{ userEmail }}</p>
          <p class="user-uid">{{ $t('user_id') }}: {{ userUid }}</p>
        </div>
      </div>
      
      <div class="settings-section">
        <h3 class="section-title">{{ $t('settings') }}</h3>
        
        <!-- 언어 설정 -->
        <div class="setting-item">
          <div class="setting-info">
            <h4 class="setting-label">{{ $t('language_setting') }}</h4>
            <p class="setting-description">{{ $t('language_setting_desc') }}</p>
          </div>
          <button class="language-btn" @click="openLanguageModal">
            <span class="current-lang">{{ getCurrentLanguageName() }}</span>
            <span class="dropdown-icon">▼</span>
          </button>
        </div>
        
        <!-- 회원탈퇴 -->
        <div class="setting-item danger">
          <div class="setting-info">
            <h4 class="setting-label">{{ $t('delete_account') }}</h4>
            <p class="setting-description">{{ $t('delete_account_desc') }}</p>
          </div>
          <button class="delete-btn" @click="openDeleteModal">
            {{ $t('delete_account_btn') }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- 언어 선택 모달 -->
    <div v-if="showLanguageModal" class="modal-overlay" @click="closeLanguageModal">
      <div class="modal-box" @click.stop>
        <div class="modal-header">
          <h3>{{ $t('select_language') }}</h3>
          <button class="close-btn" @click="closeLanguageModal">×</button>
        </div>
        <div class="language-options">
          <button 
            v-for="lang in languages" 
            :key="lang.code" 
            class="language-option" 
            :class="{ active: selectedLang === lang.code }"
            @click="selectLanguage(lang.code)"
          >
            <span class="flag">{{ lang.flag }}</span>
            <span class="lang-name">{{ lang.name }}</span>
          </button>
        </div>
      </div>
    </div>
    
    <!-- 회원탈퇴 확인 모달 -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="closeDeleteModal">
      <div class="modal-box" @click.stop>
        <div class="modal-header">
          <h3>{{ $t('delete_account_confirm_title') }}</h3>
          <button class="close-btn" @click="closeDeleteModal">×</button>
        </div>
        <div class="modal-content">
          <p class="warning-text">
            {{ $t('delete_account_confirm_message') }}
          </p>
          <div class="modal-actions">
            <button class="modal-btn cancel" @click="closeDeleteModal">{{ $t('cancel') }}</button>
            <button class="modal-btn danger" @click="deleteAccount">{{ $t('delete_account_btn') }}</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { onAuthStateChanged, signOut, deleteUser } from 'firebase/auth';
import { auth } from '../firebase';
import { i18nState, $t } from '../i18n';

export default {
  name: 'Mypage',
  data() {
    return {
      userEmail: '',
      userUid: '',
      userName: '',
      selectedLang: 'ko',
      showLanguageModal: false,
      showDeleteModal: false,
      isEditingName: false,
      editingName: '',
      languages: [
        { code: 'ko', name: '한국어', flag: '🇰🇷' },
        { code: 'en', name: 'English', flag: '🇺🇸' },
        { code: 'zh', name: '中文', flag: '🇨🇳' },
        { code: 'ja', name: '日本語', flag: '🇯🇵' },
      ],
    };
  },
  computed: {
    $t() { return $t; },
  },
  mounted() {
    onAuthStateChanged(auth, (user) => {
      if (user) {
        this.userEmail = user.email;
        this.userUid = user.uid;
        this.selectedLang = i18nState.lang || 'ko';
        this.loadUserInfo();
      } else {
        this.$router.push('/');
      }
    });
  },
  methods: {
    goBack() {
      this.$router.push('/');
    },
    async loadUserInfo() {
      try {
        const response = await fetch(`/api/get_user_info/${this.userUid}`);
        const data = await response.json();
        if (data.success && data.user) {
          this.userName = data.user.name || '';
        }
      } catch (error) {
        console.error('사용자 정보 로드 실패:', error);
      }
    },
    toggleNameEdit() {
      this.isEditingName = true;
      this.editingName = this.userName;
      this.$nextTick(() => {
        this.$refs.nameInput?.focus();
      });
    },
    cancelEditName() {
      this.isEditingName = false;
      this.editingName = '';
    },
    async saveUserName() {
      if (!this.editingName.trim()) {
        alert('이름을 입력해주세요.');
        return;
      }
      
      if (this.editingName.trim().length < 2) {
        alert('이름은 최소 2글자 이상이어야 합니다.');
        return;
      }
      
      try {
        const response = await fetch('/api/update_user_name', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            uid: this.userUid,
            name: this.editingName.trim()
          })
        });
        
        const data = await response.json();
        if (data.success) {
          this.userName = this.editingName.trim();
          this.isEditingName = false;
          this.editingName = '';
          alert('이름이 성공적으로 변경되었습니다.');
        } else {
          alert(data.error || '이름 변경에 실패했습니다.');
        }
      } catch (error) {
        console.error('이름 변경 실패:', error);
        alert('이름 변경 중 오류가 발생했습니다.');
      }
    },
    getCurrentLanguageName() {
      const lang = this.languages.find(l => l.code === this.selectedLang);
      return lang ? lang.name : '한국어';
    },
    openLanguageModal() {
      this.showLanguageModal = true;
    },
    closeLanguageModal() {
      this.showLanguageModal = false;
    },
    async selectLanguage(langCode) {
      this.selectedLang = langCode;
      i18nState.lang = langCode;
      
      // 백엔드에 언어 설정 업데이트
      try {
        const response = await fetch('/api/update_user_language', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            uid: this.userUid,
            lang: langCode
          })
        });
        
        if (!response.ok) {
          throw new Error('Failed to update user language');
        }
        
        this.showLanguageModal = false;
        alert(this.$t('language_change_success'));
      } catch (error) {
        console.error('언어 설정 업데이트 실패:', error);
        alert(this.$t('language_change_error'));
      }
    },
    openDeleteModal() {
      this.showDeleteModal = true;
    },
    closeDeleteModal() {
      this.showDeleteModal = false;
    },
    async deleteAccount() {
      try {
        const user = auth.currentUser;
        if (!user) {
          alert(this.$t('login_required_alert'));
          return;
        }
        
        // 백엔드에서 사용자 데이터 삭제
        const response = await fetch('/api/delete_user', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            uid: user.uid
          })
        });
        
        if (!response.ok) {
          throw new Error('Failed to delete user data');
        }
        
        // Firebase 계정 삭제
        await deleteUser(user);
        
        alert(this.$t('delete_account_success'));
        this.$router.push('/');
      } catch (error) {
        console.error('회원탈퇴 실패:', error);
        alert(this.$t('delete_account_error'));
      }
    }
  },
};
</script>

<style scoped>
.mypage-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
  background-attachment: fixed;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  padding: 20px;
  position: relative;
}

.back-btn {
  position: absolute;
  top: 20px;
  left: 20px;
  background: white;
  color: #4A69E2;
  border: 1px solid #4A69E2;
  border-radius: 8px;
  padding: 10px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
  z-index: 1000;
}

.back-btn:hover {
  background: #4A69E2;
  color: white;
}

.mypage-content {
  width: 100%;
  max-width: 480px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 40px 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  margin: 0 auto;
  box-sizing: border-box;
}

.mypage-header {
  text-align: center;
  margin-bottom: 32px;
}

.title {
  font-size: 24px;
  font-weight: 700;
  color: #212529;
  margin-bottom: 8px;
}

.subtitle {
  font-size: 16px;
  color: #6c757d;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  margin-bottom: 32px;
}

.user-avatar {
  width: 60px;
  height: 60px;
  background: #4A69E2;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.user-details {
  flex: 1;
}

.user-name-section {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.user-name {
  font-size: 20px;
  font-weight: 700;
  color: #212529;
  margin: 0;
}

.edit-name-btn {
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.edit-name-btn:hover {
  background: #f8f9fa;
  color: #4A69E2;
}

.name-edit-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.name-input {
  font-size: 20px;
  font-weight: 700;
  color: #212529;
  border: 2px solid #4A69E2;
  border-radius: 8px;
  padding: 8px 12px;
  background: white;
  outline: none;
  min-width: 120px;
}

.name-input:focus {
  border-color: #0984e3;
  box-shadow: 0 0 0 3px rgba(74, 105, 226, 0.1);
}

.name-edit-actions {
  display: flex;
  gap: 8px;
}

.save-btn, .cancel-btn {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s ease;
}

.save-btn {
  background: #4A69E2;
  color: white;
}

.save-btn:hover {
  background: #0984e3;
}

.cancel-btn {
  background: #f8f9fa;
  color: #6c757d;
  border: 1px solid #e9ecef;
}

.cancel-btn:hover {
  background: #e9ecef;
  color: #212529;
}

.user-email {
  font-size: 16px;
  font-weight: 500;
  color: #6c757d;
  margin-bottom: 4px;
}

.user-uid {
  font-size: 14px;
  color: #6c757d;
}

.settings-section {
  margin-top: 24px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #212529;
  margin-bottom: 20px;
}

.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 0;
  border-bottom: 1px solid #e9ecef;
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-item.danger {
  border-bottom: 1px solid #f8d7da;
}

.setting-info {
  flex: 1;
}

.setting-label {
  font-size: 16px;
  font-weight: 600;
  color: #212529;
  margin-bottom: 4px;
}

.setting-description {
  font-size: 14px;
  color: #6c757d;
}

.language-btn {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 10px 16px;
  font-size: 14px;
  font-weight: 500;
  color: #495057;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
}

.language-btn:hover {
  background: #e9ecef;
  color: #212529;
}

.current-lang {
  color: #4A69E2;
  font-weight: 600;
}

.delete-btn {
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.delete-btn:hover {
  background: #c82333;
}

/* 모달 스타일 */
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
}

.modal-box {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  width: 100%;
  max-width: 480px;
  max-height: 85vh;
  overflow-y: auto;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
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
  background: #e9ecef;
}

.language-option.active {
  background: #4A69E2;
  color: white;
  border-color: #4A69E2;
}

.flag {
  font-size: 20px;
}

.lang-name {
  flex: 1;
  text-align: left;
}

.modal-content {
  padding: 20px 24px 24px 24px;
}

.warning-text {
  font-size: 16px;
  color: #212529;
  line-height: 1.6;
  margin-bottom: 24px;
  text-align: center;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.modal-btn {
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s ease;
}

.modal-btn.cancel {
  background: #f8f9fa;
  color: #495057;
  border: 1px solid #e9ecef;
}

.modal-btn.cancel:hover {
  background: #e9ecef;
  color: #212529;
}

.modal-btn.danger {
  background: #dc3545;
  color: white;
}

.modal-btn.danger:hover {
  background: #c82333;
}

/* 반응형 */
@media (max-width: 768px) {
  .mypage-content {
    padding: 32px 20px;
    margin: 0 12px;
  }
  
  .user-info {
    flex-direction: column;
    text-align: center;
  }
  
  .setting-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .language-btn,
  .delete-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
