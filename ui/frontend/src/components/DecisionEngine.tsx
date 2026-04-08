import { useState } from 'react'
import { Vote, MessageSquare, Users, Info } from 'lucide-react'

export default function DecisionEngine() {
  const [mode, setMode] = useState<'vote' | 'debate' | 'consensus'>('vote')

  const modes = [
    { key: 'vote', icon: <Vote className="w-5 h-5" />, title: '投票模式', desc: '多个角色对议题进行投票，根据权重计算最终决策' },
    { key: 'debate', icon: <MessageSquare className="w-5 h-5" />, title: '辩论模式', desc: '多个角色围绕议题展开多轮辩论，最终总结各方观点形成决策' },
    { key: 'consensus', icon: <Users className="w-5 h-5" />, title: '共识模式', desc: '多个角色通过多轮协商达成共识，如果无法达成则回退到投票' }
  ]

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-white mb-2">决策模式说明</h2>
        <p className="text-slate-400">在创建会话时可以选择不同的决策模式</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {modes.map((m) => (
          <button
            key={m.key}
            onClick={() => setMode(m.key as any)}
            className={`p-6 rounded-xl border-2 transition-all ${
              mode === m.key
                ? 'bg-purple-600/20 border-purple-500'
                : 'bg-slate-800/50 border-slate-700 hover:border-purple-400'
            }`}
          >
            <div className="flex items-center gap-3 mb-3">
              <div className={`p-2 rounded-lg ${
                mode === m.key ? 'bg-purple-500' : 'bg-slate-700'
              }`}>
                {m.icon}
              </div>
              <h3 className="text-xl font-semibold text-white">{m.title}</h3>
            </div>
            <p className={`text-sm ${
              mode === m.key ? 'text-purple-200' : 'text-slate-400'
            }`}>
              {m.desc}
            </p>
          </button>
        ))}
      </div>

      {/* Mode Details */}
      <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700">
        <div className="flex items-start gap-4">
          <div className="flex-shrink-0 p-3 rounded-lg bg-purple-500/20">
            <Info className="w-6 h-6 text-purple-400" />
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-semibold text-white mb-4">如何使用</h3>
            
            <div className="space-y-4">
              <div>
                <div className="text-white font-medium mb-2">创建会话时选择模式</div>
                <p className="text-slate-400 text-sm">
                  在"会话管理"页面创建会话时，从"发言模式"下拉菜单中选择你想要的决策模式。
                </p>
              </div>

              <div>
                <div className="text-white font-medium mb-2">多角色会话</div>
                <p className="text-slate-400 text-sm">
                  决策模式主要用于多角色会话。选择多个角色后，系统会根据选择的模式自动处理角色间的互动。
                </p>
              </div>

              <div>
                <div className="text-white font-medium mb-2">查看结果</div>
                <p className="text-slate-400 text-sm">
                  在聊天面板中发送消息后，你可以看到每个角色的回复以及最终的决策结果（如果是投票模式）。
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
