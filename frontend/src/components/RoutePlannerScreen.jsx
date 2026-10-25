import React, { useState, useEffect } from 'react'

export function RoutePlannerScreen({ facilities }) {
  const [selectedGoal, setSelectedGoal] = useState('Print & Study')
  const [routeResult, setRouteResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [customGoalInput, setCustomGoalInput] = useState('')

  const goalPresets = [
    { label: 'Print & Study', query: 'Plan my campus route (Print & Study)' },
    { label: 'Food & Print', query: 'Plan my campus route (Food & Print)' },
    { label: 'Quiet Study & Lunch', query: 'Plan my campus route (Quiet Study & Lunch)' },
    { label: 'Quick Stationery Run', query: 'Plan my campus route (Quick Stationery Run)' },
    { label: 'Afternoon Group Study', query: 'Plan my campus route (Afternoon Group Study)' }
  ]

  const fetchRoute = async (query) => {
    setLoading(true)
    try {
      const response = await fetch('/api/v1/plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      })
      const data = await response.json()
      setRouteResult(data)
    } catch (err) {
      console.error('Failed to fetch route:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchRoute(goalPresets[0].query)
  }, [])

  const handleCustomSubmit = (e) => {
    e?.preventDefault()
    if (!customGoalInput.trim()) return
    setSelectedGoal(customGoalInput)
    fetchRoute(`Plan my campus route (${customGoalInput})`)
    setCustomGoalInput('')
  }

  const getBadgeStyle = (level) => {
    switch (level) {
      case 'low': return 'bg-emerald-50 text-emerald-700 border-emerald-200'
      case 'moderate': return 'bg-amber-50 text-amber-700 border-amber-200'
      case 'high': return 'bg-rose-50 text-rose-700 border-rose-200'
      default: return 'bg-slate-50 text-slate-700 border-slate-200'
    }
  }

  return (
    <div className="p-4 overflow-y-auto flex-1 flex flex-col bg-slate-50">
      <div className="mb-3">
        <h1 className="text-[17px] font-semibold text-slate-900 tracking-tight">Multi-Agent Route Planner</h1>
        <p className="text-[12px] text-slate-500 mt-0.5">Optimized multi-facility campus itineraries</p>
      </div>

      {/* Preset Goal Selector */}
      <div className="mb-3">
        <label className="block text-[11px] font-semibold text-slate-600 mb-1.5 uppercase tracking-wider">
          Preset Itineraries
        </label>
        <div className="flex gap-1.5 overflow-x-auto pb-1 scrollbar-none">
          {goalPresets.map((goal, idx) => (
            <button
              key={idx}
              onClick={() => {
                setSelectedGoal(goal.label)
                fetchRoute(goal.query)
              }}
              className={`whitespace-nowrap px-3 py-1.5 rounded-full text-[12px] font-medium transition-all cursor-pointer border ${
                selectedGoal === goal.label
                  ? 'bg-slate-900 text-white border-slate-900 shadow-xs'
                  : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-100'
              }`}
            >
              {goal.label}
            </button>
          ))}
        </div>
      </div>

      {/* Custom Itinerary Input */}
      <form onSubmit={handleCustomSubmit} className="mb-3.5 flex gap-1.5">
        <input
          type="text"
          value={customGoalInput}
          onChange={(e) => setCustomGoalInput(e.target.value)}
          placeholder="Or type custom itinerary (e.g. coffee & reading)..."
          className="flex-1 h-[36px] bg-white border border-slate-200 rounded-md px-3 text-[12px] text-slate-800 outline-none focus:border-slate-400"
        />
        <button
          type="submit"
          className="h-[36px] px-3 bg-slate-900 text-white rounded-md text-[12px] font-medium cursor-pointer hover:bg-slate-800 transition-colors"
        >
          Plan
        </button>
      </form>

      {/* Results Box */}
      <div className="bg-white border border-slate-200 rounded-xl p-3.5 flex-1 flex flex-col shadow-xs">
        <div className="text-[13px] font-semibold text-slate-800 mb-2.5 flex items-center justify-between border-b border-slate-100 pb-2">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            Agent Route: {selectedGoal}
          </span>
          <span className="text-[11px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-medium">
            Live Analysis
          </span>
        </div>

        {loading ? (
          <div className="flex-1 flex items-center justify-center py-8 text-slate-400 text-[13px]">
            Synthesizing optimal stop sequence...
          </div>
        ) : routeResult ? (
          <div className="flex flex-col gap-3 flex-1">
            <div className="bg-slate-50 border border-slate-100 p-2.5 rounded-lg text-[12px] text-slate-700 leading-relaxed">
              {routeResult.answer}
            </div>

            <div>
              <div className="text-[11px] font-semibold text-slate-400 mb-2 uppercase tracking-wider">
                Recommended Stop Sequence
              </div>
              <div className="flex flex-col gap-2">
                {routeResult.recommendations?.map((rec, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between bg-white border border-slate-200/80 p-2.5 rounded-lg shadow-2xs hover:border-slate-300 transition-colors"
                  >
                    <div className="flex items-center gap-2.5">
                      <div className="w-5 h-5 rounded-full bg-slate-900 text-white flex items-center justify-center font-semibold text-[11px]">
                        {i + 1}
                      </div>
                      <div>
                        <div className="font-semibold text-[13px] text-slate-900">{rec.facility_name}</div>
                        <div className="text-[11px] text-slate-500">{rec.reason}</div>
                      </div>
                    </div>
                    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded border uppercase tracking-wider ${getBadgeStyle(rec.crowd_level)}`}>
                      {rec.crowd_level}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center py-8 text-slate-400 text-[13px]">
            Select an option above to generate route.
          </div>
        )}
      </div>
    </div>
  )
}
