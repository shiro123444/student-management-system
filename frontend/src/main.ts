import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

// Global styles
import './style.css'

// Create Vue app
const app = createApp(App)

// Add Pinia store
app.use(createPinia())

// Global error handler
app.config.errorHandler = (err, vm, info) => {
  console.error('Vue Error:', err)
  console.error('Component:', vm)
  console.error('Info:', info)
}

// Mount app
app.mount('#app')