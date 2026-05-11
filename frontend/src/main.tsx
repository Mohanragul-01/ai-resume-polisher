import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'


// Find the <div id="root"> element in index.html.
// This is where React will render the entire app.
const rootElement = document.getElementById('root')

// If the root element is missing (which should never happen),
// stop early with a clear error instead of a cryptic crash.
if (!rootElement) {
  throw new Error('Could not find #root element in index.html')
}

// Mount the React app inside the root element.
// StrictMode helps catch common mistakes during development —
// it has no effect in production builds.
createRoot(rootElement).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
