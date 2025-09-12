<template>
    <div class="search-chooser-page">
      <!-- 도움말 버튼 -->
    <!-- 도움말 버튼 (오른쪽 하단) -->
    <button class="help-btn" @click="showTutorial">
      ?
    </button>

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
      

      <!-- 튜토리얼 팝업 -->
      <div v-if="showTutorialModal" class="modal-overlay" @click="closeTutorial">
        <div class="modal-box tutorial-modal" @click.stop>
          <div class="modal-header">
            <h3>{{ $t('tutorial_title') }}</h3>
            <button class="close-btn" @click="closeTutorial">×</button>
          </div>
          <div class="tutorial-content">
            <div class="tutorial-step" v-for="(step, index) in tutorialSteps" :key="index">
              <div class="step-number">{{ index + 1 }}</div>
              <div class="step-content">
                <h4>{{ $t(step.title) }}</h4>
                <p>{{ $t(step.description) }}</p>
              </div>
            </div>
          </div>
          <div class="modal-actions">
            <button class="modal-btn primary" @click="closeTutorial">{{ $t('tutorial_got_it') }}</button>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { $t } from '../i18n';
  
  export default {
    name: 'SearchChooser',
    data() {
      return {
        showTutorialModal: false,
        tutorialSteps: [
          {
            title: 'tutorial_step1_title',
            description: 'tutorial_step1_desc'
          },
          {
            title: 'tutorial_step2_title',
            description: 'tutorial_step2_desc'
          },
          {
            title: 'tutorial_step3_title',
            description: 'tutorial_step3_desc'
          },
          {
            title: 'tutorial_step4_title',
            description: 'tutorial_step4_desc'
          },
          {
            title: 'tutorial_step5_title',
            description: 'tutorial_step5_desc'
          },
          {
            title: 'tutorial_step6_title',
            description: 'tutorial_step6_desc'
          },
          {
            title: 'tutorial_step7_title',
            description: 'tutorial_step7_desc'
          }
        ]
      };
    },
    methods: {
      $t(key) {
        return $t(key);
      },
      goBack() {
        this.$router.push('/main');
      },
      goToFreeSearch() {
        this.$router.push('/preference');
      },
      goToGuidedSearch() {
        this.$router.push('/search/guided');
      },
      goHome() {
        this.$router.push('/main');
      },
      showTutorial() {
        this.showTutorialModal = true;
      },
      closeTutorial() {
        this.showTutorialModal = false;
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

  /* 도움말 버튼 */
.help-btn {
  position: fixed;
  bottom: 20px;
  right: 20px;
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

  /* 튜토리얼 모달 스타일 */
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

  /* 튜토리얼 팝업 스타일 */
  .tutorial-modal {
    max-width: 600px;
    max-height: 80vh;
  }

  .tutorial-content {
    padding: 20px 24px;
    max-height: 60vh;
    overflow-y: auto;
  }

  .tutorial-step {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    margin-bottom: 24px;
    padding-bottom: 20px;
    border-bottom: 1px solid #f1f3f4;
  }

  .tutorial-step:last-child {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
  }

  .step-number {
    background: #4A69E2;
    color: white;
    border-radius: 50%;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 14px;
    flex-shrink: 0;
  }

  .step-content h4 {
    margin: 0 0 8px 0;
    font-size: 16px;
    font-weight: 600;
    color: #212529;
  }

  .step-content p {
    margin: 0;
    font-size: 14px;
    color: #6b7280;
    line-height: 1.5;
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
    bottom: 15px;
    right: 15px;
    border: 2px solid white;
    font-size: 16px;
  }

  .help-btn svg {
    width: 18px;
    height: 18px;
    stroke: white;
    fill: none;
  }
    
    .tutorial-modal {
      max-width: 95vw;
      max-height: 85vh;
    }
    
    .tutorial-content {
      padding: 16px 20px;
      max-height: 65vh;
    }
    
    .tutorial-step {
      gap: 12px;
      margin-bottom: 20px;
      padding-bottom: 16px;
    }
    
    .step-number {
      width: 28px;
      height: 28px;
      font-size: 13px;
    }
    
    .step-content h4 {
      font-size: 15px;
    }
    
    .step-content p {
      font-size: 13px;
    }
  }
  </style>