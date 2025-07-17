import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';

const firebaseConfig = {
    apiKey: "AIzaSyCv6s8bNrtZnvRSkkhdF0vRMsGGqHrM-AA",
    authDomain: "testproject-139f1.firebaseapp.com",
    projectId: "testproject-139f1",
    storageBucket: "testproject-139f1.firebasestorage.app",
    messagingSenderId: "861164325868",
    appId: "1:861164325868:web:88564f2d490841d11bcec9",
    measurementId: "G-CET2MRQNNX"
  };

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app); 