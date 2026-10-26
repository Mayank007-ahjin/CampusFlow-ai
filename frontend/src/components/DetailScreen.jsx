import React, { useState } from 'react'
import { CampusMapModal } from './CampusMapModal'

export function DetailScreen({ facility, onSubmitReport }) {
  const [selectedPill, setSelectedPill] = useState('Empty')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitSuccess, setSubmitSuccess] = useState(false)
  const [isMapOpen, setIsMapOpen] = useState(false)

  if (!facility) return <div className="p-4">No facility selected</div>

  const getBadgeStyle = (level) => {
    switch (level) {
      case 'low': return 'bg-green-100 text-green-800'
      case 'moderate': return 'bg-amber-100 text-amber-800'
      case 'high': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const handleReportSubmit = async () => {
    setIsSubmitting(true)
    let crowdLevel = 'low'
    if (selectedPill === 'Moderate') crowdLevel = 'moderate'
    if (selectedPill === 'Packed') crowdLevel = 'high'

    await onSubmitReport({
      facility_id: facility.id,
      crowd_level: crowdLevel,
      notes: `Reported as ${selectedPill} by student`
    })

    setIsSubmitting(false)
    setSubmitSuccess(true)
    setTimeout(() => setSubmitSuccess(false), 2500)
  }

  const occupancyPercent = facility.total_capacity && facility.available_seats !== null
    ? Math.round(((facility.total_capacity - facility.available_seats) / facility.total_capacity) * 100)
    : 34

  return (
    <div className="p-4 overflow-y-auto flex-1">
      <div className="bg-white border border-gray-200 rounded-lg p-4 mb-4">
        <div className="text-[11px] font-semibold uppercase tracking-wider text-gray-500">Current Occupancy</div>
        <div className="text-[34px] font-bold my-1">{occupancyPercent}%</div>
        <div className="text-[12px] text-gray-500">
          {facility.available_seats !== null ? `${facility.available_seats} of ${facility.total_capacity || 120} seats available` : facility.name}
        </div>

        <div className="w-full h-2 bg-gray-200 rounded-full my-3 overflow-hidden">
          <div className="h-full bg-brand-primary rounded-full" style={{ width: `${occupancyPercent}%` }}></div>
        </div>

        <div className="flex justify-between items-center mt-2">
          <span className={`text-[11px] font-semibold px-2 py-0.5 rounded ${getBadgeStyle(facility.current_crowd_level)}`}>
            {facility.current_crowd_level.charAt(0).toUpperCase() + facility.current_crowd_level.slice(1)} Crowd
          </span>
          <span className="text-[11px] text-gray-500">Optimal study time</span>
        </div>
      </div>

      <div className="text-[14px] font-semibold mb-2">Facility Breakdown</div>
      <div className="bg-white border border-gray-200 rounded-lg mb-4">
        <div className="flex justify-between p-3 text-[13px] border-b border-gray-100">
          <span className="text-gray-500">Operating Hours</span>
          <span className="font-medium">{facility.opening_time || '08:00'} – {facility.closing_time || '22:00'}</span>
        </div>
        <div className="flex justify-between p-3 text-[13px] border-b border-gray-100">
          <span className="text-gray-500">Location</span>
          <span className="font-medium">{facility.location || 'Campus Center'}</span>
        </div>
        <div className="flex justify-between p-3 text-[13px] border-b border-gray-100">
          <span className="text-gray-500">Primary Source</span>
          <span className="font-medium">{facility.data_source === 'student_report' ? 'Student Reports + Sensors' : 'Simulated Baseline'}</span>
        </div>
        <div className="flex justify-between p-3 text-[13px]">
          <span className="text-gray-500">Freshness</span>
          <span className="font-medium">Just now</span>
        </div>
      </div>

      {/* Interactive Map View Trigger Button */}
      <button
        onClick={() => setIsMapOpen(true)}
        className="w-full h-[40px] bg-slate-900 text-white rounded font-medium text-[13px] cursor-pointer hover:bg-slate-800 transition-colors mb-4 flex items-center justify-center gap-2 shadow-xs"
      >
        <span>View on Interactive Campus Map</span>
      </button>

      <div className="text-[14px] font-semibold mb-1">Report Current Condition</div>
      <div className="text-[12px] text-gray-500 mb-2.5">Help fellow students verify this data:</div>

      <div className="grid grid-cols-3 gap-2 mb-2.5">
        {['Empty', 'Moderate', 'Packed'].map((pill) => (
          <button
            key={pill}
            onClick={() => setSelectedPill(pill)}
            className={`h-[44px] border rounded text-[13px] font-medium cursor-pointer ${
              selectedPill === pill
                ? 'border-1.5 border-brand-primary bg-brand-light text-brand-primary font-semibold'
                : 'border-gray-300 bg-white text-gray-800'
            }`}
          >
            {pill}
          </button>
        ))}
      </div>

      <button
        onClick={handleReportSubmit}
        disabled={isSubmitting}
        className="w-full h-[44px] border-1.5 border-brand-primary bg-transparent text-brand-primary rounded font-semibold text-[14px] cursor-pointer hover:bg-brand-light transition-colors"
      >
        {submitSuccess ? '✓ Report Recorded. Thank you!' : isSubmitting ? 'Submitting...' : 'Submit Quick Update'}
      </button>

      {/* Campus Map Modal */}
      {isMapOpen && (
        <CampusMapModal facility={facility} onClose={() => setIsMapOpen(false)} />
      )}
    </div>
  )
}
