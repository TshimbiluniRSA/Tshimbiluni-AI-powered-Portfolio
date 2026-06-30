import { useState } from 'react'
import './App.css'
import Header from './components/Header'
import Hero from './components/Hero'
import About from './components/About'
import Skills from './components/Skills'
import Projects from './components/Projects'
import BuildingToward from './components/BuildingToward'
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
        <BuildingToward />
        <Skills />
        <Projects />
      </main>
      <Footer />
      
      {/* Floating Chat Button */}
      <button 
        className="chat-toggle-btn"
        onClick={() => setIsChatOpen(!isChatOpen)}
        aria-label={isChatOpen ? "Close AI chat" : "Open AI chat"} title={isChatOpen ? "Close AI chat" : "Open AI chat"}
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
