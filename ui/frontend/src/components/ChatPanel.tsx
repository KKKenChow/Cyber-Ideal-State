import { useState, useEffect, useRef } from 'react'
import { Send, ArrowDown, Download, Trash2, Sparkles } from 'lucide-react'
import { api } from '../lib/api'

interface ChatPanelProps {
  sessionId: string
  participants: Array<{
    role_id: string
    role_name: string
    tier: string
  }>
  onMessageSent?: () => void
}

interface Message {
  role: string  // 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  metadata?: any
}

export default function ChatPanel({ sessionId, participants, onMessageSent }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [scrolledToBottom, setScrolledToBottom] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const messagesContainerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    loadMessages()
  }, [sessionId])

  const loadMessages = async () => {
    try {
      const response = await api.get(`/api/sessions/${sessionId}`)
      setMessages(response.data.messages || [])
    } catch (error) {
      console.error('Failed to load messages:', error)
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    setScrolledToBottom(true)
  }

  useEffect(() => {
    if (scrolledToBottom) {
      scrollToBottom()
    }
  }, [messages])

  const handleScroll = () => {
    if (!messagesContainerRef.current) return
    
    const { scrollTop, scrollHeight, clientHeight } = messagesContainerRef.current
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 100
    setScrolledToBottom(isAtBottom)
  }

  const handleSendMessage = async (e?: React.FormEvent) => {
    e?.preventDefault()
    
    if (!inputMessage.trim() || loading) return

    const messageToSend = inputMessage.trim()
    setInputMessage('')
    setLoading(true)

    try {
      const userMessage: Message = {
        role: 'user',
        content: messageToSend,
        timestamp: new Date().toISOString()
      }
      
      setMessages(prev => [...prev, userMessage])

      const response = await api.post(`/api/sessions/${sessionId}/messages`, {
        role: 'user',
        content: messageToSend
      })

      if (response.data.responses) {
        const assistantMessages = response.data.responses.map((resp: any) => ({
          role: 'assistant',
          content: resp.content,
          timestamp: new Date().toISOString(),
          metadata: {
            role_id: resp.role_id,
            role_name: resp.role_name
          }
        }))
        
        setMessages(prev => [...prev, ...assistantMessages])
      }

      onMessageSent?.()
    } catch (error) {
      console.error('Failed to send message:', error)
      alert('发送消息失败')
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleExportChat = async () => {
    try {
      const markdown = messages.map(msg => {
        const timestamp = new Date(msg.timestamp).toLocaleString('zh-CN')
        
        if (msg.role === 'user') {
          return `## 你 (${timestamp})\n\n${msg.content}\n`
        } else if (msg.role === 'assistant') {
          const roleName = msg.metadata?.role_name || 'AI'
          return `## ${roleName} (${timestamp})\n\n${msg.content}\n`
        }
        return ''
      }).join('\n---\n')

      const blob = new Blob([markdown], { type: 'text/markdown' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `chat-${sessionId}-${new Date().toISOString().split('T')[0]}.md`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Failed to export chat:', error)
      alert('导出失败')
    }
  }

  const handleClearChat = async () => {
    if (!confirm('确定要清空会话记录吗？')) return

    try {
      await api.delete(`/api/sessions/${sessionId}/messages`)
      const systemMessages = messages.filter(m => m.role === 'system')
      setMessages(systemMessages)
    } catch (error) {
      console.error('Failed to clear chat:', error)
      alert('清空失败')
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

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'philosopher': return 'bg-amber-500/15 border-amber-500/20'
      case 'guardian': return 'bg-blue-500/15 border-blue-500/20'
      case 'worker': return 'bg-emerald-500/15 border-emerald-500/20'
      default: return 'bg-slate-500/15 border-slate-500/20'
    }
  }

  const getRoleForMessage = (message: Message) => {
    if (message.metadata?.role_id) {
      const participant = participants.find(p => p.role_id === message.metadata.role_id)
      return participant
    }
    return null
  }

  const isVoteResult = (message: Message) => {
    return message.metadata?.type === 'vote_result' || 
           message.metadata?.type === 'consensus_fallback_vote'
  }

  const isDebateResult = (message: Message) => {
    return message.metadata?.type === 'debate_result'
  }

  const isConsensusResult = (message: Message) => {
    return message.metadata?.type === 'consensus_result'
  }

  const isDecisionResult = (message: Message) => {
    return isVoteResult(message) || isDebateResult(message) || isConsensusResult(message)
  }

  return (
    <div className="flex-1 flex flex-col bg-surface/50">
      {/* Messages Container */}
      <div
        ref={messagesContainerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-auto px-6 py-6 space-y-5"
      >
        {/* Welcome Message */}
        {messages.length === 0 && (
          <div className="text-center py-20 animate-fade-in">
            <div className="w-16 h-16 rounded-2xl bg-brand-500/15 flex items-center justify-center text-3xl mx-auto mb-5">
              💬
            </div>
            <p className="text-xl text-white font-medium mb-2">开始对话</p>
            <p className="text-slate-400 text-sm">
              {participants.map(p => p.role_name).join(', ')} 正在等待你的消息
            </p>
          </div>
        )}

        {/* Messages */}
        {messages.map((message, index) => (
          <div key={index} className="animate-fade-in-up" style={{ animationDelay: '0ms' }}>
            {message.role === 'system' && (
              <div className="text-center py-3">
                <span className="text-slate-500 text-xs bg-white/[0.03] px-4 py-1.5 rounded-full border border-white/[0.04]">
                  {message.content}
                </span>
              </div>
            )}

            {message.role === 'user' && (
              <div className="flex justify-end">
                <div className="max-w-2xl bg-gradient-to-br from-brand-600 to-brand-700 text-white px-5 py-3.5 rounded-2xl rounded-tr-md shadow-lg shadow-brand-500/10">
                  <p className="whitespace-pre-wrap break-words text-[15px] leading-relaxed">{message.content}</p>
                  <div className="text-xs text-brand-200/60 mt-1.5 text-right">
                    {new Date(message.timestamp).toLocaleTimeString('zh-CN', {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </div>
                </div>
              </div>
            )}

            {message.role === 'assistant' && (
              <div className="flex justify-start">
                <div className={`max-w-2xl px-5 py-3.5 rounded-2xl rounded-tl-md ${
                  isDecisionResult(message)
                    ? isConsensusResult(message)
                      ? 'bg-emerald-500/10 border border-emerald-500/20'
                      : isDebateResult(message)
                      ? 'bg-amber-500/10 border border-amber-500/20'
                      : 'bg-blue-500/10 border border-blue-500/20'
                    : 'glass-card'
                }`}>
                  {/* Role Info */}
                  {message.metadata && (
                    <div className="flex items-center gap-2.5 mb-2.5">
                      <div className={`w-7 h-7 rounded-lg flex items-center justify-center text-sm border ${getTierColor(getRoleForMessage(message)?.tier || 'worker')}`}>
                        {getTierIcon(getRoleForMessage(message)?.tier || 'worker')}
                      </div>
                      <span className="font-medium text-slate-300 text-sm">
                        {message.metadata.role_name || 'AI'}
                      </span>
                      {isConsensusResult(message) && (
                        <span className="bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded-md text-[11px] font-medium">
                          共识达成
                        </span>
                      )}
                      {isDebateResult(message) && (
                        <span className="bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded-md text-[11px] font-medium">
                          辩论总结
                        </span>
                      )}
                      {isVoteResult(message) && (
                        <span className="bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded-md text-[11px] font-medium">
                          投票结果
                        </span>
                      )}
                    </div>
                  )}

                  {/* Consensus Result Display */}
                  {isConsensusResult(message) && (
                    <div className="mb-4 space-y-2">
                      <div className="flex items-center gap-2 text-sm">
                        <span className="text-emerald-400 font-medium">✓ 共识达成</span>
                        {message.metadata.rounds && (
                          <span className="text-slate-500 text-xs">（{message.metadata.rounds} 轮协商）</span>
                        )}
                      </div>
                      {message.metadata.proposal && (
                        <div className="text-sm text-slate-300 bg-white/[0.03] rounded-lg p-3 border border-white/[0.06]">
                          {message.metadata.proposal}
                        </div>
                      )}
                      {message.metadata.confidence && (
                        <div className="text-xs text-slate-500">
                          置信度: {Math.round(message.metadata.confidence * 100)}%
                        </div>
                      )}
                    </div>
                  )}

                  {/* Debate Result Display */}
                  {isDebateResult(message) && (
                    <div className="mb-4 space-y-2">
                      <div className="flex items-center gap-2 text-sm">
                        <span className="text-amber-400 font-medium">🎭 辩论总结</span>
                        {message.metadata.debate_rounds && (
                          <span className="text-slate-500 text-xs">（{message.metadata.debate_rounds} 轮辩论）</span>
                        )}
                      </div>
                      {message.metadata.confidence && (
                        <div className="text-xs text-slate-500">
                          置信度: {Math.round(message.metadata.confidence * 100)}%
                        </div>
                      )}
                    </div>
                  )}

                  {/* Vote Result Display */}
                  {isVoteResult(message) && message.metadata?.votes && (
                    <div className="mb-4 space-y-2">
                      {Object.entries(message.metadata.votes).map(([roleId, voteData]: [string, any]) => (
                        <div key={roleId} className="flex items-center gap-3 text-sm">
                          <span className="text-slate-300">{voteData.role_name}</span>
                          {voteData.weight !== undefined && voteData.weight > 0 && (
                            <span className="text-slate-600 text-[10px]">×{voteData.weight}</span>
                          )}
                          <span className={`px-2 py-0.5 rounded-md font-medium text-xs ${
                            voteData.vote === 'YES'
                              ? 'bg-emerald-500/15 text-emerald-300'
                              : voteData.vote === 'NO'
                              ? 'bg-red-500/15 text-red-300'
                              : 'bg-slate-500/15 text-slate-300'
                          }`}>
                            {voteData.vote}
                          </span>
                        </div>
                      ))}
                      <div className="pt-2.5 border-t border-white/[0.06]">
                        <span className="text-sm font-medium">
                          最终结果: <span className={
                            message.metadata.result === 'YES' ? 'text-emerald-400' :
                            message.metadata.result === 'NO' ? 'text-red-400' :
                            message.metadata.result === 'CONSENSUS' ? 'text-emerald-400' :
                            'text-slate-400'
                          }>{message.metadata.result}</span>
                          <span className="text-slate-500 ml-2 text-xs">
                            (YES: {message.metadata.yes_count}, NO: {message.metadata.no_count})
                          </span>
                        </span>
                        {!message.metadata.consensus_reached && message.metadata.type === 'consensus_fallback_vote' && (
                          <span className="text-amber-400 text-xs ml-2">（共识未达成，降级为投票）</span>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Regular Message */}
                  <p className="whitespace-pre-wrap break-words text-[15px] text-slate-200 leading-relaxed">{message.content}</p>
                  
                  <div className="text-xs text-slate-600 mt-2">
                    {new Date(message.timestamp).toLocaleTimeString('zh-CN', {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}

        {/* Loading Indicator */}
        {loading && (
          <div className="flex justify-start animate-fade-in">
            <div className="glass-card px-5 py-4">
              <div className="flex items-center gap-3">
                <div className="flex space-x-1.5">
                  <div className="w-2 h-2 bg-brand-400 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-brand-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                  <div className="w-2 h-2 bg-brand-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                </div>
                <span className="text-slate-500 text-xs">AI 正在思考...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Scroll Button */}
      {!scrolledToBottom && (
        <button
          onClick={scrollToBottom}
          className="absolute bottom-32 right-8 bg-brand-600 hover:bg-brand-500 text-white p-2.5 rounded-full shadow-glow transition-all duration-200 hover:scale-105"
          title="滚动到底部"
        >
          <ArrowDown className="w-4 h-4" />
        </button>
      )}

      {/* Input Area */}
      <div className="border-t border-white/[0.06] bg-slate-950/60 backdrop-blur-2xl p-5">
        <div className="max-w-4xl mx-auto">
          {/* Toolbar */}
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2 text-xs text-slate-500">
              <Sparkles className="w-3.5 h-3.5" />
              <span>参与者:</span>
              {participants.map(p => (
                <span key={p.role_id} className={`inline-flex items-center gap-1 px-2 py-1 rounded-md border text-[11px] font-medium ${getTierColor(p.tier)}`}>
                  <span className="text-[10px]">{getTierIcon(p.tier)}</span>
                  <span className="text-slate-300">{p.role_name}</span>
                </span>
              ))}
            </div>
            
            <div className="flex gap-1">
              <button
                onClick={handleExportChat}
                className="btn-ghost rounded-lg"
                title="导出对话"
              >
                <Download className="w-4 h-4 text-slate-500" />
              </button>
              <button
                onClick={handleClearChat}
                className="btn-ghost rounded-lg"
                title="清空对话"
              >
                <Trash2 className="w-4 h-4 text-red-400/60" />
              </button>
            </div>
          </div>

          {/* Input */}
          <form onSubmit={handleSendMessage} className="flex gap-3">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
              className="flex-1 input-field min-h-[52px] max-h-[200px] py-3 resize-none"
              placeholder={participants.length > 1 
                ? `发送给 ${participants.map(p => p.role_name).join(', ')}` 
                : '输入消息...'}
              rows={1}
            />
            <button
              type="submit"
              disabled={!inputMessage.trim() || loading}
              className="btn-primary px-5 py-3 rounded-xl flex items-center gap-2 self-end"
            >
              <Send className="w-4 h-4" />
              发送
            </button>
          </form>
          
          <p className="text-[11px] text-slate-600 mt-2">
            按 Enter 发送，Shift + Enter 换行
          </p>
        </div>
      </div>
    </div>
  )
}
