import { useState } from 'react'
import { X, Crown, Shield, Wrench, Plus, Trash2 } from 'lucide-react'

interface CreateRoleModalProps {
  onClose: () => void
  onCreate: (data: any) => void
}

export default function CreateRoleModal({ onClose, onCreate }: CreateRoleModalProps) {
  interface DataSource {
    type: string;
    path: string;
  }
  
  const [formData, setFormData] = useState({
    name: '',
    type: 'friend',
    tier: 'worker',
    description: '',
    manual_description: '',
    sources: [] as DataSource[]
  })

  const [currentSource, setCurrentSource] = useState<DataSource>({
    type: 'manual',
    path: ''
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onCreate(formData)
  }

  const addSource = () => {
    setFormData({
      ...formData,
      sources: [...formData.sources, currentSource]
    })
    setCurrentSource({ type: 'manual', path: '' })
  }

  const removeSource = (index: number) => {
    setFormData({
      ...formData,
      sources: formData.sources.filter((_, i) => i !== index)
    })
  }

  const tierOptions = [
    { value: 'worker', label: '劳动者', icon: <Wrench className="w-4 h-4 text-emerald-400" />, desc: '生产、创造、服务', color: 'emerald' },
    { value: 'guardian', label: '护卫者', icon: <Shield className="w-4 h-4 text-blue-400" />, desc: '执行、保护、协调', color: 'blue' },
    { value: 'philosopher', label: '统治者', icon: <Crown className="w-4 h-4 text-amber-400" />, desc: '战略思考、价值判断', color: 'amber' },
  ]

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 animate-fade-in">
      <div className="bg-slate-900 rounded-2xl p-0 max-w-2xl w-full max-h-[90vh] overflow-hidden border border-white/[0.08] shadow-2xl animate-scale-in">
        {/* Header */}
        <div className="flex items-center justify-between px-8 py-6 border-b border-white/[0.06]">
          <div>
            <h2 className="text-xl font-bold text-white">创建新角色</h2>
            <p className="text-slate-400 text-sm mt-1">定义一个数字生命的身份与性格</p>
          </div>
          <button
            onClick={onClose}
            className="btn-ghost rounded-xl"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="overflow-auto max-h-[calc(90vh-140px)]">
          <div className="p-8 space-y-6">
            {/* Basic Info */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                角色名称 <span className="text-red-400">*</span>
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="input-field w-full"
                placeholder="例如：技术导师、初恋、家人..."
                required
              />
            </div>

            {/* Type */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                关系类型
              </label>
              <select
                value={formData.type}
                onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                className="input-field w-full appearance-none cursor-pointer"
              >
                <option value="friend">朋友</option>
                <option value="colleague">同事</option>
                <option value="family">家人</option>
                <option value="ex-partner">初恋</option>
              </select>
            </div>

            {/* Tier Selection */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-3">
                等级
              </label>
              <div className="grid grid-cols-3 gap-3">
                {tierOptions.map((opt) => (
                  <button
                    key={opt.value}
                    type="button"
                    onClick={() => setFormData({ ...formData, tier: opt.value })}
                    className={`p-4 rounded-xl border-2 transition-all duration-200 text-center ${
                      formData.tier === opt.value
                        ? `bg-${opt.color}-500/10 border-${opt.color}-500/40`
                        : 'bg-white/[0.02] border-white/[0.06] hover:border-white/[0.12]'
                    }`}
                  >
                    <div className="flex justify-center mb-2">{opt.icon}</div>
                    <div className="text-white font-medium text-sm">{opt.label}</div>
                    <div className="text-slate-500 text-[11px] mt-0.5">{opt.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                描述
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="input-field w-full min-h-[100px] resize-none"
                placeholder="简要描述这个角色..."
              />
            </div>

            {/* Data Sources */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                数据来源
              </label>
              <div className="space-y-3">
                <div className="flex gap-2">
                  <select
                    value={currentSource.type}
                    onChange={(e) => setCurrentSource({ ...currentSource, type: e.target.value })}
                    className="input-field appearance-none cursor-pointer flex-1"
                  >
                    <option value="manual">手动描述</option>
                    <option value="wechat">微信聊天记录</option>
                    <option value="qq">QQ聊天记录</option>
                    <option value="feishu">飞书</option>
                    <option value="email">邮件</option>
                    <option value="photo">照片</option>
                  </select>
                  {currentSource.type === 'manual' ? (
                    <input
                      type="text"
                      value={currentSource.path}
                      onChange={(e) => setCurrentSource({ ...currentSource, path: e.target.value })}
                      className="input-field flex-[2]"
                      placeholder="输入关于此人的描述..."
                    />
                  ) : (
                    <input
                      type="text"
                      value={currentSource.path}
                      onChange={(e) => setCurrentSource({ ...currentSource, path: e.target.value })}
                      className="input-field flex-[2]"
                      placeholder="文件路径或URL"
                    />
                  )}
                  <button
                    type="button"
                    onClick={addSource}
                    className="btn-primary px-4 py-2.5 rounded-xl flex items-center gap-1.5"
                  >
                    <Plus className="w-4 h-4" />
                    添加
                  </button>
                </div>

                {formData.sources.map((source, index) => (
                  <div key={index} className="flex items-center gap-2 bg-white/[0.03] px-4 py-2.5 rounded-xl border border-white/[0.04]">
                    <span className="text-slate-300 text-sm font-medium">{source.type}</span>
                    {source.path && <span className="text-slate-500 text-xs">{source.path}</span>}
                    <button
                      type="button"
                      onClick={() => removeSource(index)}
                      className="ml-auto btn-ghost p-1 rounded-lg"
                    >
                      <Trash2 className="w-3.5 h-3.5 text-red-400/60" />
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* Manual Description */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                手动描述
              </label>
              <textarea
                value={formData.manual_description}
                onChange={(e) => setFormData({ ...formData, manual_description: e.target.value })}
                className="input-field w-full min-h-[150px] resize-none"
                placeholder="用你自己的话描述这个人的性格、习惯、你们的关系..."
              />
            </div>
          </div>

          {/* Footer */}
          <div className="flex gap-3 px-8 py-6 border-t border-white/[0.06] bg-slate-900/50">
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary flex-1 py-3"
            >
              取消
            </button>
            <button
              type="submit"
              className="btn-primary flex-1 py-3"
            >
              创建角色
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
