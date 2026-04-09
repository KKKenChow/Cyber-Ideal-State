import { useState, useEffect } from 'react'
import { Crown, Shield, Wrench, Users, MessageSquare, TrendingUp, ArrowRight, Zap, Sparkles } from 'lucide-react'
import { api } from '../lib/api'

export default function Dashboard({ onNavigate }: { onNavigate?: (path: string) => void }) {
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
    const interval = setInterval(loadStats, 30000)
    return () => clearInterval(interval)
  }, [])

  const loadStats = async () => {
    try {
      const response = await api.get('/api/stats')
      setStats(response.data)
    } catch (error) {
      console.error('Failed to load stats:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex items-end justify-between">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="w-5 h-5 text-brand-400" />
            <span className="text-brand-400 text-sm font-medium">仪表盘</span>
          </div>
          <h2 className="text-3xl font-bold text-white text-shadow">欢迎来到赛博理想国</h2>
          <p className="text-slate-400 mt-1">管理和监控你的数字生命系统</p>
        </div>
        <button
          onClick={() => onNavigate?.('/roles')}
          className="btn-primary flex items-center gap-2"
        >
          <Zap className="w-4 h-4" />
          快速开始
        </button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {loading ? (
          <div className="col-span-full flex items-center justify-center py-20">
            <div className="flex items-center gap-3 text-slate-400">
              <div className="w-5 h-5 border-2 border-brand-500/30 border-t-brand-500 rounded-full animate-spin" />
              <span>加载统计数据...</span>
            </div>
          </div>
        ) : (
          <>
            {/* Roles Stats Card */}
            <div className="glass-card p-6 stat-glow-purple animate-fade-in-up" style={{ animationDelay: '0ms' }}>
              <div className="flex items-center justify-between mb-5">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-brand-500/15 flex items-center justify-center">
                    <Users className="w-5 h-5 text-brand-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-white">角色统计</h3>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <div className="text-3xl font-bold text-white tabular-nums">{stats?.roles.total || 0}</div>
                  <div className="text-xs text-slate-500 mt-1 font-medium">总角色</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-emerald-400 tabular-nums">{stats?.roles.active || 0}</div>
                  <div className="text-xs text-slate-500 mt-1 font-medium">活跃角色</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-brand-300 tabular-nums">
                    {stats?.roles.total && stats?.roles.active 
                      ? Math.round((stats.roles.active / stats.roles.total) * 100) 
                      : 0}%
                  </div>
                  <div className="text-xs text-slate-500 mt-1 font-medium">活跃率</div>
                </div>
              </div>

              {/* By Tier */}
              {stats?.roles.by_tier && (
                <div className="mt-5 pt-5 border-t border-white/[0.06]">
                  <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">按等级分布</h4>
                  <div className="space-y-3">
                    <div className="flex items-center gap-3">
                      <div className="w-7 h-7 rounded-lg bg-amber-500/10 flex items-center justify-center">
                        <Crown className="w-3.5 h-3.5 text-amber-400" />
                      </div>
                      <span className="text-slate-400 text-sm flex-1">统治者</span>
                      <span className="text-white font-semibold tabular-nums text-sm">
                        {stats.roles.by_tier.philosopher || 0}
                      </span>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="w-7 h-7 rounded-lg bg-blue-500/10 flex items-center justify-center">
                        <Shield className="w-3.5 h-3.5 text-blue-400" />
                      </div>
                      <span className="text-slate-400 text-sm flex-1">护卫者</span>
                      <span className="text-white font-semibold tabular-nums text-sm">
                        {stats.roles.by_tier.guardian || 0}
                      </span>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="w-7 h-7 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                        <Wrench className="w-3.5 h-3.5 text-emerald-400" />
                      </div>
                      <span className="text-slate-400 text-sm flex-1">劳动者</span>
                      <span className="text-white font-semibold tabular-nums text-sm">
                        {stats.roles.by_tier.worker || 0}
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Sessions Stats Card */}
            <div className="glass-card p-6 stat-glow-blue animate-fade-in-up" style={{ animationDelay: '100ms' }}>
              <div className="flex items-center justify-between mb-5">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-blue-500/15 flex items-center justify-center">
                    <MessageSquare className="w-5 h-5 text-blue-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-white">会话统计</h3>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <div className="text-3xl font-bold text-white tabular-nums">{stats?.sessions.total || 0}</div>
                  <div className="text-xs text-slate-500 mt-1 font-medium">总会话</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-emerald-400 tabular-nums">{stats?.sessions.active || 0}</div>
                  <div className="text-xs text-slate-500 mt-1 font-medium">活跃会话</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-blue-300 tabular-nums">{stats?.sessions.today || 0}</div>
                  <div className="text-xs text-slate-500 mt-1 font-medium">今日会话</div>
                </div>
              </div>

              {/* Session Activity Bar */}
              <div className="mt-5 pt-5 border-t border-white/[0.06]">
                <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">会话活跃度</h4>
                <div className="flex items-center gap-3">
                  <div className="flex-1 h-2 rounded-full bg-white/[0.06] overflow-hidden">
                    <div 
                      className="h-full rounded-full bg-gradient-to-r from-blue-500 to-blue-400 transition-all duration-1000"
                      style={{ 
                        width: `${stats?.sessions.total > 0 
                          ? (stats.sessions.active / stats.sessions.total) * 100 
                          : 0}%` 
                      }}
                    />
                  </div>
                  <span className="text-xs text-slate-400 tabular-nums font-medium min-w-[36px] text-right">
                    {stats?.sessions.total > 0 
                      ? `${Math.round((stats.sessions.active / stats.sessions.total) * 100)}%`
                      : '0%'}
                  </span>
                </div>
              </div>
            </div>

            {/* Quick Actions Card */}
            <div className="glass-card p-6 stat-glow-amber animate-fade-in-up" style={{ animationDelay: '200ms' }}>
              <div className="flex items-center gap-3 mb-5">
                <div className="w-10 h-10 rounded-xl bg-amber-500/15 flex items-center justify-center">
                  <TrendingUp className="w-5 h-5 text-amber-400" />
                </div>
                <h3 className="text-lg font-semibold text-white">快速开始</h3>
              </div>

              <div className="space-y-3">
                <QuickAction
                  icon={<Crown className="w-4 h-4 text-amber-400" />}
                  title="创建第一个数字生命"
                  description="从聊天记录生成你的第一个 AI 角色"
                  onClick={() => onNavigate?.('/roles')}
                  color="amber"
                />
                <QuickAction
                  icon={<MessageSquare className="w-4 h-4 text-blue-400" />}
                  title="开始三等级会话"
                  description="创建统治者、护卫者、劳动者协作对话"
                  onClick={() => onNavigate?.('/sessions')}
                  color="blue"
                />
                <QuickAction
                  icon={<Users className="w-4 h-4 text-brand-400" />}
                  title="体验多角色决策"
                  description="让多个角色一起讨论并投票决策"
                  onClick={() => onNavigate?.('/sessions')}
                  color="purple"
                />
              </div>
            </div>
          </>
        )}
      </div>

      {/* Ideal State Info */}
      {!loading && stats?.roles.by_tier && (
        <div className={`rounded-2xl p-6 border transition-all duration-500 animate-fade-in-up ${
          stats.roles.by_tier.philosopher > 0 && 
          stats.roles.by_tier.guardian > 0 && 
          stats.roles.by_tier.worker > 0
            ? 'bg-gradient-to-r from-brand-500/10 via-purple-500/10 to-blue-500/10 border-brand-500/20 stat-glow-purple'
            : 'glass-card'
        }`}>
          <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
            🏛️ 理想国状态
          </h3>
          
          {stats.roles.by_tier.philosopher > 0 && 
           stats.roles.by_tier.guardian > 0 && 
           stats.roles.by_tier.worker > 0 ? (
            <div>
              <p className="text-emerald-300 mb-3 flex items-center gap-2">
                <Sparkles className="w-4 h-4" />
                恭喜！你已经拥有统治者、护卫者、劳动者三个等级的角色！
              </p>
              <p className="text-slate-400 text-sm mb-5">
                创建会话时同时选择这三个角色，系统将自动启用理想国协作模式。
              </p>
              <button
                onClick={() => onNavigate?.('/sessions')}
                className="btn-primary flex items-center gap-2"
              >
                创建理想国会话
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div>
              <p className="text-slate-400 mb-4">
                要启用理想国模式，你需要创建以下三种等级的角色：
              </p>
              <div className="grid grid-cols-3 gap-4">
                {[
                  { tier: 'philosopher', label: '统治者', count: stats.roles.by_tier.philosopher, icon: <Crown className="w-5 h-5" />, color: 'amber' },
                  { tier: 'guardian', label: '护卫者', count: stats.roles.by_tier.guardian, icon: <Shield className="w-5 h-5" />, color: 'blue' },
                  { tier: 'worker', label: '劳动者', count: stats.roles.by_tier.worker, icon: <Wrench className="w-5 h-5" />, color: 'emerald' },
                ].map((item) => (
                  <div 
                    key={item.tier}
                    className={`rounded-xl p-4 border transition-all ${
                      item.count > 0 
                        ? `bg-${item.color}-500/10 border-${item.color}-500/20` 
                        : 'bg-white/[0.02] border-white/[0.06]'
                    }`}
                  >
                    <div className={`flex items-center gap-2 mb-2 ${
                      item.count > 0 ? `text-${item.color}-400` : 'text-slate-500'
                    }`}>
                      {item.count > 0 ? '✅' : '⬜'}
                      {item.icon}
                    </div>
                    <div className="text-white font-medium text-sm">{item.label}</div>
                    <div className="text-slate-500 text-xs mt-0.5">已创建 {item.count} 个</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Getting Started Guide */}
      {!loading && stats?.roles.total === 0 && (
        <div className="glass-card p-8 border-blue-500/20 stat-glow-blue animate-fade-in-up">
          <h3 className="text-xl font-semibold text-blue-300 mb-6 flex items-center gap-2">
            👋 新手指南
          </h3>
          <div className="space-y-5">
            {[
              { step: 1, title: '创建数字生命', desc: '从聊天记录、文档、照片中提取人格和记忆，生成独立的 AI 角色' },
              { step: 2, title: '创建会话', desc: '选择一个或多个角色，配置发言模式，开始对话' },
              { step: 3, title: '体验协作', desc: '尝试不同的发言模式（自由讨论、辩论、投票、共识）' },
            ].map((item) => (
              <div key={item.step} className="flex items-start gap-4">
                <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center text-blue-300 text-sm font-bold">
                  {item.step}
                </div>
                <div>
                  <div className="text-white font-medium mb-1">{item.title}</div>
                  <p className="text-slate-400 text-sm">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
          
          <button
            onClick={() => onNavigate?.('/roles')}
            className="mt-6 btn-primary"
          >
            开始创建角色
          </button>
        </div>
      )}
    </div>
  )
}

function QuickAction({ 
  icon, 
  title, 
  description, 
  onClick, 
  color 
}: { 
  icon: React.ReactNode
  title: string
  description: string
  onClick: () => void
  color: 'amber' | 'blue' | 'purple'
}) {
  const colorMap = {
    amber: 'hover:bg-amber-500/10 border-amber-500/15 hover:border-amber-500/30',
    blue: 'hover:bg-blue-500/10 border-blue-500/15 hover:border-blue-500/30',
    purple: 'hover:bg-brand-500/10 border-brand-500/15 hover:border-brand-500/30',
  }

  return (
    <button
      onClick={onClick}
      className={`w-full text-left px-4 py-3 rounded-xl border border-white/[0.06] transition-all duration-200 group ${colorMap[color]}`}
    >
      <div className="flex items-center gap-2.5 mb-1">
        {icon}
        <span className="text-white font-medium text-sm">{title}</span>
        <ArrowRight className="w-3.5 h-3.5 ml-auto text-slate-600 group-hover:text-slate-400 group-hover:translate-x-0.5 transition-all" />
      </div>
      <p className="text-slate-500 text-xs pl-7">{description}</p>
    </button>
  )
}
