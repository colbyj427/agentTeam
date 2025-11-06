import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'
import { installExitBeacon } from './services/exitBeacon';

// Install a beacon that notifies the backend when the tab/app closes
installExitBeacon();

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
