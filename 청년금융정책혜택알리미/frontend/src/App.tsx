import { Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from './common/components/Layout'
import { useAuthStore } from './domains/auth/store/authStore'
import { LoginPage } from './domains/auth/pages/LoginPage'
import { RegisterPage } from './domains/auth/pages/RegisterPage'
import { ProfilePage } from './domains/profile/pages/ProfilePage'
import { RecommendPage } from './domains/policy/pages/RecommendPage'
import { PolicyDetailPage } from './domains/policy/pages/PolicyDetailPage'
import { AlertPage } from './domains/policy/pages/AlertPage'
import { FinancialPage } from './domains/financial/pages/FinancialPage'
import { ChatPage } from './domains/chat/pages/ChatPage'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const token = useAuthStore((s) => s.accessToken)
  return token ? <>{children}</> : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route
        path="/"
        element={
          <PrivateRoute>
            <Layout />
          </PrivateRoute>
        }
      >
        <Route index element={<Navigate to="/recommend" replace />} />
        <Route path="recommend" element={<RecommendPage />} />
        <Route path="policies/:id" element={<PolicyDetailPage />} />
        <Route path="alerts" element={<AlertPage />} />
        <Route path="financial" element={<FinancialPage />} />
        <Route path="chat" element={<ChatPage />} />
        <Route path="profile" element={<ProfilePage />} />
      </Route>
    </Routes>
  )
}
