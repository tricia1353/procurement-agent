import { useState, useEffect } from 'react'
import { Header } from './components/layout/Header'
import { PriceTracker } from './components/price/PriceTracker'
import { SupplierFinder } from './components/supplier/SupplierFinder'
import { SettingsModal } from './components/common/SettingsModal'
import { useLocalStorage } from './hooks/useLocalStorage'
import { api } from './services/api'

function App() {
  const [activeTab, setActiveTab] = useState('price')
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [apiKeys, setApiKeys] = useLocalStorage('jintian_api_keys', {
    llmToken: '',
    mouserApiKey: ''
  })
  const [llmConfigured, setLlmConfigured] = useState(false)

  useEffect(() => {
    checkHealth()
  }, [apiKeys])

  const checkHealth = async () => {
    try {
      const health = await api.getHealth()
      setLlmConfigured(health.llm_configured || !!apiKeys.llmToken)
    } catch {
      setLlmConfigured(!!apiKeys.llmToken)
    }
  }

  const handleSaveSettings = (newKeys) => {
    setApiKeys(newKeys)
    setSettingsOpen(false)
  }

  const tabs = [
    { id: 'price', label: '采购成本分析' },
    { id: 'supplier', label: '供应商搜索' },
  ]

  return (
    <div className="relative min-h-screen overflow-hidden bg-gradient-to-br from-slate-50 via-blue-50 to-cyan-50">
      <div className="pointer-events-none fixed inset-0 z-0">
        <div className="absolute -top-24 left-10 h-72 w-72 rounded-full bg-cyan-300/30 blur-3xl animate-breath" />
        <div className="absolute top-40 right-0 h-96 w-96 rounded-full bg-blue-400/20 blur-3xl animate-breath-slow" />
        <div className="absolute bottom-[-120px] left-1/3 h-80 w-80 rounded-full bg-violet-300/20 blur-3xl animate-breath" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(59,130,246,0.12),transparent_32%),radial-gradient(circle_at_bottom_right,rgba(6,182,212,0.12),transparent_30%)]" />
      </div>

      <div className="relative z-10">
        <Header
          activeTab={activeTab}
          tabs={tabs}
          onTabChange={setActiveTab}
          onSettingsClick={() => setSettingsOpen(true)}
          llmConfigured={llmConfigured}
        />

        <main className="container mx-auto px-4 py-6 max-w-7xl">
          {activeTab === 'price' && <PriceTracker />}
          {activeTab === 'supplier' && <SupplierFinder />}
        </main>
      </div>

      {settingsOpen && (
        <SettingsModal
          isOpen={settingsOpen}
          onClose={() => setSettingsOpen(false)}
          onSave={handleSaveSettings}
          initialValues={apiKeys}
        />
      )}
    </div>
  )
}

export default App