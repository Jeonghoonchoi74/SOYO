<template>
    <div class="search-chooser-page">
      <button class="back-btn" @click="goBack">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
        뒤로가기
      </button>
      <div class="chooser-content">
        <div class="chooser-header">
          <h2 class="title">어떤 방식으로 추천을 받을까요?</h2>
          <p class="subtitle">원하는 방식에 따라 맞춤 장소를 추천해 드립니다.</p>
        </div>
        <div class="chooser-options">
          <div class="option-card" @click="goToFreeSearch">
            <div class="option-icon">⌨️</div>
            <h3 class="option-title">자유롭게 검색하기</h3>
            <p class="option-description">가고 싶은 곳, 하고 싶은 것을 자유롭게 입력하여 추천 받습니다.</p>
          </div>
          <div class="option-card" @click="goToGuidedSearch">
            <div class="option-icon">🗺️</div>
            <h3 class="option-title">가이드 따라 검색하기</h3>
            <p class="option-description">단계별 질문에 답변하며 나에게 꼭 맞는 장소를 찾아갑니다.</p>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'SearchChooser',
    methods: {
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
    background: #F7F8FA;
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
  }
  
  .chooser-header {
    margin-bottom: 40px;
  }
  
  .title {
    font-size: 28px;
    font-weight: 700;
    color: #212529;
    margin-bottom: 12px;
  }
  
  .subtitle {
    font-size: 18px;
    color: #6c757d;
  }
  
  .chooser-options {
    display: flex;
    gap: 24px;
    justify-content: center;
  }
  
  .option-card {
    background: white;
    border-radius: 16px;
    padding: 32px;
    width: 280px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    cursor: pointer;
    transition: all 0.2s ease;
    border: 1px solid #e9ecef;
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