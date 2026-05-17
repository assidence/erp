import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import AppLayout from './components/Layout'

// Pages
import Dashboard from './pages/Dashboard'
import Customers from './pages/Customers'
import Foundries from './pages/Foundries'
import Castings from './pages/Castings'
import CastingIns from './pages/CastingIns'
import WorkpieceOuts from './pages/WorkpieceOuts'
import ProductionPlans from './pages/ProductionPlans'
import PaymentPlans from './pages/PaymentPlans'
import QualityIssues from './pages/QualityIssues'

function App() {
  return (
    <AppLayout>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/customers" element={<Customers />} />
        <Route path="/foundries" element={<Foundries />} />
        <Route path="/castings" element={<Castings />} />
        <Route path="/casting-ins" element={<CastingIns />} />
        <Route path="/workpiece-outs" element={<WorkpieceOuts />} />
        <Route path="/production-plans" element={<ProductionPlans />} />
        <Route path="/payment-plans" element={<PaymentPlans />} />
        <Route path="/quality-issues" element={<QualityIssues />} />
      </Routes>
    </AppLayout>
  )
}

export default App
