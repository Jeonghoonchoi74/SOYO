<template>
  <div class="test-container">
    <h1>📍 위치 정보 테스트</h1>
    
    <div class="location-info">
      <h2>현재 위치 정보</h2>
      
      <div v-if="loading" class="loading">
        <p>위치 정보를 확인하는 중...</p>
        <div class="spinner"></div>
      </div>
      
      <div v-else-if="error" class="error">
        <h3>❌ 오류 발생</h3>
        <p>{{ error }}</p>
        <button @click="getLocation" class="retry-btn">다시 시도</button>
      </div>
      
      <div v-else-if="location" class="success">
        <h3>✅ 위치 확인 완료</h3>
        <div class="location-details">
          <p><strong>위도 (Latitude):</strong> {{ location.latitude }}</p>
          <p><strong>경도 (Longitude):</strong> {{ location.longitude }}</p>
          <p><strong>정확도 (Accuracy):</strong> {{ location.accuracy }}m</p>
          <p><strong>확인 시간:</strong> {{ formatTime(location.timestamp) }}</p>
        </div>
        <button @click="getLocation" class="refresh-btn">새로고침</button>
      </div>
      
      <div v-else class="initial">
        <p>위치 정보를 확인하려면 아래 버튼을 클릭하세요.</p>
        <button @click="getLocation" class="get-location-btn">📍 현재 위치 확인</button>
      </div>
    </div>
    
    <div class="instructions">
      <h3>📋 사용 방법</h3>
      <ul>
        <li>브라우저에서 위치 접근 허용을 선택하세요</li>
        <li>실외에서 사용하면 더 정확한 위치를 얻을 수 있습니다</li>
        <li>GPS가 켜져 있는지 확인하세요</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const location = ref(null);
const loading = ref(false);
const error = ref(null);

const getLocation = () => {
  loading.value = true;
  error.value = null;
  
  if (!navigator.geolocation) {
    error.value = '브라우저가 위치 정보를 지원하지 않습니다.';
    loading.value = false;
    return;
  }
  
  navigator.geolocation.getCurrentPosition(
    (position) => {
      location.value = {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
        accuracy: position.coords.accuracy,
        timestamp: position.timestamp
      };
      loading.value = false;
    },
    (err) => {
      switch (err.code) {
        case err.PERMISSION_DENIED:
          error.value = '위치 접근이 거부되었습니다. 브라우저 설정에서 위치 접근을 허용해주세요.';
          break;
        case err.POSITION_UNAVAILABLE:
          error.value = '위치 정보를 사용할 수 없습니다.';
          break;
        case err.TIMEOUT:
          error.value = '위치 확인 시간이 초과되었습니다.';
          break;
        default:
          error.value = '알 수 없는 오류가 발생했습니다.';
      }
      loading.value = false;
    },
    {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 60000
    }
  );
};

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleString('ko-KR');
};

// 페이지 진입 시 자동으로 위치 확인
onMounted(() => {
  getLocation();
});
</script>

<style scoped>
.test-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}

.location-info {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 20px;
}

h2 {
  color: #495057;
  margin-bottom: 20px;
}

.loading {
  text-align: center;
  color: #6c757d;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 20px auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  color: #dc3545;
  text-align: center;
}

.success {
  color: #28a745;
}

.location-details {
  background: white;
  padding: 15px;
  border-radius: 8px;
  margin: 15px 0;
}

.location-details p {
  margin: 8px 0;
  font-size: 16px;
}

.instructions {
  background: #e9ecef;
  border-radius: 8px;
  padding: 15px;
}

.instructions h3 {
  color: #495057;
  margin-bottom: 10px;
}

.instructions ul {
  margin: 0;
  padding-left: 20px;
}

.instructions li {
  margin: 5px 0;
  color: #6c757d;
}

button {
  background: #007bff;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  margin: 10px 5px;
  transition: background-color 0.3s;
}

button:hover {
  background: #0056b3;
}

.retry-btn {
  background: #dc3545;
}

.retry-btn:hover {
  background: #c82333;
}

.refresh-btn {
  background: #28a745;
}

.refresh-btn:hover {
  background: #218838;
}

.get-location-btn {
  background: #17a2b8;
  font-size: 18px;
  padding: 15px 30px;
}

.get-location-btn:hover {
  background: #138496;
}

.initial {
  text-align: center;
  color: #6c757d;
}
</style> 