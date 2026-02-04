import { StrictMode, ReactNode } from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { ClerkProvider } from '@clerk/clerk-react'
import { AuthProvider } from './context/AuthContext'
import './index.css'
import App from './App.tsx'

// Clerk publishable key from environment
const CLERK_PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY || ''

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30 * 1000, // 30 seconds
      refetchOnWindowFocus: false,
      retry: 2,
    },
  },
})

// Wrapper that only uses Clerk if configured
function AuthWrapper({ children }: { children: ReactNode }) {
  if (CLERK_PUBLISHABLE_KEY) {
    return (
      <ClerkProvider publishableKey={CLERK_PUBLISHABLE_KEY}>
        <AuthProvider clerkEnabled>{children}</AuthProvider>
      </ClerkProvider>
    )
  }
  // No Clerk key - run without auth
  return <AuthProvider clerkEnabled={false}>{children}</AuthProvider>
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthWrapper>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </QueryClientProvider>
    </AuthWrapper>
  </StrictMode>,
)
