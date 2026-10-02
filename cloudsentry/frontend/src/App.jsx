import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Sidebar from './components/Sidebar'
import Overview from './pages/Overview'
import Findings from './pages/Findings'
import FindingDetail from './pages/FindingDetail'

function App() {
  return (
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
  )
}

export default App