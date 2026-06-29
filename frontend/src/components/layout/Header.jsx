import { Settings } from 'lucide-react'

export function Header({ activeTab, tabs, onTabChange, onSettingsClick, llmConfigured }) {
  return (
    <header className="sticky top-0 z-40 border-b border-white/60 bg-white/75 shadow-sm shadow-blue-900/5 backdrop-blur-xl">
      <div className="container mx-auto px-4 max-w-7xl">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center space-x-3">
            <div className="breath-glow h-9 w-9 rounded-xl bg-gradient-to-br from-blue-600 via-cyan-500 to-violet-600 shadow-glow" />
            <h1 className="text-lg font-bold text-slate-900">采购成本与供应商搜索智能体</h1>
          </div>

          {/* 标签页导航 */}
          <nav className="hidden rounded-2xl border border-white/70 bg-white/55 p-1 shadow-inner shadow-blue-100/60 md:flex md:space-x-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={`rounded-xl px-4 py-2 text-sm font-semibold transition-all duration-300 ${
                  activeTab === tab.id
                    ? 'bg-gradient-to-r from-blue-600 to-cyan-500 text-white shadow-glow scale-[1.02]'
                    : 'text-slate-600 hover:bg-white/80 hover:text-blue-700 hover:shadow-sm'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>

          {/* 设置按钮 */}
          <button
            onClick={onSettingsClick}
            className="rounded-2xl border border-white/70 bg-white/60 p-2.5 shadow-sm transition-all duration-300 hover:-translate-y-0.5 hover:bg-white hover:shadow-glow"
            title="API 设置"
          >
            <Settings className={`h-5 w-5 ${llmConfigured ? 'text-emerald-500' : 'text-slate-500'}`} />
          </button>
        </div>

        {/* 移动端标签页 */}
        <nav className="flex space-x-2 overflow-x-auto pb-3 md:hidden">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`whitespace-nowrap rounded-xl px-3 py-1.5 text-sm font-semibold transition-all duration-300 ${
                activeTab === tab.id
                  ? 'bg-gradient-to-r from-blue-600 to-cyan-500 text-white shadow-glow'
                  : 'bg-white/60 text-slate-600 hover:bg-white hover:text-blue-700'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>
    </header>
  )
}