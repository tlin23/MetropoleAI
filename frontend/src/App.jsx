import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import './App.css'
import styles from './App.styles.js'

function App() {
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [inputFocused, setInputFocused] = useState(false)
  const messagesEndRef = useRef(null)

  // Welcome message
  const welcomeMessage = {
    id: 'welcome',
    text: 'Welcome to Metropole.AI! I can help answer questions about the building, maintenance, rules, and more. How can I assist you today?',
    sender: 'bot'
  }

  // Display welcome message on initial load
  useEffect(() => {
    setMessages([welcomeMessage])
  }, [])

  // Scroll to bottom of messages when messages change
  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  // Reset chat function
  const handleReset = () => {
    setMessages([welcomeMessage])
    setInputValue('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!inputValue.trim()) return

    const userMessage = {
      id: Date.now(),
      text: inputValue,
      sender: 'user'
    }

    // Add user message to chat
    setMessages(prevMessages => [...prevMessages, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      // Send request to backend
      const response = await axios.post('/api/ask', {
        question: userMessage.text
      })

      // Add bot response to chat
      setMessages(prevMessages => [
        ...prevMessages,
        {
          id: Date.now(),
          text: response.data.answer || "I'm sorry, I couldn't find an answer to that.",
          sender: 'bot'
        }
      ])
    } catch (error) {   
      // Add error message to chat
      setMessages(prevMessages => [
        ...prevMessages,
        {
          id: Date.now(),
          text: "Sorry, there was an error processing your request. Please try again.",
          sender: 'bot'
        }
      ])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div style={styles.container}>
      {/* App Header */}
      <header style={styles.header}>
        <h1 style={styles.headerTitle}>Metropole.AI</h1>
        <button 
          onClick={handleReset} 
          style={styles.resetButton}
        >
          Start Over
        </button>
      </header>

      {/* Chat Container */}
      <main style={styles.main}>
        {/* Message Display Area (Scrollable) */}
        <div style={styles.messageArea}>
          {messages.length === 0 ? (
            <div style={styles.emptyMessage}>
              No messages yet. Start a conversation!
            </div>
          ) : (
            messages.map(message => (
              <div 
                key={message.id}
                style={{
                  ...styles.messageContainer,
                  ...(message.sender === 'user' ? styles.messageRight : styles.messageLeft)
                }}
              >
                <div 
                  style={{
                    ...styles.messageBubble,
                    ...(message.sender === 'user' ? styles.userBubble : styles.botBubble)
                  }}
                >
                  {message.text}
                </div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Form */}
        <form 
          onSubmit={handleSubmit}
          style={styles.form}
        >
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onFocus={() => setInputFocused(true)}
            onBlur={() => setInputFocused(false)}
            placeholder="Ask a question about the building..."
            style={{
              ...styles.input,
              ...(inputFocused ? styles.inputFocus : {})
            }}
          />
          <button
            type="submit"
            disabled={isLoading}
            style={{
              ...styles.button,
              ...(isLoading ? styles.buttonDisabled : {})
            }}
          >
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </form>
      </main>
    </div>
  )
}

export default App
