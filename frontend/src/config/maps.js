// Google Maps API 설정
export const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || 'YOUR_GOOGLE_MAPS_API_KEY';

// Google Maps API URL
export const GOOGLE_MAPS_API_URL = 'https://maps.googleapis.com/maps/api/js';

// 지도 기본 설정
export const MAP_DEFAULT_CONFIG = {
  zoom: 15,
  mapTypeId: 'roadmap',
  streetViewControl: false,
  fullscreenControl: false,
  mapTypeControl: false,
  zoomControl: true,
  scrollwheel: true,
  disableDoubleClickZoom: false,
  draggable: true,
  clickableIcons: false
};

// 마커 기본 설정
export const MARKER_DEFAULT_CONFIG = {
  animation: null, // Google Maps API 로드 후 동적으로 설정
  clickable: true,
  draggable: false
};
