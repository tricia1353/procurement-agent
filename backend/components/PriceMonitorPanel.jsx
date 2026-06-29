"""
价格监控管理组件
"""

import { useState } from 'react'
import { Plus, Trash2, RefreshCw, Play, Pause, Calendar, BarChart3, List, Settings } from 'lucide-react'
import { useApi } from '../../hooks/useApi'
import { api } from '../../services/api'

export function PriceMonitorPanel() {
  const [watchList, setWatchList] = useState([
    "STM32F103C8T6",
    "ESP32-WROOM-32",
    "LM7805"
  ])
  const [newModel, setNewModel] = useState('')

  const { data: statusData, execute: getWatchList, execute: addWatch, execute: removeWatch, execute: getSchedulerStatus } = useApi(api.getWatchList)
  const { data: recordData, execute: recordNow } = useApi(api.record_now)

  const [schedulerStatus, setSchedulerStatus] = useState({ running: false })

  // 获取监控列表
  const fetchWatchList = async () => {
    const data = await getWatchList()
    if (data) {
      setWatchList(data.watch_list || [])
    }
  }

  // 获取调度器状态
  const fetchSchedulerStatus = async () => {
    const data = await getSchedulerStatus()
    if (data) {
      setSchedulerStatus(data)
    }
  }

  // 初始化
  useState(() => {
    fetchWatchList()
    fetchSchedulerStatus()

    // 定期刷新状态（每30秒）
    const interval = setInterval(() => {
      fetchSchedulerStatus()
    }, 30000)

    return () => clearInterval(interval)
  }, [fetchWatchList])

  const handleAdd = async () => {
    if (!newModel.trim()) return

    try {
      const data = await addWatchList(newModel.trim())
      alert(data.message)
      setNewModel('')
      await fetchWatchList()
    } catch (err) {
      alert(`添加失败: ${err.message || err}`)
    }
  }

  const handleRemove = async (model) => {
    try {
      const data = await removeWatchList(model)
      alert(data.message)
      await fetchWatchList()
    } catch (err) {
      alert(`移除失败: {err.message || err}`)
    }
  }

  const handleRecordNow = async () => {
    try {
      await recordNow()
      await fetchWatchList()
      alert("价格记录完成")
      // 更新调度器状态
      await fetchSchedulerStatus()
    } catch (err) {
      alert(`记录失败: ${err.message || err}`)
    }
  }

  const handleAddDemoData = async () => {
    // 添加一些示例数据
    demo_models = ["STM32F103C8T6", "ESP32-WROOM-32", "LM7805", "ATmega328P", "RTL8211"]
    for model in demo_models:
      await addWatchList(model)
    alert(f"已添加 {len(demo_models)} 个示例物料")
    await fetchWatchList()
  }

  return (
    <div className="space-y-6">
      {/* 头部统计 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <p className="text-sm text-gray-500 mb-1">监控数量</p>
          <p className="text-2xl font-bold">{watchList.length}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500 mb-1">调度器状态</p>
          <p className={`text-lg font-medium ${schedulerStatus.running ? 'text-green-600' : 'text-gray-500'}`}>
            {schedulerStatus.running ? '🟢 运行中' : '⏸ 已停止'}
          </p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500 mb-1">DigiKey API</p>
          <p className={`text-lg font-medium ${schedulerStatus.digikey_configured ? 'text-green-600' : 'text-orange-500'}`}>
            {schedulerStatus.digikey_configured ? '✅ 已配置' : '⚠️ 未配置'}
          </p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500 mb-1">下次运行</p>
          <p className="text-sm">
            {schedulerStatus.next_run || '未启动'}
          </p>
        </div>
      </div>

      {/* 快捷操作 */}
      <div className="flex flex-wrap gap-2">
        <button onClick={handleRecordNow} className="btn btn-primary" disabled={!schedulerStatus.digikey_configured}>
          <RefreshCw className="w-4 h-4 mr-2" />
          立即记录
        </button>
        <button onClick={handleAddDemoData} className="btn btn-secondary">
          <Plus className="w-4 h-4 mr-2" />
          添加示例数据
        </button>
        <button onClick={() => { schedulerStatus.running ? stopScheduler() : startScheduler() }} className="btn btn-ghost">
          {schedulerStatus.running ? <Pause className="w-4 h-4 mr-2" /> : <Play className="w-4 h-4 mr-2" />}
          {schedulerStatus.running ? '暂停调度' : '启动调度'}
        </button>
      </div>

      {/* 添加监控 */}
      <div className="card">
        <h3 className="text-base font-semibold text-gray-900 mb-4">📊 添加价格监控</h3>

        <div className="flex gap-2">
          <input
            type="text"
            value={newModel}
            onChange={(e) => setNewModel(e.target.value)}
            placeholder="输入物料型号，如: STM32F103C8T6"
            className="input-field flex-1"
          />
          <button onClick={handleAdd} className="btn btn-primary">
            <Plus className="w-4 h-4 mr-2" />
            添加
          </button>
        </div>

        <div className="mt-4">
          <p className="text-sm text-gray-500 mb-2">当前监控列表:</p>

          {watchList.length === 0 ? (
            <p className="text-sm text-gray-400 italic">
              暂️ 监控列表为空，添加物料后即可开始追踪价格历史
            </p>
          ) : (
            <div className="space-y-2">
              {watchList.map((model, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="font-medium text-gray-900">{model}</span>
                  <button
                    onClick={() => handleRemove(model)}
                    className="text-red-600 hover:text-red-700"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

      {/* 使用说明 */}
      <div className="card">
        <h3 className="text-base font-semibold text-gray-900 mb-4">📖 使用说明</h3>

        <div className="space-y-3 text-sm text-gray-600">
          <div>
            <strong>配置 DigiKey API：</strong>
            <ol className="mt-2 space-y-1 pl-4 list-decimal">
              <li>访问 https://developer.digikey.com/ 注册开发者账号</li>
              <li>创建 API Key 后，配置环境变量</li>
              <li>免费额度：500次/天（个人项目够用）</li>
            </ol>
          </div>

          <div>
            <strong>工作原理：</strong>
            <ol className="mt-2 space-y-1 pl-4 list-decimal">
              <li>添加物料到监控列表</li>
              <li>启动调度器后，每天自动记录价格</li>
              <li>积累数据后，查看价格趋势图</li>
            </ol>
          </div>

          <div>
            <strong>数据积累：</strong>
            <p className="mt-2">
              <span className="text-gray-500">现在开始记录，3-6 个月后就会有完整的价格历史趋势。</span>
            </p>
          </div>

          <div>
            <strong>⚠️ 注意：</strong>
            <p className="mt-2">
              <span className="text-gray-500">每日定时记录依赖后端服务运行。如需长期运行，建议使用 Docker 或 systemd 配置为系统服务。</span>
            </p>
          </div>
        </div>
      </div>

      {/* 快捷键提示 */}
      <div className="card bg-blue-50">
        <h4 className="text-base font-medium text-blue-900 mb-2">💡 小贴士</h4>
        <ul className="text-sm text-blue-800 space-y-1 pl-4">
          <li>DigiKey 价格是美元价格，前端会自动按 7.25 汇率转换为人民币</li>
          <li>建议同时监控国产替代型号，对比国产vs进口价格</li>
          <li>先添加几个常用型号，观察几天后再扩展</li>
        </ul>
      </div>
    </div>
  )
}

async function startScheduler() {
  const { data: startData, execute: startScheduler } = useApi(api.startScheduler)
  try {
    await startScheduler()
    alert(data.message)
    # 刷新状态
    const status = await getSchedulerStatus()
    setSchedulerStatus(status)
  } catch (err) {
    alert(`启动失败: ${err.message || err}`)
  }
}

async function stopScheduler() {
  const { data: stopData, execute: stopScheduler } = useApi(api.stopScheduler)
  try {
    await stopScheduler()
    alert(stopData.message)
    const status = await getSchedulerStatus()
    setSchedulerStatus(status)
  } catch (err) {
    alert(`停止失败: {err.message || err}`)
  }
}