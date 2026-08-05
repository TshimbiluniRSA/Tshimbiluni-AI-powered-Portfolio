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
  return (
    <div className="app">
      <Header />
      <main>
        <Hero />
        <About />
        <BuildingToward />
        <Skills />
        <Projects />
        <section id="ai-chat" className="chat-section" aria-labelledby="ai-chat-title">
          <div className="container">
            <div className="chat-section-intro">
              <p className="section-kicker">AI Portfolio Assistant</p>
              <h2 id="ai-chat-title" className="section-title">Ask about my experience</h2>
              <p className="section-intro">
                Ask about my skills, work experience, projects, technical background,
                or anything else on this portfolio.
              </p>
            </div>
            <div className="embedded-chat">
              <Chat />
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  )
}

export default App
