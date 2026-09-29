# Portfolio frontend

The React and TypeScript single-page site for [tshimbiluniportfolio.tech](https://tshimbiluniportfolio.tech): experience, projects, skills and an AI assistant backed by the FastAPI API in [`backend/`](../backend).

## Development

```bash
npm ci
npm run dev
```

The site calls the production API by default. To use a local backend, create `.env.local`:

```env
VITE_API_URL=http://localhost:8000
```

## Scripts

| Command                | What it does                    |
| ---------------------- | ------------------------------- |
| `npm run dev`          | Vite dev server with hot reload |
| `npm run build`        | Type-check and build to `dist/` |
| `npm run lint`         | ESLint                          |
| `npm run format`       | Format with Prettier            |
| `npm run format:check` | Check formatting (run in CI)    |

## Structure

- `src/content/profile.ts`: all site copy (experience, projects, skills, links). Update it alongside the CV.
- `src/components/`: one component and stylesheet per section.
- `src/index.css`: design tokens (light and dark themes) and shared styles.
- `src/api/client.ts`: typed API client.
- `public/`: favicon, social preview image, `robots.txt` and `sitemap.xml`.

## Deployment

Render builds and deploys the site on every merge to `main`.
