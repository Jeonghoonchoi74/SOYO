<template>
    <div class="search-chooser-page">
      <button class="back-btn" @click="goBack">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
      </button>
      <div class="chooser-content">
        <div class="chooser-box">
        <div class="chooser-header">
          <h2 class="title">{{ $t('search_chooser_title') }}</h2>
          <p class="subtitle">{{ $t('search_chooser_subtitle') }}</p>
        </div>
        <div class="chooser-options">
          <div class="option-card" @click="goToFreeSearch">
            <div class="option-icon">⌨️</div>
            <h3 class="option-title">{{ $t('search_chooser_free_title') }}</h3>
            <p class="option-description">{{ $t('search_chooser_free_desc') }}</p>
          </div>
          <div class="option-card" @click="goToGuidedSearch">
            <div class="option-icon">🗺️</div>
            <h3 class="option-title">{{ $t('search_chooser_guided_title') }}</h3>
            <p class="option-description">{{ $t('search_chooser_guided_desc') }}</p>
          </div>
        </div>
        </div>
      </div>
      
      <!-- 홈 버튼 (오른쪽 하단) -->
      <button class="float-btn home-float-btn" @click="goHome">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
          <polyline points="9,22 9,12 15,12 15,22" />
        </svg>
      </button>
    </div>
  </template>
  
  <script>
  import { $t } from '../i18n';
  
  export default {
    name: 'SearchChooser',
    methods: {
      $t(key) {
        return $t(key);
      },
      goBack() {
        this.$router.push('/');
      },
      goToFreeSearch() {
        this.$router.push('/preference');
      },
      goToGuidedSearch() {
        this.$router.push('/search/guided');
      },
      goHome() {
        this.$router.push('/');
      }
    }
  };
  </script>
  
  <style scoped>
  .search-chooser-page {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
    background-attachment: fixed;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    padding: 20px;
    position: relative;
  }

  .back-btn {
    position: fixed;
    bottom: 20px;
    left: 20px;
    width: 56px;
    height: 56px;
    border-radius: 50%;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    border: none;
    background: #4A69E2;
    color: white;
    cursor: pointer;
    transition: all 0.2s ease;
    z-index: 1000;
  }

  .back-btn:hover {
    background: #3B5BC7;
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
  }
  
  .chooser-content {
    width: 100%;
    max-width: 640px;
    text-align: center;
    position: relative;
    z-index: 5;
  }

  .chooser-box {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 16px;
    padding: 40px 32px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  }
  
  .chooser-header {
    margin-bottom: 40px;
  }
  
  .title {
    font-size: 28px;
    font-weight: 700;
    color: #212529;
    margin-bottom: 12px;
    text-shadow: none;
  }
  
  .subtitle {
    font-size: 18px;
    color: #495057;
    text-shadow: none;
  }
  
  .chooser-options {
    display: flex;
    gap: 24px;
    justify-content: center;
  }
  
  .option-card {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 16px;
    padding: 32px;
    width: 280px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    cursor: pointer;
    transition: all 0.2s ease;
    position: relative;
    z-index: 10;
  }
  
  .option-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
    border-color: #4A69E2;
  }
  
  .option-icon {
    font-size: 48px;
    margin-bottom: 20px;
  }
  
  .option-title {
    font-size: 20px;
    font-weight: 600;
    color: #343a40;
    margin-bottom: 12px;
  }
  
  .option-description {
    font-size: 14px;
    color: #6c757d;
    line-height: 1.6;
  }
  
  @media (max-width: 768px) {
    .chooser-options {
      flex-direction: column;
      align-items: center;
    }
    .option-card {
      width: 100%;
      max-width: 350px;
    }
  }

  /* 플로팅 버튼 스타일 */
  .float-btn {
    position: fixed;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    border: none;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  .float-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
  }

  .home-float-btn {
    bottom: 20px;
    right: 20px;
    background: #28a745;
    color: white;
  }

  .home-float-btn:hover {
    background: #218838;
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
  }

  /* 모바일 반응형 */
  @media (max-width: 768px) {
    .float-btn {
      width: 50px;
      height: 50px;
    }
    
    .home-float-btn {
      right: 20px;
    }
  }
  </style>