import { useEffect, useState } from 'react'

interface HealthStatus {
  status: string
  environment: string
  version: string
}

function App() {
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch('http://localhost:8000/health')
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }
        const data = await response.json()
        setHealth(data)
        setError(null)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to connect')
        setHealth(null)
      } finally {
        setLoading(false)
      }
    }

    checkHealth()
    const interval = setInterval(checkHealth, 30000) // Check every 30s
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8">
      <div className="max-w-md w-full">
        <h1 className="text-4xl font-bold text-center mb-8">
          Perplex Engine
        </h1>

        <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
          <h2 className="text-xl font-semibold mb-4">Backend Status</h2>

          {loading && (
            <div className="flex items-center gap-2 text-gray-400">
              <div className="animate-spin h-5 w-5 border-2 border-gray-400 border-t-transparent rounded-full"></div>
              <span>Checking connection...</span>
            </div>
          )}

          {!loading && error && (
            <div className="bg-red-900/50 border border-red-700 rounded-lg p-4">
              <div className="flex items-center gap-2">
                <span className="h-3 w-3 bg-red-500 rounded-full"></span>
                <span className="font-medium text-red-400">Disconnected</span>
              </div>
              <p className="text-sm text-gray-400 mt-2">
                Error: {error}
              </p>
              <p className="text-sm text-gray-500 mt-1">
                Make sure the backend is running on port 8000
              </p>
            </div>
          )}

          {!loading && health && (
            <div className="bg-green-900/50 border border-green-700 rounded-lg p-4">
              <div className="flex items-center gap-2">
                <span className="h-3 w-3 bg-green-500 rounded-full animate-pulse"></span>
                <span className="font-medium text-green-400">Connected</span>
              </div>
              <div className="mt-3 space-y-1 text-sm">
                <p>
                  <span className="text-gray-400">Status:</span>{' '}
                  <span className="text-white">{health.status}</span>
                </p>
                <p>
                  <span className="text-gray-400">Environment:</span>{' '}
                  <span className="text-white">{health.environment}</span>
                </p>
                <p>
                  <span className="text-gray-400">Version:</span>{' '}
                  <span className="text-white">{health.version}</span>
                </p>
              </div>
            </div>
          )}
        </div>

        <p className="text-center text-gray-500 text-sm mt-6">
          Sports betting analytics platform
        </p>
      </div>
    </div>
  )
}

export default App
