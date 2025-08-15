<template>
  <div id="app" class="app">
    <!-- Accessibility Toolbar -->
    <AccessibilityToolbar 
      @toggle-high-contrast="toggleHighContrast"
      @toggle-large-text="toggleLargeText"
      @toggle-tts="toggleTTS"
    />
    
    <!-- Main Content -->
    <main class="main-content" :class="accessibilityClasses">
      <div class="container">
        <!-- Header -->
        <header class="header">
          <div class="header-content">
            <h1 class="title">
              <span class="icon" aria-hidden="true">🎓</span>
              Educational QA Bot
            </h1>
            <p class="subtitle">
              AI-powered learning assistant to help answer your educational questions
            </p>
          </div>
        </header>
        
        <!-- Chat Interface -->
        <section class="chat-section" aria-label="Chat Interface">
          <ChatPanel 
            :high-contrast="highContrast"
            :large-text="largeText"
            :tts-enabled="ttsEnabled"
            @speak-text="handleSpeakText"
          />
        </section>
      </div>
    </main>
    
    <!-- Skip Link for Accessibility -->
    <a href="#main-content" class="skip-link">Skip to main content</a>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import ChatPanel from './components/ChatPanel.vue'
import AccessibilityToolbar from './components/AccessibilityToolbar.vue'

// Accessibility state
const highContrast = ref(false)
const largeText = ref(false)
const ttsEnabled = ref(false)

// Computed classes for accessibility
const accessibilityClasses = computed(() => ({
  'high-contrast': highContrast.value,
  'large-text': largeText.value
}))

// TTS functionality
let speechSynthesis: SpeechSynthesis | null = null

onMounted(() => {
  // Initialize TTS if available
  if ('speechSynthesis' in window) {
    speechSynthesis = window.speechSynthesis
  }
  
  // Load saved accessibility preferences
  loadAccessibilityPreferences()
  
  // Announce page load for screen readers
  announcePageLoad()
})

const toggleHighContrast = () => {
  highContrast.value = !highContrast.value
  saveAccessibilityPreferences()
  
  // Announce change
  if (speechSynthesis && ttsEnabled.value) {
    const message = highContrast.value ? 'High contrast enabled' : 'High contrast disabled'
    speak(message)
  }
}

const toggleLargeText = () => {
  largeText.value = !largeText.value
  saveAccessibilityPreferences()
  
  // Announce change
  if (speechSynthesis && ttsEnabled.value) {
    const message = largeText.value ? 'Large text enabled' : 'Large text disabled'
    speak(message)
  }
}

const toggleTTS = () => {
  ttsEnabled.value = !ttsEnabled.value
  saveAccessibilityPreferences()
  
  // Test TTS when enabling
  if (ttsEnabled.value && speechSynthesis) {
    speak('Text to speech enabled')
  }
}

const handleSpeakText = (text: string) => {
  if (ttsEnabled.value) {
    speak(text)
  }
}

const speak = (text: string) => {
  if (!speechSynthesis || !ttsEnabled.value) return
  
  // Cancel any ongoing speech
  speechSynthesis.cancel()
  
  const utterance = new SpeechSynthesisUtterance(text)
  utterance.rate = 0.9
  utterance.pitch = 1
  utterance.volume = 0.8
  
  speechSynthesis.speak(utterance)
}

const loadAccessibilityPreferences = () => {
  try {
    const preferences = localStorage.getItem('accessibility-preferences')
    if (preferences) {
      const parsed = JSON.parse(preferences)
      highContrast.value = parsed.highContrast || false
      largeText.value = parsed.largeText || false
      ttsEnabled.value = parsed.ttsEnabled || false
    }
  } catch (error) {
    console.warn('Failed to load accessibility preferences:', error)
  }
}

const saveAccessibilityPreferences = () => {
  try {
    const preferences = {
      highContrast: highContrast.value,
      largeText: largeText.value,
      ttsEnabled: ttsEnabled.value
    }
    localStorage.setItem('accessibility-preferences', JSON.stringify(preferences))
  } catch (error) {
    console.warn('Failed to save accessibility preferences:', error)
  }
}

const announcePageLoad = () => {
  // Create announcement for screen readers
  const announcement = document.createElement('div')
  announcement.setAttribute('aria-live', 'polite')
  announcement.setAttribute('aria-atomic', 'true')
  announcement.className = 'sr-only'
  announcement.textContent = 'Educational QA Bot loaded. Use the chat interface to ask questions.'
  
  document.body.appendChild(announcement)
  
  // Remove after announcement
  setTimeout(() => {
    document.body.removeChild(announcement)
  }, 2000)
}
</script>