import About from './components/About';
import Assistant from './components/Assistant';
import Contact from './components/Contact';
import Experience from './components/Experience';
import Footer from './components/Footer';
import Hero from './components/Hero';
import Projects from './components/Projects';
import { useReveal } from './hooks/useReveal';

export default function App() {
  useReveal();

  return (
    <>
      <a href="#main" className="skip-link">
        Skip to content
      </a>
      <main id="main">
        <Hero />
        <Projects />
        <Experience />
        <About />
        <Assistant />
        <Contact />
      </main>
      <Footer />
    </>
  );
}
