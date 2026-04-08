import { useState, useEffect } from 'react'
import { Routes, Route, Link, useNavigate, useLocation } from 'react-router-dom'
import { 
  Users, 
  MessageSquare, 
  LayoutDashboard,
  Crown,
  Shield,
  Wrench,
  HelpCircle,
  Activity,
  ChevronRight
} from 'lucide-react'
import Dashboard from './components/Dashboard'
import RoleManager from './components/RoleManager'
import SessionManager from './components/SessionManager'
import { api } from './lib/api'

function App() {
  const navigate = useNavigate()
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [roles, setRoles] = useState<any[]>([])

  useEffect(() => {
    loadStats()
    loadRoles()
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

  const loadRoles = async () => {
    try {
      const response = await api.get('/api/roles')
      setRoles(response.data.roles || [])
    } catch (error) {
      console.error('Failed to load roles:', error)
    }
  }

  const refreshAll = async () => {
    await Promise.all([loadStats(), loadRoles()])
  }

  const handleNavigate = (path: string) => {
    navigate(path)
  }

  return (
    <div className="w-full h-screen bg-surface bg-mesh noise-overlay relative">
      <div className="flex w-full h-full relative z-10">
        {/* Sidebar */}
        <aside className="w-[260px] flex-shrink-0 h-full flex flex-col border-r border-white/[0.06] bg-slate-950/60 backdrop-blur-2xl">
          {/* Logo */}
          <div className="px-6 pt-7 pb-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center text-xl shadow-glow-sm">
                🏛️
              </div>
              <div>
                <h1 className="text-lg font-bold text-white tracking-tight">Cyber-Ideal-State</h1>
                <p className="text-[11px] text-slate-500 font-medium tracking-wider uppercase">赛博理想国</p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-3 space-y-1">
            <p className="px-3 mb-2 text-[11px] font-semibold text-slate-500 uppercase tracking-widest">导航</p>
            <NavLink to="/" icon={<LayoutDashboard className="w-[18px] h-[18px]" />} onClick={handleNavigate}>
              仪表盘
              {stats && (
                <span className="ml-auto bg-brand-500/15 text-brand-300 px-2 py-0.5 rounded-md text-[11px] font-medium">
                  {stats.roles.active}
                </span>
              )}
            </NavLink>
            <NavLink to="/roles" icon={<Users className="w-[18px] h-[18px]" />} onClick={handleNavigate}>
              角色管理
              {stats && (
                <span className="ml-auto bg-amber-500/15 text-amber-300 px-2 py-0.5 rounded-md text-[11px] font-medium">
                  {stats.roles.total}
                </span>
              )}
            </NavLink>
            <NavLink to="/sessions" icon={<MessageSquare className="w-[18px] h-[18px]" />} onClick={handleNavigate}>
              会话管理
              {stats && (
                <span className="ml-auto bg-blue-500/15 text-blue-300 px-2 py-0.5 rounded-md text-[11px] font-medium">
                  {stats.sessions.active}
                </span>
              )}
            </NavLink>
          </nav>

          {/* System Status */}
          <div className="px-4 py-4 border-t border-white/[0.06]">
            <p className="px-2 mb-3 text-[11px] font-semibold text-slate-500 uppercase tracking-widest">系统状态</p>
            {loading ? (
              <div className="px-2 text-slate-500 text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-slate-500 animate-pulse" />
                  <span>加载中...</span>
                </div>
              </div>
            ) : stats ? (
              <div className="space-y-2.5 text-sm px-2">
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">总角色</span>
                  <span className="text-white font-semibold tabular-nums">{stats.roles.total}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">活跃会话</span>
                  <span className="text-white font-semibold tabular-nums">{stats.sessions.active}</span>
                </div>
                <div className="flex items-center gap-2 pt-1">
                  <Activity className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-emerald-400 text-xs font-medium">系统运行正常</span>
                </div>
              </div>
            ) : (
              <div className="px-2 text-red-400/80 text-sm">无法获取状态</div>
            )}
          </div>

          {/* Tier Legend */}
          <div className="px-4 py-4 border-t border-white/[0.06]">
            <p className="px-2 mb-3 text-[11px] font-semibold text-slate-500 uppercase tracking-widest">三等级制</p>
            <div className="space-y-2 text-sm px-2">
              <div className="flex items-center gap-2.5 text-slate-300">
                <Crown className="w-4 h-4 text-amber-400" />
                <span>统治者</span>
              </div>
              <div className="flex items-center gap-2.5 text-slate-300">
                <Shield className="w-4 h-4 text-blue-400" />
                <span>护卫者</span>
              </div>
              <div className="flex items-center gap-2.5 text-slate-300">
                <Wrench className="w-4 h-4 text-emerald-400" />
                <span>劳动者</span>
              </div>
            </div>
          </div>

          {/* Help Link */}
          <div className="px-4 py-4 border-t border-white/[0.06]">
            <a
              href="https://github.com/KKKenChow/Cyber-Ideal-State/blob/master/README.md"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2.5 text-slate-500 hover:text-slate-300 transition-colors text-sm px-2 group"
            >
              <HelpCircle className="w-4 h-4" />
              <span>帮助文档</span>
              <ChevronRight className="w-3 h-3 ml-auto opacity-0 -translate-x-1 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
            </a>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 h-full overflow-auto">
          <div className="max-w-6xl mx-auto w-full py-10 px-8">
            <Routes>
              <Route path="/" element={<Dashboard onNavigate={handleNavigate} />} />
              <Route path="/roles" element={<RoleManager onRoleUpdate={refreshAll} />} />
              <Route path="/sessions" element={<SessionManager availableRoles={roles} />} />
            </Routes>
          </div>
        </main>
      </div>
    </div>
  )
}

function NavLink({ to, icon, children, onClick }: { to: string; icon: React.ReactNode; children: React.ReactNode; onClick: (path: string) => void }) {
  const location = useLocation()
  const isActive = location.pathname === to

  return (
    <Link
      to={to}
      onClick={() => onClick(to)}
      className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group relative ${
        isActive 
          ? 'nav-active' 
          : 'nav-inactive'
      }`}
    >
      <span className={`transition-colors duration-200 ${isActive ? 'text-brand-400' : 'text-slate-500 group-hover:text-slate-300'}`}>
        {icon}
      </span>
      <span className="text-sm font-medium">{children}</span>
    </Link>
  )
}

export default App
