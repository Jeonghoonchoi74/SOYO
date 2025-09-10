<template>
    <div class="search-chooser-page">
      <button class="back-btn" @click="goBack">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
        {{ $t('back') }}
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
  </style>