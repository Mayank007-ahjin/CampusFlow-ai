import React, { useState, useEffect } from 'react'
import { Header, BottomNav } from './components/Navigation'
import { HomeScreen } from './components/HomeScreen'
import { DetailScreen } from './components/DetailScreen'
import { ChatScreen } from './components/ChatScreen'
import { RoutePlannerScreen } from './components/RoutePlannerScreen'
import { ProfileScreen } from './components/ProfileScreen'
import { facilityService, reportService, recommendationService } from './services/api'

export default function App() {
  const [currentScreen, setCurrentScreen] = useState('home')
  const [facilities, setFacilities] = useState([])
  const [selectedFacility, setSelectedFacility] = useState(null)
  const [messages, setMessages] = useState([
    {
      sender: 'assistant',
      text: 'Hey there! I am your CampusFlow AI assistant. I can help you check live crowd levels, find available library seats, track canteen wait times, or plan the fastest route across campus. What would you like to check today?'
    }
  ])
  const [chatInput, setChatInput] = useState('')

  // Load facilities on mount
  useEffect(() => {
    loadFacilities()
  }, [])

  const loadFacilities = async () => {
    try {
      const data = await facilityService.getFacilities()
      setFacilities(data.facilities)
      if (data.facilities.length > 0 && !selectedFacility) {
        setSelectedFacility(data.facilities[0])
      }
    } catch (err) {
      console.error('Failed to load facilities:', err)
      // Fallback mock data if backend isn't running yet
      setFacilities([
        {
          id: 1,
          name: 'Central Library',
          type: 'library',
          location: 'Building A, Ground Floor',
          opening_time: '08:00',
          closing_time: '22:00',
          current_crowd_level: 'low',
          available_seats: 42,
          total_capacity: 120,
          data_source: 'student_report'
        },
        {
          id: 2,
          name: 'Main Canteen',
          type: 'canteen',
          location: 'Building B, First Floor',
          opening_time: '07:30',
          closing_time: '21:00',
          current_crowd_level: 'high',
          estimated_wait_minutes: 18,
          data_source: 'historical'
        },
        {
          id: 3,
          name: 'Stationery & Print Shop',
          type: 'stationery',
          location: 'Building C, Ground Floor',
          opening_time: '09:00',
          closing_time: '18:00',
          current_crowd_level: 'moderate',
          estimated_wait_minutes: 4,
          data_source: 'student_report'
        }
      ])
      setSelectedFacility({
        id: 1,
        name: 'Central Library',
        type: 'library',
        location: 'Building A, Ground Floor',
        opening_time: '08:00',
        closing_time: '22:00',
        current_crowd_level: 'low',
        available_seats: 42,
        total_capacity: 120,
        data_source: 'student_report'
      })
    }
  }

  const handleSelectFacility = (facility) => {
    setSelectedFacility(facility)
    setCurrentScreen('detail')
  }

  const handleSubmitReport = async (reportData) => {
    try {
      await reportService.submitReport(reportData)
      await loadFacilities()
    } catch (err) {
      console.error('Failed to submit report:', err)
    }
  }

  const handleSendMessage = async (queryText) => {
    if (!queryText.trim()) return

    const newMessages = [...messages, { sender: 'user', text: queryText }]
    setMessages(newMessages)
    setChatInput('')

    // Add temporary "thinking" message
    const thinkingMessages = [...newMessages, { sender: 'assistant', text: 'CampusFlow AI is thinking...', isThinking: true }]
    setMessages(thinkingMessages)

    try {
      // Ensure at least 2.0s delay so the thinking state feels like a thoughtful agent
      const startTime = Date.now()

      const isRouteQuery = queryText.toLowerCase().includes('route') || queryText.toLowerCase().includes('plan')
      const response = isRouteQuery
        ? await recommendationService.planRoute(queryText)
        : await recommendationService.getRecommendations(queryText)

      const elapsed = Date.now() - startTime
      if (elapsed < 2000) {
        await new Promise(resolve => setTimeout(resolve, 2000 - elapsed))
      }

      const topRec = response.recommendations?.[0]

      setMessages([
        ...newMessages,
        {
          sender: 'assistant',
          text: response.answer,
          recommendation: topRec ? {
            facility_name: topRec.facility_name,
            reason: topRec.reason
          } : null
        }
      ])
    } catch (err) {
      console.error('Failed to get recommendation/route:', err)
      setMessages([
        ...newMessages,
        {
          sender: 'assistant',
          text: 'Could not reach the CampusFlow server. Make sure the backend is running on port 8001 and try again.'
        }
      ])
    }
  }

  return (
    <div className="bg-[#E5E7EB] min-h-screen flex flex-col items-center py-6 px-4">
      {/* Mobile Container Frame */}
      <div className="w-full max-w-[380px] h-[740px] bg-white rounded-[28px] border-[6px] border-[#1F2937] overflow-hidden flex flex-col relative shadow-xl">

        <Header currentScreen={currentScreen} onNavigate={setCurrentScreen} onBack={() => setCurrentScreen('home')} />

        <div className="flex-1 overflow-y-auto bg-gray-50 flex flex-col">
          {currentScreen === 'home' && (
            <HomeScreen facilities={facilities} onSelectFacility={handleSelectFacility} />
          )}
          {currentScreen === 'detail' && (
            <DetailScreen facility={selectedFacility} onSubmitReport={handleSubmitReport} />
          )}
          {currentScreen === 'route' && (
            <RoutePlannerScreen facilities={facilities} />
          )}
          {currentScreen === 'chat' && (
            <ChatScreen
              messages={messages}
              onSendMessage={handleSendMessage}
              inputQuery={chatInput}
              setInputQuery={setChatInput}
            />
          )}
          {currentScreen === 'profile' && (
            <ProfileScreen />
          )}
        </div>

        {currentScreen === 'chat' && (
          <div className="bg-white border-t border-gray-200 p-3 flex gap-2 items-center flex-shrink-0">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSendMessage(chatInput)}
              placeholder="Ask about wait times, seats..."
              className="flex-1 h-[42px] border border-gray-300 rounded px-3 text-[14px] outline-none bg-gray-50 focus:border-brand-primary"
            />
            <button
              onClick={() => handleSendMessage(chatInput)}
              className="w-[42px] h-[42px] bg-brand-primary border-none rounded text-white cursor-pointer flex items-center justify-center font-bold text-[16px]"
            >
              →
            </button>
          </div>
        )}

        <BottomNav currentScreen={currentScreen} onNavigate={setCurrentScreen} />
      </div>
    </div>
  )
}
