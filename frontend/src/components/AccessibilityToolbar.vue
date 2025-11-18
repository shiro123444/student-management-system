<template>
  <nav class="accessibility-toolbar" role="toolbar" aria-label="Accessibility options">
    <div class="toolbar-container">
      <h2 class="toolbar-title">
        <span class="icon" aria-hidden="true">♿</span>
        Accessibility
      </h2>
      
      <div class="toolbar-controls">
        <!-- High Contrast Toggle -->
        <button
          @click="$emit('toggle-high-contrast')"
          class="toolbar-button"
          type="button"
          :class="{ active: highContrast }"
          :aria-pressed="highContrast"
          aria-describedby="high-contrast-help"
        >
          <span class="button-icon" aria-hidden="true">🌗</span>
          <span class="button-text">High Contrast</span>
        </button>
        
        <!-- Large Text Toggle -->
        <button
          @click="$emit('toggle-large-text')"
          class="toolbar-button"
          type="button"
          :class="{ active: largeText }"
          :aria-pressed="largeText"
          aria-describedby="large-text-help"
        >
          <span class="button-icon" aria-hidden="true">🔍</span>
          <span class="button-text">Large Text</span>
        </button>
        
        <!-- Text-to-Speech Toggle -->
        <button
          @click="handleTTSToggle"
          class="toolbar-button"
          type="button"
          :class="{ active: ttsEnabled, disabled: !ttsSupported }"
          :aria-pressed="ttsEnabled"
          :disabled="!ttsSupported"
          aria-describedby="tts-help"
        >
          <span class="button-icon" aria-hidden="true">🔊</span>
          <span class="button-text">Read Aloud</span>
        </button>
        
        <!-- Font Size Controls -->
        <div class="font-size-controls" role="group" aria-label="Font size controls">
          <button
            @click="decreaseFontSize"
            class="toolbar-button font-button"
            type="button"
            :disabled="fontSize <= minFontSize"
            aria-label="Decrease font size"
          >
            <span class="button-icon" aria-hidden="true">A-</span>
          </button>
          
          <span class="font-size-display" aria-live="polite">
            {{ Math.round(fontSize * 100) }}%
          </span>
          
          <button
            @click="increaseFontSize"
            class="toolbar-button font-button"
            type="button"
            :disabled="fontSize >= maxFontSize"
            aria-label="Increase font size"
          >
            <span class="button-icon" aria-hidden="true">A+</span>
          </button>
        </div>
        
        <!-- Reset Button -->
        <button
          @click="resetAccessibility"
          class="toolbar-button reset-button"
          type="button"
          aria-label="Reset all accessibility settings"
        >
          <span class="button-icon" aria-hidden="true">↺</span>
          <span class="button-text">Reset</span>
        </button>
        
        <!-- Help Button -->
        <button
          @click="showHelp = !showHelp"
          class="toolbar-button help-button"
          type="button"
          :aria-expanded="showHelp"
          aria-controls="accessibility-help"
        >
          <span class="button-icon" aria-hidden="true">❓</span>
          <span class="button-text">Help</span>
        </button>
      </div>
    </div>
    
    <!-- Help Panel -->
    <div
      v-if="showHelp"
      id="accessibility-help"
      class="help-panel"
      role="region"
      aria-label="Accessibility help information"
    >
      <div class="help-content">
        <h3>Accessibility Features</h3>
        
        <div class="help-section">
          <h4 id="high-contrast-help">High Contrast Mode</h4>
          <p>Increases contrast between text and background for better visibility.</p>
        </div>
        
        <div class="help-section">
          <h4 id="large-text-help">Large Text Mode</h4>
          <p>Increases text size throughout the application for easier reading.</p>
        </div>
        
        <div class="help-section">
          <h4 id="tts-help">Text-to-Speech</h4>
          <p>
            Enables audio reading of chat messages. 
            {{ ttsSupported ? 'Click the speaker button next to messages to hear them read aloud.' : 'Not supported in your browser.' }}
          </p>
        </div>
        
        <div class="help-section">
          <h4>Keyboard Navigation</h4>
          <ul>
            <li><kbd>Tab</kbd> - Navigate between interactive elements</li>
            <li><kbd>Enter</kbd> - Activate buttons and send messages</li>
            <li><kbd>Shift + Enter</kbd> - New line in message input</li>
            <li><kbd>Escape</kbd> - Close dialogs and help panels</li>
          </ul>
        </div>
        
        <div class="help-section">
          <h4>Screen Reader Support</h4>
          <p>This application is optimized for screen readers with proper ARIA labels and live regions.</p>
        </div>
        
        <button
          @click="showHelp = false"
          class="close-help-button"
          type="button"
          aria-label="Close accessibility help"
        >
          ✕ Close
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'

// Props
interface Props {
  highContrast?: boolean
  largeText?: boolean
  ttsEnabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  highContrast: false,
  largeText: false,
  ttsEnabled: false
})

// Emits
const emit = defineEmits<{
  'toggle-high-contrast': []
  'toggle-large-text': []
  'toggle-tts': []
  'font-size-change': [size: number]
}>()

// State
const showHelp = ref(false)
const fontSize = ref(1.0)
const minFontSize = 0.8
const maxFontSize = 1.5
const ttsSupported = ref(false)

// Check TTS support
onMounted(() => {
  ttsSupported.value = 'speechSynthesis' in window
  loadFontSize()
  
  // Close help panel on Escape key
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})

// Watch font size changes and apply to document
watch(fontSize, (newSize) => {
  document.documentElement.style.fontSize = `${newSize}rem`
  saveFontSize()
  emit('font-size-change', newSize)
})

const handleTTSToggle = () => {
  if (ttsSupported.value) {
    emit('toggle-tts')
  }
}

const increaseFontSize = () => {
  if (fontSize.value < maxFontSize) {
    fontSize.value = Math.min(maxFontSize, fontSize.value + 0.1)
  }
}

const decreaseFontSize = () => {
  if (fontSize.value > minFontSize) {
    fontSize.value = Math.max(minFontSize, fontSize.value - 0.1)
  }
}

const resetAccessibility = () => {
  fontSize.value = 1.0
  
  // Reset other settings through parent component
  if (props.highContrast) emit('toggle-high-contrast')
  if (props.largeText) emit('toggle-large-text')
  if (props.ttsEnabled) emit('toggle-tts')
  
  // Announce reset
  announceToScreenReader('Accessibility settings reset to defaults')
}

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && showHelp.value) {
    showHelp.value = false
  }
}

const loadFontSize = () => {
  try {
    const saved = localStorage.getItem('accessibility-font-size')
    if (saved) {
      fontSize.value = parseFloat(saved)
    }
  } catch (error) {
    console.warn('Failed to load font size:', error)
  }
}

const saveFontSize = () => {
  try {
    localStorage.setItem('accessibility-font-size', fontSize.value.toString())
  } catch (error) {
    console.warn('Failed to save font size:', error)
  }
}

const announceToScreenReader = (message: string) => {
  const announcement = document.createElement('div')
  announcement.setAttribute('aria-live', 'polite')
  announcement.setAttribute('aria-atomic', 'true')
  announcement.className = 'sr-only'
  announcement.textContent = message
  
  document.body.appendChild(announcement)
  
  setTimeout(() => {
    document.body.removeChild(announcement)
  }, 1000)
}
</script>