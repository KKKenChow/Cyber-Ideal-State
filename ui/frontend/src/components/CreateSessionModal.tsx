import { useState } from 'react'
import { X, Plus, Users, MessageSquare, CheckCircle } from 'lucide-react'

interface CreateSessionModalProps {
  onClose: () => void
  onCreate: (data: any) => void
  roles: any[]
}

export default function CreateSessionModal({ onClose, onCreate, roles }: CreateSessionModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    speaking_mode: 'free',
    decision_mode: 'chat'
  })
  
  const [selectedRoles, setSelectedRoles] = useState<string[]>([])
  const [showTierHelp, setShowTierHelp] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (selectedRoles.length === 0) {
      alert('请至少选择一个角色')
      return
    }
    
    const participants = selectedRoles.map(roleId => {
      const role = roles.find(r => r.id === roleId)
      return {
        role_id: roleId,
        role_name: role?.name || roleId,
        tier: role?.tier || 'worker'
      }
    })
    
    onCreate({
      name: formData.name || `会话 ${new Date().toLocaleDateString()}`,
      participants,
      speaking_mode: formData.speaking_mode,
      decision_mode: formData.decision_mode
    })
  }

  const toggleRole = (roleId: string) => {
    if (selectedRoles.includes(roleId)) {
      setSelectedRoles(selectedRoles.filter(id => id !== roleId))
    } else {
      setSelectedRoles([...selectedRoles, roleId])
    }
  }

  const getTierIcon = (tier: string) => {
    switch (tier) {
      case 'philosopher':
        return '👑'
      case 'guardian':
        return '🛡️'
      case 'worker':
        return '🔧'
      default:
        return '👤'
    }
  }

  const getTierLabel = (tier: string) => {
    switch (tier) {
      case 'philosopher':
        return '统治者'
      case 'guardian':
        return '护卫者'
      case 'worker':
        return '劳动者'
      default:
        return tier
    }
  }

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'philosopher': return 'border-amber-500/30 bg-amber-500/10'
      case 'guardian': return 'border-blue-500/30 bg-blue-500/10'
      case 'worker': return 'border-emerald-500/30 bg-emerald-500/10'
      default: return 'border-slate-500/30 bg-slate-500/10'
    }
  }

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      'first-love': '初恋',
      'colleague': '同事',
      'family': '家人',
      'friend': '朋友'
    }
    return labels[type] || type
  }

  const speakingModes = [
    { value: 'free', label: '自由讨论', desc: '所有角色自由发言', icon: '💬' },
    { value: 'turn_based', label: '轮流发言', desc: '按顺序轮流回应', icon: '🔄' },
    { value: 'debate', label: '辩论', desc: '多轮辩论，总结观点', icon: '⚔️' },
    { value: 'vote', label: '投票', desc: '对问题投票决定', icon: '🗳️' },
    { value: 'consensus', label: '共识', desc: '多轮协商达成一致', icon: '🤝' }
  ]

  const isIdealState = (() => {
    const tiers = selectedRoles.map(id => roles.find(r => r.id === id)?.tier)
    const uniqueTiers = new Set(tiers)
    return uniqueTiers.size === 3 && 
           uniqueTiers.has('philosopher') && 
           uniqueTiers.has('guardian') && 
           uniqueTiers.has('worker')
  })()

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 animate-fade-in">
      <div className="bg-slate-900 rounded-2xl p-0 max-w-4xl w-full max-h-[90vh] overflow-hidden border border-white/[0.08] shadow-2xl animate-scale-in">
        {/* Header */}
        <div className="flex items-center justify-between px-8 py-6 border-b border-white/[0.06]">
          <div>
            <h2 className="text-xl font-bold text-white">创建新会话</h2>
            <p className="text-slate-400 text-sm mt-1">选择角色并配置会话模式</p>
          </div>
          <button
            onClick={onClose}
            className="btn-ghost rounded-xl"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="overflow-auto max-h-[calc(90vh-140px)]">
          <div className="p-8 space-y-7">
            {/* Session Name */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                会话名称
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="input-field w-full"
                placeholder="留空则自动生成名称"
              />
            </div>

            {/* Role Selection */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <label className="text-sm font-medium text-slate-300">
                  选择角色
                </label>
                <div className="flex items-center gap-3">
                  <button
                    type="button"
                    onClick={() => setShowTierHelp(!showTierHelp)}
                    className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-300 transition-colors"
                  >
                    <MessageSquare className="w-3.5 h-3.5" />
                    了解三等级制
                  </button>
                  <button
                    type="button"
                    onClick={() => setSelectedRoles(roles.map(r => r.id))}
                    className="text-xs text-brand-400 hover:text-brand-300 transition-colors font-medium"
                  >
                    全选
                  </button>
                </div>
              </div>

              {/* Tier Help Popup */}
              {showTierHelp && (
                <div className="mb-4 glass-card p-4 animate-scale-in">
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div className="flex items-start gap-2">
                      <span className="text-xl">👑</span>
                      <div>
                        <div className="text-white font-medium text-sm">统治者</div>
                        <div className="text-slate-500 text-xs">战略思考、价值判断、终极决策</div>
                      </div>
                    </div>
                    <div className="flex items-start gap-2">
                      <span className="text-xl">🛡️</span>
                      <div>
                        <div className="text-white font-medium text-sm">护卫者</div>
                        <div className="text-slate-500 text-xs">执行、保护、协调</div>
                      </div>
                    </div>
                    <div className="flex items-start gap-2">
                      <span className="text-xl">🔧</span>
                      <div>
                        <div className="text-white font-medium text-sm">劳动者</div>
                        <div className="text-slate-500 text-xs">生产、创造、服务</div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Role Grid */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3 max-h-60 overflow-y-auto p-1">
                {roles.map((role) => (
                  <button
                    key={role.id}
                    type="button"
                    onClick={() => toggleRole(role.id)}
                    className={`p-4 rounded-xl border-2 transition-all duration-200 text-left ${
                      selectedRoles.includes(role.id)
                        ? getTierColor(role.tier)
                        : 'bg-white/[0.02] border-white/[0.06] hover:border-white/[0.12]'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-xl">{getTierIcon(role.tier)}</span>
                        <span className="text-white font-medium text-sm">{role.name}</span>
                      </div>
                      {selectedRoles.includes(role.id) && (
                        <CheckCircle className="w-4 h-4 text-brand-400 flex-shrink-0" />
                      )}
                    </div>
                    <div className="flex items-center gap-1.5 text-[11px] text-slate-500">
                      <span>{getTypeLabel(role.type)}</span>
                      <span>·</span>
                      <span>{getTierLabel(role.tier)}</span>
                    </div>
                  </button>
                ))}
              </div>

              <p className="text-xs text-slate-500 mt-3">
                已选择 <span className="text-brand-400 font-semibold">{selectedRoles.length}</span> 个角色
              </p>
            </div>

            {/* Speaking Mode */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-3">
                发言模式
              </label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {speakingModes.map((mode) => (
                  <button
                    key={mode.value}
                    type="button"
                    onClick={() => setFormData({ ...formData, speaking_mode: mode.value })}
                    className={`p-4 rounded-xl border-2 transition-all duration-200 text-left ${
                      formData.speaking_mode === mode.value
                        ? 'bg-brand-500/10 border-brand-500/30'
                        : 'bg-white/[0.02] border-white/[0.06] hover:border-white/[0.12]'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-lg">{mode.icon}</span>
                      <span className="text-white font-medium text-sm">{mode.label}</span>
                    </div>
                    <div className="text-[11px] text-slate-500">{mode.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Ideal State Suggestion */}
            {isIdealState && (
              <div className="bg-gradient-to-r from-brand-500/10 via-purple-500/10 to-blue-500/10 border border-brand-500/20 rounded-xl p-4 animate-scale-in">
                <div className="flex items-center gap-2 text-brand-300 mb-1.5">
                  <Users className="w-4 h-4" />
                  <span className="font-medium text-sm">三等级协作模式</span>
                </div>
                <p className="text-xs text-slate-400">
                  你选择了统治者、护卫者、劳动者，系统将自动启用理想国协作模式！
                </p>
              </div>
            )}
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
              disabled={selectedRoles.length === 0}
              className="btn-primary flex-1 py-3 flex items-center justify-center gap-2"
            >
              <Plus className="w-4 h-4" />
              创建会话
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
