import { useState, useEffect } from 'react'
import { Play, Trash2, Clock } from 'lucide-react'
import { api } from '../lib/api'

type Session = {
  id: string
  role_id: string
  mode: string
  created_at: string
  updated_at: string
  messages: Array<{
    role: string
    content: string
    timestamp: string
  }>
  active: boolean
}

export default function SessionPanel() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadSessions()
  }, [])

  const loadSessions = async () => {
    try {
      setLoading(true)
      const response = await api.get('/api/sessions')
      setSessions(response.data.sessions)
    } catch (error) {
      console.error('Failed to load sessions:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2">会话面板</h2>
          <p className="text-slate-400">管理你的对话会话</p>
        </div>
      </div>

      {loading ? (
        <div className="text-center text-slate-400 py-12">加载中...</div>
      ) : sessions.length === 0 ? (
        <div className="text-center text-slate-400 py-12">
          <p>还没有会话</p>
          <p className="text-sm mt-2">从角色管理开始对话</p>
        </div>
      ) : (
        <div className="space-y-4">
          {sessions.map((session) => (
            <div
              key={session.id}
              className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-4">
                  <Clock className="w-5 h-5 text-slate-400" />
                  <div>
                    <h3 className="text-lg font-semibold text-white">
                      会话 {session.id}
                    </h3>
                    <p className="text-slate-400 text-sm">
                      {session.mode === 'philosopher' && '统治者模式'}
                      {session.mode === 'guardian' && '护卫者模式'}
                      {session.mode === 'worker' && '劳动者模式'}
                    </p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button className="p-2 hover:bg-slate-700 rounded-lg transition-colors">
                    <Play className="w-4 h-4 text-green-400" />
                  </button>
                  <button className="p-2 hover:bg-slate-700 rounded-lg transition-colors">
                    <Trash2 className="w-4 h-4 text-red-400" />
                  </button>
                </div>
              </div>

              <div className="text-sm text-slate-400">
                {session.messages.length} 条消息
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
