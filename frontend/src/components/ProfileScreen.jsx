import React, { useState, useEffect } from 'react'

export function ProfileScreen() {
  const [name, setName] = useState(() => localStorage.getItem('campusflow_profile_name') || 'Alex Rivera')
  const [studentId, setStudentId] = useState(() => localStorage.getItem('campusflow_profile_id') || 'CS-2026-4892')
  const [department, setDepartment] = useState(() => localStorage.getItem('campusflow_profile_dept') || 'Computer Science & Engineering')
  const [notificationsEnabled, setNotificationsEnabled] = useState(() => {
    const saved = localStorage.getItem('campusflow_profile_notifs')
    return saved !== null ? JSON.parse(saved) : true
  })
  const [savedStatus, setSavedStatus] = useState(false)
  const [avatarUrl, setAvatarUrl] = useState(() => localStorage.getItem('campusflow_profile_avatar') || null)

  const handleSave = (e) => {
    e.preventDefault()
    localStorage.setItem('campusflow_profile_name', name)
    localStorage.setItem('campusflow_profile_id', studentId)
    localStorage.setItem('campusflow_profile_dept', department)
    localStorage.setItem('campusflow_profile_notifs', JSON.stringify(notificationsEnabled))
    if (avatarUrl) {
      localStorage.setItem('campusflow_profile_avatar', avatarUrl)
    }
    setSavedStatus(true)
    setTimeout(() => setSavedStatus(false), 2500)
  }

  const handleImageUpload = (e) => {
    const file = e.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onloadend = () => {
        const result = reader.result
        setAvatarUrl(result)
        localStorage.setItem('campusflow_profile_avatar', result)
      }
      reader.readAsDataURL(file)
    }
  }

  // Get initials for fallback avatar
  const initials = name
    ? name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    : 'AR'

  return (
    <div className="p-4 overflow-y-auto flex-1 flex flex-col bg-slate-50">
      <div className="mb-4">
        <h1 className="text-[17px] font-semibold text-slate-900 tracking-tight">Student Profile</h1>
        <p className="text-[12px] text-slate-500 mt-0.5">Manage your account and preferences</p>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs flex flex-col gap-4">
        <div className="flex items-center gap-3.5 pb-3 border-b border-slate-100">
          <div className="relative group">
            <div className="w-14 h-14 rounded-full bg-slate-900 text-white font-bold flex items-center justify-center text-[16px] overflow-hidden border-2 border-slate-200">
              {avatarUrl ? (
                <img src={avatarUrl} alt="Profile" className="w-full h-full object-cover" />
              ) : (
                <span>{initials}</span>
              )}
            </div>
            <label className="absolute inset-0 bg-black/40 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer text-white text-[10px] font-medium">
              Edit
              <input type="file" accept="image/*" onChange={handleImageUpload} className="hidden" />
            </label>
          </div>
          <div>
            <div className="text-[14px] font-semibold text-slate-900">{name || 'Student'}</div>
            <div className="text-[12px] text-slate-500">{department}</div>
            <label className="inline-block mt-1 text-[11px] text-brand-primary font-medium cursor-pointer hover:underline">
              Change picture
              <input type="file" accept="image/*" onChange={handleImageUpload} className="hidden" />
            </label>
          </div>
        </div>

        <form onSubmit={handleSave} className="flex flex-col gap-3">
          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1 uppercase tracking-wider">
              Full Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full h-[36px] bg-slate-50 border border-slate-200 rounded-md px-3 text-[12px] text-slate-800 outline-none focus:border-slate-400"
            />
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1 uppercase tracking-wider">
              Student ID
            </label>
            <input
              type="text"
              value={studentId}
              onChange={(e) => setStudentId(e.target.value)}
              className="w-full h-[36px] bg-slate-50 border border-slate-200 rounded-md px-3 text-[12px] text-slate-800 outline-none focus:border-slate-400"
            />
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1 uppercase tracking-wider">
              Department / Major
            </label>
            <input
              type="text"
              value={department}
              onChange={(e) => setDepartment(e.target.value)}
              className="w-full h-[36px] bg-slate-50 border border-slate-200 rounded-md px-3 text-[12px] text-slate-800 outline-none focus:border-slate-400"
            />
          </div>

          <div className="flex items-center justify-between pt-2">
            <span className="text-[12px] font-medium text-slate-700">Push Notifications for Rush Alerts</span>
            <input
              type="checkbox"
              checked={notificationsEnabled}
              onChange={(e) => setNotificationsEnabled(e.target.checked)}
              className="w-4 h-4 accent-slate-900 cursor-pointer"
            />
          </div>

          <button
            type="submit"
            className="mt-2 w-full h-[38px] bg-slate-900 text-white rounded-md text-[13px] font-medium cursor-pointer hover:bg-slate-800 transition-colors"
          >
            Save Profile & Preferences
          </button>

          {savedStatus && (
            <div className="text-center text-[12px] text-emerald-600 font-medium animate-pulse">
              Profile updated and saved successfully!
            </div>
          )}
        </form>
      </div>
    </div>
  )
}
