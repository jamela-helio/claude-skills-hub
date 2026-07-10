import { Route, Routes } from 'react-router-dom'
import Sidebar from './components/Sidebar.jsx'
import Dashboard from './pages/Dashboard.jsx'
import GwaAutofill from './pages/GwaAutofill.jsx'
import GwaReport from './pages/GwaReport.jsx'
import HelioReport from './pages/HelioReport.jsx'
import HelioTiers from './pages/HelioTiers.jsx'
import LandUsePrompt from './pages/LandUsePrompt.jsx'
import HtmlPopulator from './pages/HtmlPopulator.jsx'

export default function App() {
  return (
    <div className="app-shell">
      <Sidebar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/gwa-autofill" element={<GwaAutofill />} />
          <Route path="/gwa-report" element={<GwaReport />} />
          <Route path="/helio-report" element={<HelioReport />} />
          <Route path="/helio-tiers" element={<HelioTiers />} />
          <Route path="/html-populator" element={<HtmlPopulator />} />
          <Route path="/land-use-prompt" element={<LandUsePrompt />} />
        </Routes>
      </main>
    </div>
  )
}
