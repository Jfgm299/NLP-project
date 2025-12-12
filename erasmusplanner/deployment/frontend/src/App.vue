<script setup>
import ChatInterface from './components/ChatInterface.vue'
</script>

<template>
  <div class="glass-wrapper">
    <ChatInterface />
  </div>
</template>


<style>
/* Reset */
body {
  margin: 0;
  padding: 0;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;

  .glass-wrapper {
    width: 100vw;
    height: 100vh;
    backdrop-filter: blur(15px) brightness(1.1);
    -webkit-backdrop-filter: blur(15px) brightness(1.1);
    background: rgba(255, 255, 255, 0.05);
  }


  /* === THE GRAINY PURPLE GRADIENT === */
  background-color: #4c1d95; /* Deep base */
  background-image: 
    /* The Noise Texture */
    url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.05'/%3E%3C/svg%3E"),
    /* The Color Blobs */
    radial-gradient(at 0% 0%, #e879f9 0px, transparent 50%), /* Top Left Fuchsia */
    radial-gradient(at 100% 0%, #8b5cf6 0px, transparent 50%), /* Top Right Violet */
    radial-gradient(at 100% 100%, #4c1d95 0px, transparent 50%), /* Bottom Dark */
    radial-gradient(at 0% 100%, #7c3aed 0px, transparent 50%); /* Bottom Left Electric */
  
  background-size: 100% 100%, 120% 120%; /* Scale noise and gradient */
  background-position: center;
  background-repeat: repeat, no-repeat;
}
</style>