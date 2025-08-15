<template>
  <div class="chat-panel" :class="chatPanelClasses">
    <!-- Status Bar -->
    <div class="status-bar" role="status" aria-live="polite">
      <span class="status-indicator" :class="connectionStatus">
        {{ connectionStatus === 'connected' ? 'Connected' : 'Connecting...' }}
      </span>
      <button 
        v-if="messages.length > 0"
        @click="clearChat"
        class="clear-button"
        type="button"
        aria-label="Clear chat history"
      >
        Clear Chat
      </button>
    </div>
    
    <!-- Messages Container -->
    <div 
      ref="messagesContainer"
      class="messages-container"
      role="log"
      aria-label="Chat messages"
      aria-live="polite"
    >
      <!-- Welcome Message -->
      <div v-if="messages.length === 0" class="welcome-message">
        <div class="welcome-content">
          <h2>👋 Welcome to Educational QA Bot!</h2>
          <p>Ask me any educational question and I'll help you learn.</p>
          <div class="example-questions">
            <h3>Try asking:</h3>
            <button 
              v-for="example in exampleQuestions"
              :key="example"
              @click="sendMessage(example)"
              class="example-button"
              type="button"
            >
              {{ example }}
            </button>
          </div>
        </div>
      </div>
      
      <!-- Chat Messages -->
      <div 
        v-for="message in messages"
        :key="message.id"
        class="message"
        :class="[`message-${message.sender}`, { 'message-error': message.error }]"
      >
        <div class="message-header">
          <span class="message-sender">
            {{ message.sender === 'user' ? 'You' : 'AI Assistant' }}
          </span>
          <span class="message-time">
            {{ formatTime(message.timestamp) }}
          </span>
          <button 
            v-if="ttsEnabled && message.content"
            @click="$emit('speak-text', message.content)"
            class="speak-button"
            type="button"
            :aria-label="`Read message from ${message.sender}`"
          >
            🔊
          </button>
        </div>
        
        <div class="message-content">
          <div v-if="message.sender === 'assistant' && message.thinking" class="thinking-indicator">
            <span>🤔 Thinking...</span>
          </div>
          
          <div 
            v-html="formatMessage(message.content)"
            class="message-text"
          ></div>
          
          <!-- Sources -->
          <div v-if="message.sources && message.sources.length > 0" class="message-sources">
            <details class="sources-details">
              <summary class="sources-summary">
                📚 Sources ({{ message.sources.length }})
              </summary>
              <ul class="sources-list">
                <li 
                  v-for="source in message.sources"
                  :key="source.id"
                  class="source-item"
                >
                  <div class="source-header">
                    <strong>{{ source.title }}</strong>
                    <span class="source-score">{{ Math.round(source.relevance_score * 100) }}% relevant</span>
                  </div>
                  <p class="source-preview">{{ source.content_preview }}</p>
                </li>
              </ul>
            </details>
          </div>
          
          <!-- Follow-up suggestions -->
          <div v-if="message.suggested_followups && message.suggested_followups.length > 0" class="followups">
            <p class="followups-title">💡 Follow-up questions:</p>
            <button 
              v-for="followup in message.suggested_followups"
              :key="followup"
              @click="sendMessage(followup)"
              class="followup-button"
              type="button"
            >
              {{ followup }}
            </button>
          </div>
        </div>
      </div>
      
      <!-- Loading indicator -->
      <div v-if="isLoading" class="message message-assistant">
        <div class="message-header">
          <span class="message-sender">AI Assistant</span>
        </div>
        <div class="message-content">
          <div class="loading-indicator">
            <div class="loading-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <span class="loading-text">Processing your question...</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Input Form -->
    <form @submit.prevent="handleSubmit" class="input-form" role="search">
      <div class="input-container">
        <label for="message-input" class="sr-only">Enter your question</label>
        <textarea
          id="message-input"
          ref="inputElement"
          v-model="currentMessage"
          @keydown="handleKeydown"
          class="message-input"
          placeholder="Ask an educational question..."
          rows="1"
          :disabled="isLoading"
          aria-describedby="input-help"
          maxlength="2000"
        ></textarea>
        
        <button
          type="submit"
          class="send-button"
          :disabled="!currentMessage.trim() || isLoading"
          :aria-label="isLoading ? 'Processing...' : 'Send message'"
        >
          <span v-if="isLoading" class="send-icon loading">⏳</span>
          <span v-else class="send-icon">📤</span>
        </button>
      </div>
      
      <div id="input-help" class="input-help">
        Press Enter to send, Shift+Enter for new line
      </div>
      
      <!-- Character counter -->
      <div class="character-counter" :class="{ 'near-limit': currentMessage.length > 1800 }">
        {{ currentMessage.length }}/2000
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, watch } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { chatApi } from '@/services/api'

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
  'speak-text': [text: string]
}>()

// Types
interface ChatMessage {
  id: string
  sender: 'user' | 'assistant'
  content: string
  timestamp: Date
  sources?: Array<{
    id: string
    title: string
    content_preview: string
    relevance_score: number
  }>
  suggested_followups?: string[]
  error?: boolean
  thinking?: boolean
}

// Reactive state
const messages = ref<ChatMessage[]>([])
const currentMessage = ref('')
const isLoading = ref(false)
const connectionStatus = ref<'connected' | 'connecting' | 'disconnected'>('connected')
const sessionId = ref<string>('')

// Refs
const messagesContainer = ref<HTMLElement>()
const inputElement = ref<HTMLTextAreaElement>()

// Example questions
const exampleQuestions = [
  "What is photosynthesis?",
  "Explain the Pythagorean theorem",
  "How does machine learning work?",
  "What caused World War I?"
]

// Computed
const chatPanelClasses = computed(() => ({
  'high-contrast': props.highContrast,
  'large-text': props.largeText
}))

// Initialize session
onMounted(() => {
  sessionId.value = generateSessionId()
  checkConnection()
  
  // Focus input
  inputElement.value?.focus()
})

// Auto-scroll to bottom when messages change
watch(messages, () => {
  nextTick(() => {
    scrollToBottom()
  })
})

// Auto-resize textarea
watch(currentMessage, () => {
  nextTick(() => {
    autoResizeTextarea()
  })
})

const generateSessionId = (): string => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}

const checkConnection = async () => {
  try {
    connectionStatus.value = 'connecting'
    await chatApi.healthCheck()
    connectionStatus.value = 'connected'
  } catch (error) {
    connectionStatus.value = 'disconnected'
    console.error('Connection check failed:', error)
  }
}

const handleSubmit = () => {
  if (currentMessage.value.trim() && !isLoading.value) {
    sendMessage(currentMessage.value.trim())
  }
}

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    handleSubmit()
  }
}

const sendMessage = async (messageText: string) => {
  if (!messageText.trim() || isLoading.value) return
  
  // Add user message
  const userMessage: ChatMessage = {
    id: generateMessageId(),
    sender: 'user',
    content: messageText,
    timestamp: new Date()
  }
  
  messages.value.push(userMessage)
  currentMessage.value = ''
  isLoading.value = true
  
  try {
    // Call API
    const response = await chatApi.sendMessage({
      query: messageText,
      session_id: sessionId.value,
      include_sources: true,
      max_sources: 3
    })
    
    // Add assistant response
    const assistantMessage: ChatMessage = {
      id: generateMessageId(),
      sender: 'assistant',
      content: response.response,
      timestamp: new Date(),
      sources: response.sources,
      suggested_followups: response.suggested_followups
    }
    
    messages.value.push(assistantMessage)
    
    // Announce new message for screen readers
    announceMessage(response.response)
    
  } catch (error) {
    console.error('Failed to send message:', error)
    
    // Add error message
    const errorMessage: ChatMessage = {
      id: generateMessageId(),
      sender: 'assistant',
      content: 'Sorry, I encountered an error processing your question. Please try again.',
      timestamp: new Date(),
      error: true
    }
    
    messages.value.push(errorMessage)
  } finally {
    isLoading.value = false
    inputElement.value?.focus()
  }
}

const clearChat = () => {
  if (confirm('Are you sure you want to clear the chat history?')) {
    messages.value = []
    sessionId.value = generateSessionId()
    
    // Announce for screen readers
    announceMessage('Chat history cleared')
  }
}

const formatMessage = (content: string): string => {
  try {
    // Convert markdown to HTML
    const html = marked(content, {
      breaks: true,
      gfm: true
    })
    
    // Sanitize HTML
    return DOMPurify.sanitize(html)
  } catch (error) {
    console.error('Message formatting error:', error)
    return DOMPurify.sanitize(content)
  }
}

const formatTime = (timestamp: Date): string => {
  return timestamp.toLocaleTimeString(undefined, {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const generateMessageId = (): string => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2, 5)
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const autoResizeTextarea = () => {
  if (inputElement.value) {
    inputElement.value.style.height = 'auto'
    inputElement.value.style.height = Math.min(inputElement.value.scrollHeight, 120) + 'px'
  }
}

const announceMessage = (text: string) => {
  // Create temporary element for screen reader announcement
  const announcement = document.createElement('div')
  announcement.setAttribute('aria-live', 'polite')
  announcement.setAttribute('aria-atomic', 'true')
  announcement.className = 'sr-only'
  announcement.textContent = `AI Assistant: ${text.slice(0, 100)}${text.length > 100 ? '...' : ''}`
  
  document.body.appendChild(announcement)
  
  setTimeout(() => {
    document.body.removeChild(announcement)
  }, 1000)
}
</script>