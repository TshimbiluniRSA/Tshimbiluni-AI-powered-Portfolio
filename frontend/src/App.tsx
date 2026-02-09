import { useState } from 'react'
import './App.css'
import Header from './components/Header'
import Hero from './components/Hero'
import About from './components/About'
import Skills from './components/Skills'
import Projects from './components/Projects'
import Chat from './components/Chat'
import Footer from './components/Footer'

function App() {
  const [isChatOpen, setIsChatOpen] = useState(false)

  return (
    <div className="app">
      <Header />
      <main>
        <Hero />
        <About />
        <Skills />
        <Projects />
      </main>
      <Footer />
      
      {/* Floating Chat Button */}
      <button 
        className="chat-toggle-btn"
        onClick={() => setIsChatOpen(!isChatOpen)}
        aria-label="Toggle AI Chat"
      >
        💬
      </button>
      
      {/* Chat Modal */}
      {isChatOpen && (
        <div className="chat-modal">
          <Chat onClose={() => setIsChatOpen(false)} />
        </div>
      )}
    </div>
  )
}

export default App
