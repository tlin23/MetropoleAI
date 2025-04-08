import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import './App.css'

// Inline styles
const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
    backgroundColor: '#f3f4f6'
  },
  header: {
    backgroundColor: '#2563eb',
    color: 'white',
    padding: '16px',
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
  },
  headerTitle: {
    fontSize: '1.25rem',
    fontWeight: 'bold'
  },
  main: {
    flex: 1,
    overflow: 'hidden',
    display: 'flex',
    flexDirection: 'column',
    padding: '16px'
  },
  messageArea: {
    flex: 1,
    overflowY: 'auto',
    marginBottom: '16px',
    borderRadius: '8px',
    backgroundColor: 'white',
    boxShadow: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
    padding: '16px'
  },
  emptyMessage: {
    textAlign: 'center',
    color: '#6b7280',
    margin: '32px 0'
  },
  messageContainer: {
    marginBottom: '16px'
  },
  messageRight: {
    textAlign: 'right'
  },
  messageLeft: {
    textAlign: 'left'
  },
  messageBubble: {
    display: 'inline-block',
    maxWidth: '80%',
    padding: '8px 16px',
    borderRadius: '8px'
  },
  userBubble: {
    backgroundColor: '#2563eb',
    color: 'white',
    borderBottomRightRadius: 0
  },
  botBubble: {
    backgroundColor: '#e5e7eb',
    color: '#1f2937',
    borderBottomLeftRadius: 0
  },
  form: {
    display: 'flex',
    gap: '8px',
    backgroundColor: 'white',
    borderRadius: '8px',
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    padding: '8px'
  },
  input: {
    flex: 1,
    padding: '8px',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    outline: 'none'
  },
  inputFocus: {
    borderColor: '#2563eb',
    boxShadow: '0 0 0 2px rgba(37, 99, 235, 0.2)'
  },
  button: {
    padding: '8px 16px',
    borderRadius: '6px',
    backgroundColor: '#2563eb',
    color: 'white',
    border: 'none',
    cursor: 'pointer',
    transition: 'background-color 0.2s'
  },
  buttonHover: {
    backgroundColor: '#1d4ed8'
  },
  buttonDisabled: {
    backgroundColor: '#93c5fd',
    cursor: 'not-allowed'
  }
};

function App() {
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [inputFocused, setInputFocused] = useState(false)
  const messagesEndRef = useRef(null)

  // Scroll to bottom of messages when messages change
  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
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
      console.error('Error sending message:', error)
      
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
