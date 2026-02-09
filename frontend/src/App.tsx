import { useState } from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import About from './components/About';
import Skills from './components/Skills';
import Projects from './components/Projects';
import Chat from './components/Chat';
import Footer from './components/Footer';
import './App.css';

function App() {
  const [isChatOpen, setIsChatOpen] = useState(false);

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
      
      <button 
        className="chat-toggle-button" 
        onClick={() => setIsChatOpen(!isChatOpen)}
        aria-label="Toggle chat"
      >
        💬
      </button>
      
      <Chat isOpen={isChatOpen} onClose={() => setIsChatOpen(false)} />
    </div>
  );
}

export default App;
