#!/usr/bin/env python3

# New App.jsx content with correct imports and paths
new_content = '''import React from 'react'
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
'''

with open('/home/ubuntu/erp/frontend/src/App.jsx', 'w') as f:
    f.write(new_content)

print("App.jsx updated successfully!")

# Verify
with open('/home/ubuntu/erp/frontend/src/App.jsx', 'r') as f:
    content = f.read()

print("\\n=== Verification ===")
old_items = ['Suppliers', 'Parts', 'MaterialIns', 'ProductOuts']
found_issues = False
for item in old_items:
    if f"import {item}" in content:
        print(f"ISSUE: import {item}")
        found_issues = True
    if f"'/suppliers'" in content or f"'/parts'" in content or f"'/material-ins'" in content or f"'/product-outs'" in content:
        print(f"ISSUE: old path found")
        found_issues = True

if not found_issues:
    print("All imports and paths are correct!")