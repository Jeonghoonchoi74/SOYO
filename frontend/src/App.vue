<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { getAuth, onAuthStateChanged } from 'firebase/auth';
import Home from './components/Home.vue';

const router = useRouter();
onMounted(() => {
  const auth = getAuth();
  onAuthStateChanged(auth, (user) => {
    if (user && user.email && user.email.toLowerCase() === 'admin@gmail.com' && router.currentRoute.value.path !== '/management') {
      router.replace('/management');
    }
  });
});
</script>

<template>
  <router-view />
</template>