import { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Overview from './pages/Overview';
import AreaView from './pages/AreaView';
import AusbildungsplaetzeAdmin from './pages/AusbildungsplaetzeAdmin';
import APAbdeckungOverview from './pages/APAbdeckungOverview';
import APAbdeckungDetail from './pages/APAbdeckungDetail';
import RotationsplanungView from './pages/RotationsplanungView';

function AppShell() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="app-layout">
      <Header onToggleSidebar={() => setSidebarOpen(p => !p)} />
      <div className="below-header">
        {sidebarOpen && (
          <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)} />
        )}
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <main className="main-content">
          <Routes>
            <Route path="/"                                    element={<Navigate to="/overview" replace />} />
            <Route path="/overview"                            element={<Overview />} />
            <Route path="/area/:areaId"                        element={<AreaView />} />
            <Route path="/ap-abdeckung"                        element={<APAbdeckungOverview />} />
            <Route path="/ap-abdeckung/:bildungsplanKey"       element={<APAbdeckungDetail />} />
            <Route path="/admin/ausbildungsplaetze"            element={<AusbildungsplaetzeAdmin />} />
            <Route path="/rotationsplanung"                    element={<RotationsplanungView />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <AppShell />
      </BrowserRouter>
    </AppProvider>
  );
}
