import { useState, useEffect } from 'react'
import { Plus, Play, Trash2, MessageSquare, Clock, Users, CheckCircle, X, PauseCircle, PlayCircle } from 'lucide-react'
import { api } from '../lib/api'
import CreateSessionModal from './CreateSessionModal'
import ChatPanel from './ChatPanel'

type Session = {
  id: string
  name: string
  participants: Array<{
    role_id: string
    role_name: string
    tier: string
  }>
  speaking_mode: string
  decision_mode: string
  created_at: string
  updated_at: string
  active: boolean
  messages?: Array<any>
}

export default function SessionManager({ availableRoles }: { availableRoles: any[] }) {
  const [sessions, setSessions] = useState<Session[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [activeSession, setActiveSession] = useState<Session | null>(null)
  const [viewingChat, setViewingChat] = useState(false)

  useEffect(() => {
    loadSessions()
  }, [])

  const loadSessions = async () => {
    try {
      setLoading(true)
      const response = await api.get('/api/sessions')
      setSessions(response.data.sessions || [])
    } catch (error) {
      console.error('Failed to load sessions:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateSession = async (data: any) => {
    try {
      await api.post('/api/sessions', data)
      setShowCreateModal(false)
      loadSessions()
    } catch (error) {
      console.error('Failed to create session:', error)
      alert('创建会话失败')
    }
  }

  const handleDeleteSession = async (sessionId: string) => {
    if (!confirm('确定要删除这个会话吗？')) return
    
    try {
      await api.delete(`/api/sessions/${sessionId}`)
      loadSessions()
    } catch (error) {
      console.error('Failed to delete session:', error)
      alert('删除会话失败')
    }
  }

  const handleToggleActive = async (sessionId: string, currentActive: boolean) => {
    try {
      await api.put(`/api/sessions/${sessionId}/active`, { active: !currentActive })
      loadSessions()
    } catch (error) {
      console.error('Failed to toggle session active:', error)
      alert('操作失败')
    }
  }

  const handleEnterChat = (session: Session) => {
    setActiveSession(session)
    setViewingChat(true)
  }

  const handleExitChat = () => {
    setActiveSession(null)
    setViewingChat(false)
  }

  const getSpeakingModeLabel = (mode: string) => {
    const labels: Record<string, string> = {
      'free': '自由讨论',
      'turn_based': '轮流发言',
      'debate': '辩论',
      'vote': '投票',
      'consensus': '共识'
    }
    return labels[mode] || mode
  }

  const getSpeakingModeColor = (mode: string) => {
    const colors: Record<string, string> = {
      'free': 'text-emerald-400 bg-emerald-500/15',
      'turn_based': 'text-blue-400 bg-blue-500/15',
      'debate': 'text-amber-400 bg-amber-500/15',
      'vote': 'text-brand-400 bg-brand-500/15',
      'consensus': 'text-pink-400 bg-pink-500/15',
    }
    return colors[mode] || 'text-slate-400 bg-slate-500/15'
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

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'philosopher': return 'bg-amber-500/15 border-amber-500/20 text-amber-300'
      case 'guardian': return 'bg-blue-500/15 border-blue-500/20 text-blue-300'
      case 'worker': return 'bg-emerald-500/15 border-emerald-500/20 text-emerald-300'
      default: return 'bg-slate-500/15 border-slate-500/20 text-slate-300'
    }
  }

  // Chat view
  if (viewingChat && activeSession) {
    return (
      <div className="h-[calc(100vh-80px)] flex flex-col -m-10 animate-fade-in">
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/[0.06] bg-slate-950/60 backdrop-blur-2xl">
          <div className="flex items-center gap-4">
            <button
              onClick={handleExitChat}
              className="btn-ghost rounded-xl"
            >
              <X className="w-5 h-5" />
            </button>
            <div>
              <h3 className="text-lg font-semibold text-white">{activeSession.name}</h3>
              <div className="flex items-center gap-2 mt-0.5">
                {activeSession.participants.map(p => (
                  <span key={p.role_id} className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-medium border ${getTierColor(p.tier)}`}>
                    <span className="text-xs">{getTierIcon(p.tier)}</span>
                    {p.role_name}
                  </span>
                ))}
              </div>
            </div>
          </div>
          <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium ${getSpeakingModeColor(activeSession.speaking_mode)}`}>
            <MessageSquare className="w-3.5 h-3.5" />
            <span>{getSpeakingModeLabel(activeSession.speaking_mode)}</span>
          </div>
        </div>
        
        <ChatPanel 
          sessionId={activeSession.id}
          participants={activeSession.participants}
          onMessageSent={loadSessions}
        />
      </div>
    )
  }

  // Session list view
  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-end justify-between">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <MessageSquare className="w-5 h-5 text-blue-400" />
            <span className="text-blue-400 text-sm font-medium">会话管理</span>
          </div>
          <h2 className="text-3xl font-bold text-white text-shadow">管理你的对话会话</h2>
          <p className="text-slate-400 mt-1">自由组合角色，体验多角色协作对话</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          创建会话
        </button>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="glass-card p-5 stat-glow-purple">
          <div className="flex items-center gap-2.5 mb-3">
            <div className="w-8 h-8 rounded-lg bg-brand-500/15 flex items-center justify-center">
              <Users className="w-4 h-4 text-brand-400" />
            </div>
            <span className="text-slate-400 text-sm">总会话</span>
          </div>
          <div className="text-3xl font-bold text-white tabular-nums">{sessions.length}</div>
        </div>
        <div className="glass-card p-5 stat-glow-blue">
          <div className="flex items-center gap-2.5 mb-3">
            <div className="w-8 h-8 rounded-lg bg-blue-500/15 flex items-center justify-center">
              <MessageSquare className="w-4 h-4 text-blue-400" />
            </div>
            <span className="text-slate-400 text-sm">活跃会话</span>
          </div>
          <div className="text-3xl font-bold text-white tabular-nums">{sessions.filter(s => s.active).length}</div>
        </div>
        <div className="glass-card p-5 stat-glow-green">
          <div className="flex items-center gap-2.5 mb-3">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/15 flex items-center justify-center">
              <Clock className="w-4 h-4 text-emerald-400" />
            </div>
            <span className="text-slate-400 text-sm">今日会话</span>
          </div>
          <div className="text-3xl font-bold text-white tabular-nums">
            {sessions.filter(s => {
              const date = new Date(s.created_at)
              const today = new Date()
              return date.toDateString() === today.toDateString()
            }).length}
          </div>
        </div>
      </div>

      {/* Session List */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="flex items-center gap-3 text-slate-400">
            <div className="w-5 h-5 border-2 border-brand-500/30 border-t-brand-500 rounded-full animate-spin" />
            <span>加载会话列表...</span>
          </div>
        </div>
      ) : sessions.length === 0 ? (
        <div className="glass-card p-16 text-center">
          <div className="text-6xl mb-4">💬</div>
          <p className="text-xl text-white font-medium mb-2">还没有会话</p>
          <p className="text-slate-400 text-sm mb-6">点击"创建会话"开始你的第一个对话</p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn-primary inline-flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            创建会话
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {sessions.map((session, index) => {
            const tiers = new Set(session.participants.map(p => p.tier))
            const isIdealState = tiers.has('philosopher') && tiers.has('guardian') && tiers.has('worker')

            return (
              <div
                key={session.id}
                className="glass-card-hover p-6 cursor-pointer animate-fade-in-up"
                style={{ animationDelay: `${index * 50}ms` }}
                onClick={() => handleEnterChat(session)}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className={`text-lg font-semibold truncate ${session.active ? 'text-white' : 'text-slate-500'}`}>{session.name}</h3>
                      {session.active ? (
                        <span className="badge-active">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                          活跃
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[11px] font-medium bg-slate-500/15 text-slate-400">
                          已结束
                        </span>
                      )}
                    </div>
                    
                    {/* Participants */}
                    <div className="flex items-center gap-3 mb-3">
                      <div className="flex -space-x-1.5">
                        {session.participants.slice(0, 5).map((participant, pIdx) => (
                          <div
                            key={pIdx}
                            className={`w-7 h-7 rounded-lg flex items-center justify-center text-sm border-2 border-surface ${
                              participant.tier === 'philosopher' ? 'bg-amber-500/20' :
                              participant.tier === 'guardian' ? 'bg-blue-500/20' :
                              'bg-emerald-500/20'
                            }`}
                            title={participant.role_name}
                          >
                            {getTierIcon(participant.tier)}
                          </div>
                        ))}
                        {session.participants.length > 5 && (
                          <div className="w-7 h-7 rounded-lg bg-brand-500/20 flex items-center justify-center text-[10px] text-brand-300 font-medium border-2 border-surface">
                            +{session.participants.length - 5}
                          </div>
                        )}
                      </div>
                      <span className="text-slate-500 text-sm truncate">
                        {session.participants.map(p => p.role_name).slice(0, 3).join(', ')}
                        {session.participants.length > 3 && ` 等${session.participants.length}人`}
                      </span>
                    </div>

                    {/* Session Meta */}
                    <div className="flex items-center gap-4 text-xs">
                      <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg font-medium ${getSpeakingModeColor(session.speaking_mode)}`}>
                        <MessageSquare className="w-3 h-3" />
                        <span>{getSpeakingModeLabel(session.speaking_mode)}</span>
                      </div>
                      <div className="flex items-center gap-1.5 text-slate-500">
                        <Clock className="w-3 h-3" />
                        <span>{new Date(session.created_at).toLocaleDateString('zh-CN')}</span>
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-1 ml-4 flex-shrink-0">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleEnterChat(session)
                      }}
                      className="btn-ghost"
                      title="进入会话"
                    >
                      <Play className="w-4 h-4 text-emerald-400" />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleToggleActive(session.id, session.active)
                      }}
                      className="btn-ghost"
                      title={session.active ? '结束会话' : '重新激活'}
                    >
                      {session.active 
                        ? <PauseCircle className="w-4 h-4 text-amber-400" />
                        : <PlayCircle className="w-4 h-4 text-blue-400" />
                      }
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleDeleteSession(session.id)
                      }}
                      className="btn-ghost"
                      title="删除会话"
                    >
                      <Trash2 className="w-4 h-4 text-red-400" />
                    </button>
                  </div>
                </div>

                {/* Ideal State Badge */}
                {isIdealState && (
                  <div className="mt-4 pt-4 border-t border-white/[0.06]">
                    <div className="inline-flex items-center gap-2 bg-gradient-to-r from-brand-500/15 via-purple-500/15 to-blue-500/15 border border-brand-500/20 rounded-lg px-3 py-1.5">
                      <CheckCircle className="w-3.5 h-3.5 text-brand-400" />
                      <span className="text-xs font-medium text-brand-300">理想国三等级协作模式</span>
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}

      {/* Create Session Modal */}
      {showCreateModal && (
        <CreateSessionModal
          onClose={() => setShowCreateModal(false)}
          onCreate={handleCreateSession}
          roles={availableRoles}
        />
      )}
    </div>
  )
}
