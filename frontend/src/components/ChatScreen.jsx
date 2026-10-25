import React, { useState } from 'react'

export function ChatScreen({ messages, onSendMessage, inputQuery, setInputQuery }) {
  const promptChips = [
    "Plan my campus route (Print & Study)",
    "Plan my campus route (Food & Print)",
    "Plan my campus route (Food , Print & study)",
    "Shortest lunch queue right now?",
    "Where can I print notes quickly?",
    "Quiet space for next 2 hours?"
  ]

  const handleSend = (e) => {
    e?.preventDefault()
    if (!inputQuery.trim()) return
    onSendMessage(inputQuery)
  }

  return (
    <div className="p-4 overflow-y-auto flex-1 flex flex-col justify-between">
      <div>
        <div className="flex gap-2 overflow-x-auto pb-2 mb-3 scrollbar-none">
          {promptChips.map((chip, index) => (
            <button
              key={index}
              onClick={() => onSendMessage(chip)}
              className="whitespace-nowrap bg-gray-200 text-gray-700 px-3 py-1.5 rounded-full text-[12px] font-medium cursor-pointer border-none hover:bg-gray-300"
            >
              {chip}
            </button>
          ))}
        </div>

        <div className="flex flex-col gap-3">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`p-3 rounded-lg text-[14px] leading-relaxed max-w-[88%] ${
                msg.sender === 'user'
                  ? 'self-end bg-brand-primary text-white rounded-br-sm'
                  : 'self-start bg-white border border-gray-200 rounded-bl-sm w-full'
              }`}
            >
              <div>{msg.text}</div>
              {msg.recommendation && (
                <div className="mt-2.5 bg-gray-50 border border-gray-200 rounded p-2.5">
                  <div className="font-semibold text-[13px] mb-1">📚 {msg.recommendation.facility_name}</div>
                  <div className="text-[12px] text-green-700 font-medium">Status: {msg.recommendation.reason}</div>
                  <div className="text-[11px] text-gray-500 mt-1">Verified via live student reports</div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
