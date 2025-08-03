import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import ChatPage from '@/pages/ChatPage'
import DocumentsPage from '@/pages/DocumentsPage'
import WizardPage from '@/pages/WizardPage'
import Layout from '@/components/Layout'

function App() {
  const [branding, setBranding] = useState({
    company_name: 'White Label Chat',
    primary_color: '#8A2BE2',
    welcome_message: 'Welcome to our modern chat platform',
    logo_url: '',
    chat_placeholder: 'Type your message...',
    footer_text: 'Powered by White Label Chat SaaS'
  })

  return (
    <Router>
      <Layout branding={branding}>
        <Routes>
          <Route path="/" element={<ChatPage branding={branding} />} />
          <Route path="/chat" element={<ChatPage branding={branding} />} />
          <Route path="/documents" element={<DocumentsPage branding={branding} />} />
          <Route path="/wizard" element={<WizardPage branding={branding} onBrandingUpdate={setBranding} />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
