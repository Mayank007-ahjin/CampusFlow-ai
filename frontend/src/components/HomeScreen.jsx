import React from 'react'

export function HomeScreen({ facilities, onSelectFacility }) {
  const getBadgeStyle = (level) => {
    switch (level) {
      case 'low': return 'bg-green-100 text-green-800'
      case 'moderate': return 'bg-amber-100 text-amber-800'
      case 'high': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getFacilityIcon = (type) => {
    switch (type) {
      case 'library': return '📚'
      case 'canteen': return '🥪'
      case 'stationery': return '🖨️'
      default: return '🏢'
    }
  }

  const formatMetric = (facility) => {
    if (facility.available_seats !== null && facility.available_seats !== undefined) {
      return `${facility.available_seats} seats available`
    }
    if (facility.estimated_wait_minutes !== null && facility.estimated_wait_minutes !== undefined) {
      return `~${facility.estimated_wait_minutes} min wait`
    }
    return `Status: ${facility.current_crowd_level}`
  }

  return (
    <div className="p-4 overflow-y-auto flex-1">
      <div className="mb-3.5">
        <h1 className="text-[18px] font-semibold leading-6">Live Campus Status</h1>
        <p className="text-[13px] text-gray-500 mt-0.5">Real-time crowd estimates across facilities</p>
      </div>

      {facilities.length === 0 ? (
        <div className="text-center py-8 text-gray-500 text-sm">
          Loading facilities... Make sure backend is running.
        </div>
      ) : (
        facilities.map((facility) => (
          <div
            key={facility.id}
            onClick={() => onSelectFacility(facility)}
            className="bg-white border border-gray-200 rounded-lg p-3.5 mb-3 cursor-pointer hover:border-gray-300 transition-colors"
          >
            <div className="flex justify-between items-center mb-2">
              <div className="text-[15px] font-semibold flex items-center gap-2">
                <span>{getFacilityIcon(facility.type)}</span>
                <span>{facility.name}</span>
              </div>
              <span className={`text-[11px] font-semibold px-2 py-0.5 rounded ${getBadgeStyle(facility.current_crowd_level)}`}>
                {facility.current_crowd_level.charAt(0).toUpperCase() + facility.current_crowd_level.slice(1)} Crowd
              </span>
            </div>

            <div className="text-[20px] font-bold tracking-tight mb-0.5">
              {formatMetric(facility)}
            </div>
            <div className="text-[12px] text-gray-500">
              {facility.location || 'Campus facility'} • Open until {facility.closing_time || '22:00'}
            </div>

            <div className="border-t border-gray-100 mt-2.5 pt-2 flex justify-between items-center text-[11px] text-gray-500">
              <span className="bg-[#F0F5F8] text-[#4A7C9D] px-2 py-0.5 rounded text-[10px] font-medium">
                {facility.data_source === 'student_report' ? 'Live Report' : 'Simulated Data'}
              </span>
              <span>Updated recently</span>
            </div>
          </div>
        ))
      )}
    </div>
  )
}
