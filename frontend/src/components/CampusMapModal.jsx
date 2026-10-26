import React, { useState } from 'react'

export function CampusMapModal({ facility, onClose }) {
  const [zoom, setZoom] = useState(1)
  const [pan, setPan] = useState({ x: 0, y: 0 })
  const [isDragging, setIsDragging] = useState(false)
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })

  const handleMouseDown = (e) => {
    setIsDragging(true)
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y })
  }

  const handleMouseMove = (e) => {
    if (!isDragging) return
    setPan({
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y
    })
  }

  const handleMouseUp = () => {
    setIsDragging(false)
  }

  const crowdLevel = facility?.current_crowd_level || 'low'

  const getCrowdBadgeStyle = (level) => {
    switch (level) {
      case 'low': return 'bg-emerald-100 text-emerald-800 border-emerald-300'
      case 'moderate': return 'bg-amber-100 text-amber-800 border-amber-300'
      case 'high': return 'bg-rose-100 text-rose-800 border-rose-300'
      default: return 'bg-slate-100 text-slate-800 border-slate-300'
    }
  }

  const getPinColor = (level) => {
    switch (level) {
      case 'low': return 'bg-emerald-600'
      case 'moderate': return 'bg-amber-500'
      case 'high': return 'bg-rose-600'
      default: return 'bg-slate-800'
    }
  }

  return (
    <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4 animate-fade-in">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg overflow-hidden flex flex-col border border-slate-200">
        {/* OpenStreetMap Style Header */}
        <div className="flex justify-between items-center px-4 py-3 bg-[#334155] text-white">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
            <div>
              <h3 className="text-[14px] font-bold tracking-tight">OpenCampus GIS Map Viewer</h3>
              <p className="text-[11px] text-slate-300">Viewing: {facility?.name}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-7 h-7 rounded-full bg-slate-700 text-slate-300 flex items-center justify-center text-[13px] font-bold hover:bg-slate-600 cursor-pointer"
          >
            ✕
          </button>
        </div>

        {/* OSM Vector Viewport Container with Pan & Drag */}
        <div
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          className="relative w-full h-80 bg-[#f4f1ea] cursor-grab active:cursor-grabbing overflow-hidden border-b border-slate-200 select-none"
        >
          <div
            className="absolute inset-0 transition-transform duration-75 ease-out"
            style={{
              transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
              transformOrigin: 'center center'
            }}
          >
            {/* GIS Grid Background */}
            <div className="absolute inset-0 opacity-25 bg-[linear-gradient(to_right,#e2e8f0_1px,transparent_1px),linear-gradient(to_bottom,#e2e8f0_1px,transparent_1px)] [background-size:48px_48px]"></div>

            {/* Campus Road Network */}
            <div className="absolute top-1/2 left-0 right-0 h-10 bg-[#e5e7eb] border-y border-[#cbd5e1] -translate-y-1/2 flex items-center justify-between px-8">
              <span className="text-[9px] text-slate-500 font-mono tracking-wider">CAMPUS AVENUE ➔</span>
              <span className="text-[9px] text-slate-500 font-mono tracking-wider">➔ NORTH GATE</span>
            </div>
            <div className="absolute top-0 bottom-0 left-1/2 w-10 bg-[#e5e7eb] border-x border-[#cbd5e1] -translate-x-1/2 flex flex-col items-center justify-between py-6">
              <span className="text-[9px] text-slate-500 font-mono tracking-widest [writing-mode:vertical-lr]">UNIVERSITY BLVD</span>
            </div>

            {/* Building 1: College Administrative Office */}
            <div className="absolute top-6 left-6 w-32 h-20 bg-[#e8f0fe] border-2 border-[#93c5fd] rounded shadow-xs flex flex-col items-center justify-center p-1 text-center">
              <span className="text-[10px] font-bold text-blue-900">Admin Office</span>
              <span className="text-[9px] text-blue-700">AB1 Ground Flr</span>
              <span className="text-[8px] px-1.5 py-0.5 bg-emerald-100 text-emerald-800 rounded font-semibold mt-1">Low Crowd</span>
            </div>

            {/* Building 2: Central Library & AB2 Branch */}
            <div className="absolute top-6 right-6 w-36 h-20 bg-[#ecfdf5] border-2 border-[#6ee7b7] rounded shadow-sm flex flex-col items-center justify-center p-1 text-center">
              <span className="text-[10px] font-bold text-emerald-900">Central Library</span>
              <span className="text-[9px] text-emerald-700">AB2 Study Branch</span>
              <span className="text-[8px] px-1.5 py-0.5 bg-emerald-100 text-emerald-800 rounded font-semibold mt-1">Low Crowd</span>
            </div>

            {/* Building 3: Main Canteen */}
            <div className="absolute bottom-6 left-6 w-32 h-20 bg-[#fff1f2] border-2 border-[#fda4af] rounded shadow-xs flex flex-col items-center justify-center p-1 text-center">
              <span className="text-[10px] font-bold text-rose-900">Main Canteen</span>
              <span className="text-[9px] text-rose-700">Mess Building</span>
              <span className="text-[8px] px-1.5 py-0.5 bg-rose-100 text-rose-800 rounded font-semibold mt-1">High Rush (~10m)</span>
            </div>

            {/* Building 4: Stationery & Print Shop */}
            <div className="absolute bottom-6 right-6 w-36 h-20 bg-[#fffbeb] border-2 border-[#fcd34d] rounded shadow-xs flex flex-col items-center justify-center p-1 text-center">
              <span className="text-[10px] font-bold text-amber-900">Stationery & Print</span>
              <span className="text-[9px] text-amber-700">Workshop Bldg</span>
              <span className="text-[8px] px-1.5 py-0.5 bg-amber-100 text-amber-800 rounded font-semibold mt-1">Moderate (~4m)</span>
            </div>

            {/* Live Facility GIS Marker */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-full flex flex-col items-center pointer-events-none drop-shadow-xl">
              <div className="bg-slate-900 text-white text-[10px] font-bold px-3 py-1 rounded-md shadow-lg whitespace-nowrap mb-1 flex items-center gap-2 border border-slate-700">
                <span>📍 {facility?.name}</span>
                <span className={`text-[9px] px-1.5 py-0.5 rounded uppercase font-extrabold ${getCrowdBadgeStyle(crowdLevel)}`}>
                  {crowdLevel}
                </span>
              </div>
              <div className={`w-5 h-5 rounded-full border-2 border-white shadow-xl animate-bounce ${getPinColor(crowdLevel)} flex items-center justify-center text-white text-[9px] font-bold`}>
                ★
              </div>
            </div>
          </div>

          {/* Attribution Tag */}
          <div className="absolute bottom-2 left-2 bg-white/90 backdrop-blur-xs px-2 py-0.5 rounded text-[9px] text-slate-500 font-mono border border-slate-200 pointer-events-none">
            © OpenCampus GIS • Click & drag to pan map
          </div>
        </div>

        {/* GIS Controls Toolbar */}
        <div className="p-3 bg-slate-50 flex justify-between items-center text-[12px] text-slate-700 border-t border-slate-200">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-500 text-[11px]">Zoom:</span>
            <button
              onClick={() => setZoom(Math.max(0.8, zoom - 0.25))}
              className="w-7 h-7 bg-white border border-slate-300 rounded hover:bg-slate-100 font-bold flex items-center justify-center shadow-xs cursor-pointer"
            >
              -
            </button>
            <span className="font-mono font-semibold text-[11px]">{Math.round(zoom * 100)}%</span>
            <button
              onClick={() => setZoom(Math.min(2.0, zoom + 0.25))}
              className="w-7 h-7 bg-white border border-slate-300 rounded hover:bg-slate-100 font-bold flex items-center justify-center shadow-xs cursor-pointer"
            >
              +
            </button>
            <button
              onClick={() => { setZoom(1); setPan({ x: 0, y: 0 }); }}
              className="ml-2 px-2.5 py-1 bg-white border border-slate-300 rounded text-[11px] font-medium hover:bg-slate-100 cursor-pointer shadow-xs"
            >
              Reset
            </button>
          </div>

          <div className="flex items-center gap-3 text-[11px]">
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-emerald-600"></span> Low</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-amber-500"></span> Moderate</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-rose-600"></span> High</span>
          </div>
        </div>
      </div>
    </div>
  )
}
