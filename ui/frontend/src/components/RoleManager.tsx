import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Crown, Shield, Wrench, Plus, RefreshCw, Trash2, Edit, Play, Users, Filter } from 'lucide-react'
import { api } from '../lib/api'
import CreateRoleModal from './CreateRoleModal'

type Role = {
  id: string
  name: string
  type: string
  tier: string
  description?: string
  created_at: string
  updated_at: string
  active: boolean
  persona?: {
    tags?: string[]
    mbti?: string
  }
}

export default function RoleManager({ onRoleUpdate }: { onRoleUpdate?: () => void }) {
  const navigate = useNavigate()
  const [roles, setRoles] = useState<Role[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [filter, setFilter] = useState({ tier: '', type: '', active: '' })

  useEffect(() => {
    loadRoles()
  }, [filter])

  const loadRoles = async () => {
    try {
      setLoading(true)
      const response = await api.get('/api/roles', {
        params: filter
      })
      setRoles(response.data.roles)
    } catch (error) {
      console.error('Failed to load roles:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateRole = async (data: any) => {
    try {
      await api.post('/api/roles', data)
      setShowCreateModal(false)
      loadRoles()
      onRoleUpdate?.()
    } catch (error) {
      console.error('Failed to create role:', error)
      alert('创建角色失败')
    }
  }

  const handleDeleteRole = async (roleId: string) => {
    if (!confirm('确定要删除这个角色吗？')) return
    
    try {
      await api.delete(`/api/roles/${roleId}`)
      loadRoles()
      onRoleUpdate?.()
    } catch (error) {
      console.error('Failed to delete role:', error)
      alert('删除角色失败')
    }
  }

  const getTierIcon = (tier: string) => {
    switch (tier) {
      case 'philosopher':
        return <Crown className="w-5 h-5 text-amber-400" />
      case 'guardian':
        return <Shield className="w-5 h-5 text-blue-400" />
      case 'worker':
        return <Wrench className="w-5 h-5 text-emerald-400" />
      default:
        return null
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

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      'ex-partner': '初恋',
      'colleague': '同事',
      'family': '家人',
      'friend': '朋友'
    }
    return labels[type] || type
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-end justify-between">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Users className="w-5 h-5 text-amber-400" />
            <span className="text-amber-400 text-sm font-medium">角色管理</span>
          </div>
          <h2 className="text-3xl font-bold text-white text-shadow">管理你的数字生命</h2>
          <p className="text-slate-400 mt-1">创建和管理 AI 角色，赋予他们独特的性格与记忆</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          创建角色
        </button>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3">
        <div className="relative">
          <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <select
            value={filter.tier}
            onChange={(e) => setFilter({ ...filter, tier: e.target.value })}
            className="input-field pl-9 pr-8 appearance-none cursor-pointer min-w-[130px]"
          >
            <option value="">所有等级</option>
            <option value="philosopher">统治者</option>
            <option value="guardian">护卫者</option>
            <option value="worker">劳动者</option>
          </select>
        </div>

        <select
          value={filter.type}
          onChange={(e) => setFilter({ ...filter, type: e.target.value })}
          className="input-field appearance-none cursor-pointer min-w-[120px]"
        >
          <option value="">所有类型</option>
          <option value="ex-partner">初恋</option>
          <option value="colleague">同事</option>
          <option value="family">家人</option>
          <option value="friend">朋友</option>
        </select>

        <div className="flex-1" />

        <button
          onClick={loadRoles}
          className="btn-ghost flex items-center gap-2 text-sm"
          title="刷新"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Roles Grid */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="flex items-center gap-3 text-slate-400">
            <div className="w-5 h-5 border-2 border-brand-500/30 border-t-brand-500 rounded-full animate-spin" />
            <span>加载角色列表...</span>
          </div>
        </div>
      ) : roles.length === 0 ? (
        <div className="glass-card p-16 text-center">
          <div className="text-6xl mb-4">🎭</div>
          <p className="text-xl text-white font-medium mb-2">还没有角色</p>
          <p className="text-slate-400 text-sm mb-6">点击"创建角色"开始创建你的第一个数字生命</p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn-primary inline-flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            创建角色
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {roles.map((role, index) => (
            <div
              key={role.id}
              className="glass-card-hover p-6 animate-fade-in-up"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={`w-11 h-11 rounded-xl flex items-center justify-center ${
                    role.tier === 'philosopher' ? 'bg-amber-500/15' :
                    role.tier === 'guardian' ? 'bg-blue-500/15' :
                    'bg-emerald-500/15'
                  }`}>
                    {getTierIcon(role.tier)}
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-white">{role.name}</h3>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="text-slate-500 text-xs">{getTypeLabel(role.type)}</span>
                      <span className="text-slate-600">·</span>
                      <span className={`badge ${
                        role.tier === 'philosopher' ? 'badge-philosopher' :
                        role.tier === 'guardian' ? 'badge-guardian' :
                        'badge-worker'
                      }`}>
                        {getTierLabel(role.tier)}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="flex gap-1">
                  <button 
                    className="btn-ghost" 
                    title="开始对话"
                    onClick={() => navigate('/sessions')}
                  >
                    <Play className="w-4 h-4 text-emerald-400" />
                  </button>
                  <button className="btn-ghost" title="编辑角色" disabled>
                    <Edit className="w-4 h-4 text-blue-400/40" />
                  </button>
                  <button
                    onClick={() => handleDeleteRole(role.id)}
                    className="btn-ghost"
                    title="删除角色"
                  >
                    <Trash2 className="w-4 h-4 text-red-400" />
                  </button>
                </div>
              </div>

              {role.description && (
                <p className="text-slate-400 text-sm mb-3 line-clamp-2">{role.description}</p>
              )}

              <div className="space-y-2.5">
                {role.persona?.mbti && (
                  <div className="flex items-center gap-2">
                    <span className="text-slate-500 text-xs font-medium w-12">MBTI</span>
                    <span className="bg-brand-500/15 text-brand-300 px-2.5 py-0.5 rounded-md text-xs font-semibold">{role.persona.mbti}</span>
                  </div>
                )}
                {role.persona?.tags && role.persona.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mt-2">
                    {role.persona.tags.map((tag, idx) => (
                      <span
                        key={idx}
                        className="bg-white/[0.04] text-slate-400 px-2.5 py-1 rounded-lg text-xs border border-white/[0.04]"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              <div className="mt-4 pt-4 border-t border-white/[0.06] text-xs text-slate-600 flex items-center gap-1.5">
                <span>创建于 {new Date(role.created_at).toLocaleDateString('zh-CN')}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Role Modal */}
      {showCreateModal && (
        <CreateRoleModal
          onClose={() => setShowCreateModal(false)}
          onCreate={handleCreateRole}
        />
      )}
    </div>
  )
}


