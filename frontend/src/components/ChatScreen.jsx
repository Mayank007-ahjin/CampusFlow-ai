import React, { useEffect, useRef } from 'react'

export function ChatScreen({ messages, onSendMessage, inputQuery, setInputQuery }) {
  const messagesEndRef = useRef(null)

  const promptChips = [
    "Plan my campus route (Print & Study)",
    "Plan my campus route (Food & Print)",
    "Plan my campus route (Food , Print & study)",
    "Shortest lunch queue right now?",
    "Where can I print notes quickly?",
    "Quiet space for next 2 hours?"
  ]

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  return (
    <div className="flex-1 flex flex-col h-full bg-slate-50 overflow-y-auto p-3">
      {/* Prompt Chips */}
      <div className="flex gap-1.5 overflow-x-auto pb-2 mb-2 flex-shrink-0 scrollbar-none">
        {promptChips.map((chip, idx) => (
          <button
            key={idx}
            onClick={() => onSendMessage(chip)}
            className="whitespace-nowrap bg-white border border-slate-200 text-slate-700 px-3 py-1 rounded-full text-[11px] font-medium cursor-pointer hover:bg-slate-100 shadow-2xs"
          >
            {chip}
          </button>
        ))}
      </div>

      {/* Messages List */}
      <div className="flex flex-col gap-2.5 flex-1 pb-2">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`p-3 rounded-xl text-[13px] leading-relaxed max-w-[90%] shadow-2xs ${
              msg.sender === 'user'
                ? 'self-end bg-slate-900 text-white rounded-br-xs'
                : 'self-start bg-white border border-slate-200 text-slate-800 rounded-bl-xs w-full'
            }`}
          >
            {msg.isThinking ? (
              <div className="flex items-center gap-2 text-slate-500 italic">
                <span className="inline-block animate-pulse">●</span>
                <span>{msg.text}</span>
              </div>
            ) : (
              <div className="whitespace-pre-line">{msg.text}</div>
            )}
            {msg.recommendation && (
              <div className="mt-2 bg-slate-50 border border-slate-200 rounded-lg p-2.5">
                <div className="font-semibold text-[12px] text-slate-900 mb-0.5">📚 {msg.recommendation.facility_name}</div>
                <div className="text-[11px] text-emerald-600 font-medium">Status: {msg.recommendation.reason}</div>
              </div>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
    </div>
  )
}
