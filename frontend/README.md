# Tshimbiluni AI-Powered Portfolio - Frontend

A modern, professional portfolio website built with React, TypeScript, and Vite, featuring AI-powered chat capabilities.

## 🚀 Features

- **Modern Design**: Beautiful gradient-based UI with smooth animations
- **AI Chat Integration**: Interactive AI assistant powered by OpenAI
- **GitHub Integration**: Real-time profile data from GitHub API
- **Responsive Design**: Fully responsive across all devices
- **TypeScript**: Type-safe development experience
- **Fast Build**: Lightning-fast builds with Vite

## 📁 Project Structure

```
src/
├── api/
│   └── client.ts           # API client with TypeScript types
├── components/
│   ├── Header.tsx/.css     # Navigation header with smooth scrolling
│   ├── Hero.tsx/.css       # Hero section with GitHub profile
│   ├── About.tsx/.css      # About section with highlights
│   ├── Skills.tsx/.css     # Skills organized by category
│   ├── Projects.tsx/.css   # Featured projects showcase
│   ├── Chat.tsx/.css       # AI chat interface
│   └── Footer.tsx/.css     # Footer with social links
├── App.tsx/.css            # Main app component
├── index.css               # Global styles and resets
└── main.tsx                # App entry point
```

## 🛠️ Technologies

- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Axios** - HTTP client
- **CSS3** - Styling with custom properties

## 🚦 Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.example .env.local
```

3. Configure environment variables in `.env.local`:
```env
VITE_API_URL=http://localhost:8000
VITE_GITHUB_USERNAME=TshimbiluniRSA
```

### Development

Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build

Build for production:
```bash
npm run build
```

Preview production build:
```bash
npm run preview
```

### Linting

Run ESLint:
```bash
npm run lint
```

## 🎨 Design Features

- **Gradient Theme**: Purple/blue gradient (#667eea to #764ba2)
- **Smooth Animations**: Transitions and hover effects
- **Custom Scrollbar**: Themed scrollbar matching design
- **Floating Chat Button**: Fixed position AI assistant toggle
- **Responsive Grid**: Adaptive layouts for all screen sizes

## 📡 API Integration

The frontend connects to the FastAPI backend for:

- **Chat API**: Send messages, manage sessions
- **GitHub API**: Sync and fetch profile data
- **LinkedIn API**: Fetch professional profile

All API calls are typed with TypeScript interfaces for type safety.

## 🌐 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` |
| `VITE_GITHUB_USERNAME` | GitHub username | `TshimbiluniRSA` |

## 📱 Responsive Breakpoints

- Mobile: < 576px
- Tablet: 576px - 968px
- Desktop: > 968px

## 🔧 Development Notes

- Uses `import type` syntax for TypeScript type imports
- Environment variables accessed via `import.meta.env`
- All components follow a modular structure with separate CSS files
- Smooth scrolling implemented globally
- Custom scrollbar styling for better UX

## 📄 License

This project is part of the Tshimbiluni AI-powered Portfolio.
