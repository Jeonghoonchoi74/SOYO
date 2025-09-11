<template>
  <div class="home-page">
    <div class="white-container">
      <div class="image-container">
        <img 
          :src="currentImage" 
          :key="currentImage"
          alt="Search" 
          class="search-image"
        />
      </div>
      <div class="welcome-text">
        <h2 class="main-title">Search For Your Own Oasis!</h2>
        <p class="sub-title">SOYO에 어서오세요!</p>
      </div>
      <button class="start-btn" @click="goToMain">{{ $t('start') }}</button>
    </div>
  </div>
</template>

<script>
import { $t } from '../i18n';
import search1 from '../assets/search1.png';
import search2 from '../assets/search2.png';

export default {
  name: 'Home',
  data() {
    return {
      currentImageIndex: 0,
      images: [search1, search2],
      intervalId: null
    };
  },
  computed: {
    $t() { return $t; },
    currentImage() {
      return this.images[this.currentImageIndex];
    }
  },
  mounted() {
    this.startImageRotation();
  },
  beforeUnmount() {
    this.stopImageRotation();
  },
  methods: {
    goToMain() {
      this.$router.push('/main');
    },
    startImageRotation() {
      this.intervalId = setInterval(() => {
        this.currentImageIndex = (this.currentImageIndex + 1) % this.images.length;
      }, 500); // 0.5초마다 이미지 변경
    },
    stopImageRotation() {
      if (this.intervalId) {
        clearInterval(this.intervalId);
        this.intervalId = null;
      }
    }
  },
};
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
  background-attachment: fixed;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.white-container {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 30px;
  max-width: 400px;
  width: 100%;
}

.image-container {
  width: 200px;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0;
}

.search-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.welcome-text {
  text-align: center;
  margin-bottom: 5px;
  margin-top: 0;
}

.main-title {
  font-size: 20px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 8px 0;
  line-height: 1.3;
}

.sub-title {
  font-size: 16px;
  font-weight: 500;
  color: #6b7280;
  margin: 0;
  line-height: 1.4;
}

.start-btn {
  padding: 20px 40px;
  background: #4A69E2;
  color: white;
  font-size: 18px;
  font-weight: 600;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 25px rgba(74, 105, 226, 0.3);
}

.start-btn:hover {
  background: #3B5BC7;
  transform: translateY(-2px);
  box-shadow: 0 12px 35px rgba(74, 105, 226, 0.4);
}

.start-btn:active {
  transform: translateY(0);
}

/* 반응형 */
@media (max-width: 768px) {
  .white-container {
    padding: 30px;
    max-width: 350px;
  }
  
  .image-container {
    width: 150px;
    height: 150px;
  }
  
  .main-title {
    font-size: 18px;
  }
  
  .sub-title {
    font-size: 14px;
  }
  
  .start-btn {
    padding: 16px 32px;
    font-size: 16px;
  }
}

@media (max-width: 480px) {
  .white-container {
    padding: 24px;
    max-width: 300px;
    margin: 0 12px;
  }
  
  .image-container {
    width: 120px;
    height: 120px;
  }
  
  .main-title {
    font-size: 16px;
  }
  
  .sub-title {
    font-size: 13px;
  }
  
  .start-btn {
    padding: 14px 28px;
    font-size: 15px;
  }
}
</style>