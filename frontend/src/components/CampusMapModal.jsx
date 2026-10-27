import React from 'react'

export function CampusMapModal({ facility, onClose }) {
  const crowdLevel = facility?.current_crowd_level || 'low'

  const getCrowdBadgeStyle = (level) => {
    switch (level) {
      case 'low': return 'bg-emerald-100 text-emerald-800 border-emerald-300'
      case 'moderate': return 'bg-amber-100 text-amber-800 border-amber-300'
      case 'high': return 'bg-rose-100 text-rose-800 border-rose-300'
      default: return 'bg-slate-100 text-slate-800 border-slate-300'
    }
  }

  // Use the actual facility latitude and longitude from the database object
  const lat = facility?.latitude || 28.472353
  const lon = facility?.longitude || 77.489328

  const getOsmEmbedUrl = () => {
    return `https://www.openstreetmap.org/export/embed.html?bbox=${Number(lon)-0.003}%2C${Number(lat)-0.003}%2C${Number(lon)+0.003}%2C${Number(lat)+0.003}&layer=mapnik&marker=${lat}%2C${lon}`
  }

  const getOsmLinkUrl = () => {
    return `https://www.openstreetmap.org/?mlat=${lat}&mlon=${lon}#map=17/${lat}/${lon}`
  }

  return (
    <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4 animate-fade-in">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg overflow-hidden flex flex-col border border-slate-200">
        {/* OpenStreetMap Style Header */}
        <div className="flex justify-between items-center px-4 py-3 bg-[#334155] text-white">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
            <div>
              <h3 className="text-[14px] font-bold tracking-tight">OpenStreetMap Campus View</h3>
              <p className="text-[11px] text-slate-300">{facility?.name} ({lat}, {lon})</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-7 h-7 rounded-full bg-slate-700 text-slate-300 flex items-center justify-center text-[13px] font-bold hover:bg-slate-600 cursor-pointer"
          >
            ✕
          </button>
        </div>

        {/* OSM Embedded Tile View */}
        <div className="relative w-full h-80 bg-slate-100 overflow-hidden border-b border-slate-200">
          <iframe
            title="OpenStreetMap View"
            width="100%"
            height="100%"
            frameBorder="0"
            scrolling="no"
            marginHeight="0"
            marginWidth="0"
            src={getOsmEmbedUrl()}
            style={{ border: 0 }}
          />

          {/* Floating Live Crowd Badge Overlay */}
          <div className="absolute top-3 left-3 bg-white/95 backdrop-blur-xs px-3 py-1.5 rounded-lg shadow-md border border-slate-200 flex items-center gap-2 pointer-events-none">
            <span className="text-[12px]">📍</span>
            <div>
              <div className="text-[11px] font-bold text-slate-900">{facility?.name}</div>
              <div className={`text-[10px] px-1 py-0.2 rounded font-extrabold uppercase inline-block mt-0.5 ${getCrowdBadgeStyle(crowdLevel)}`}>
                {crowdLevel} Crowd
              </div>
            </div>
          </div>
        </div>

        {/* GIS Controls Toolbar */}
        <div className="p-3 bg-slate-50 flex justify-between items-center text-[12px] text-slate-700 border-t border-slate-200">
          <div className="flex items-center gap-2 text-[11px] text-slate-500">
            <span>Lat: {lat}, Lon: {lon}</span>
          </div>

          <a
            href={getOsmLinkUrl()}
            target="_blank"
            rel="noopener noreferrer"
            className="px-3 py-1 bg-slate-900 text-white rounded text-[11px] font-medium hover:bg-slate-800 transition-colors shadow-xs"
          >
            View Larger Map ↗
          </a>
        </div>
      </div>
    </div>
  )
}
