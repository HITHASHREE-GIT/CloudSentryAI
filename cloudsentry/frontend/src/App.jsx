import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Sidebar from './components/Sidebar'
import Overview from './pages/Overview'
import Findings from './pages/Findings'
import FindingDetail from './pages/FindingDetail'
import Hub from './pages/Hub'

function App() {
  return (
    <Routes>
      {/* Public Hub — no Navbar/Sidebar */}
      <Route path="/hub" element={<Hub />} />

      {/* Main app layout */}
      <Route
        path="/*"
        element={
          <div className="app-layout">
            <Navbar />
            <Sidebar />
            <main className="main-content">
              <Routes>
                <Route path="/" element={<Overview />} />
                <Route path="/findings" element={<Findings />} />
                <Route path="/findings/:id" element={<FindingDetail />} />
              </Routes>
            </main>
          </div>
        }
      />
    </Routes>
  )
}

export default App