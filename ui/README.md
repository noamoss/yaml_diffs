# YAML Diff UI

A GitHub PR review-style UI for comparing and reviewing changes in YAML documents.

## Features

- **YAML Editor**: CodeMirror-based editor with syntax highlighting and RTL support for Hebrew content
- **File Upload**: Drag-and-drop or click to upload YAML files
- **Diff Visualization**: GitHub PR-style change cards with character-level diff highlighting
- **Threaded Discussions**: Add comments and replies to specific changes
- **Export**: Download diff results and discussions as JSON

## Development

### Prerequisites

- Node.js 18+ and npm
- Access to the Railway API backend

### Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env.local` file:
```bash
cp .env.example .env.local
```

3. Update `NEXT_PUBLIC_API_URL` in `.env.local` with your Railway API URL

4. Run development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Build

```bash
npm run build
npm start
```

## Deployment

### Vercel

1. Connect your GitHub repository to Vercel
2. Set root directory to `ui/`
3. Add environment variable `NEXT_PUBLIC_API_URL` with your Railway API URL
4. Deploy

### Railway CORS Configuration

**For Local Development:**
Add `http://localhost:3000` to the Railway API's `CORS_ORIGINS` environment variable in Railway project settings:

```
CORS_ORIGINS=http://localhost:3000
```

**For Production (Vercel):**
After deploying to Vercel, add your Vercel domain to the Railway API's `CORS_ORIGINS` environment variable:

```
CORS_ORIGINS=http://localhost:3000,https://your-vercel-app.vercel.app
```

**Note:** You can add multiple origins separated by commas. Make sure to include both localhost for development and your Vercel domain for production.

## Tech Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **CodeMirror 6** - YAML editor
- **React Query** - API state management
- **Zustand** - Local state for discussions
- **diff-match-patch** - Character-level diff highlighting
