import { initializeApp } from "firebase/app";
import { getAuth, signInAnonymously } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

const firebaseConfig = {
  apiKey: "AIzaSyARKzapuoleotwPSVRxBOTvPP8RXLmDth4",
  authDomain: "civicguide-pw-2026.firebaseapp.com",
  projectId: "civicguide-pw-2026",
  storageBucket: "civicguide-pw-2026.firebasestorage.app",
  messagingSenderId: "396731383793",
  appId: "1:396731383793:web:85c48bbb87e26f2f9b0e50"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);

/**
 * Sign in user anonymously
 * @returns A promise that resolves when the user is signed in.
 */
export const signInUser = async () => {
  try {
    const userCredential = await signInAnonymously(auth);
    return userCredential.user;
  } catch (error) {
    console.error("Error signing in anonymously:", error);
    throw error;
  }
};
