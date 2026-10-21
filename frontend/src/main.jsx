/**
 * P.R.I.S.M. Frontend Entry Point
 * Initializes the React application and mounts the root component to the DOM.
 */
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

// Import global stylesheets (Tailwind/CSS configurations)
import './index.css'

// Import the primary Application component containing the UI layout and state logic
import App from './App.jsx'

// Mount the React application to the standard 'root' div defined in index.html
createRoot(document.getElementById('root')).render(
  // StrictMode enables additional development checks, helping catch potential 
  // memory leaks in the polling hooks before they reach production
  <StrictMode>
    <App />
  </StrictMode>,
)