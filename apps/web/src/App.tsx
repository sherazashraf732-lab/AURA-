import { lazy, Suspense } from 'react'
import { BrowserRouter, Route, Routes } from 'react-router'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from '@/lib/auth'
import { PreferencesProvider } from '@/lib/preferences'
import { AppShell } from '@/layouts/AppShell'
import { LandingPage } from '@/pages/LandingPage'
import { DashboardPage, ModulesPage, NotFoundPage, SettingsPage } from '@/pages/AppPages'
import { ForgotPasswordPage, LoginPage, ResetPasswordPage, SignupPage, VerifyEmailPage } from '@/pages/auth/AuthPages'
import { ApiError } from '@/lib/api'
import { Spinner } from '@/components/ui/card'

// Route-level code splitting keeps the first load small on slow connections.
const ChatPage = lazy(() => import('@/pages/ChatPage').then((m) => ({ default: m.ChatPage })))
const MemoryPage = lazy(() => import('@/pages/MemoryPage').then((m) => ({ default: m.MemoryPage })))
const ProjectsPage = lazy(() => import('@/pages/ProjectsPage').then((m) => ({ default: m.ProjectsPage })))
const Agents = () => import('@/pages/AgentsPages')
const ResearchPage = lazy(() => Agents().then((m) => ({ default: () => <m.NewRunPage kind="research" /> })))
const FactCheckPage = lazy(() => Agents().then((m) => ({ default: () => <m.NewRunPage kind="fact_check" /> })))
const ControlRoomPage = lazy(() => Agents().then((m) => ({ default: m.ControlRoomPage })))
const RunDetailPage = lazy(() => Agents().then((m) => ({ default: m.RunDetailPage })))
const KnowledgePage = lazy(() => import('@/pages/KnowledgePage').then((m) => ({ default: m.KnowledgePage })))
const DocumentsPage = lazy(() => import('@/pages/DocumentsPage').then((m) => ({ default: m.DocumentsPage })))
const DataPage = lazy(() => import('@/pages/DataPage').then((m) => ({ default: m.DataPage })))
const ProjectDetailPage = lazy(() => import('@/pages/ProjectsPage').then((m) => ({ default: m.ProjectDetailPage })))

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (count, err) => !(err instanceof ApiError && err.status < 500) && count < 2,
      refetchOnWindowFocus: false,
    },
  },
})

export function AppRoutes() {
  return (
    <Suspense fallback={<div className="flex h-full items-center justify-center"><Spinner /></div>}>
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />
      <Route path="/verify-email" element={<VerifyEmailPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />
      <Route path="/app" element={<AppShell />}>
        <Route index element={<DashboardPage />} />
        <Route path="settings" element={<SettingsPage />} />
        <Route path="modules" element={<ModulesPage />} />
        <Route path="chat" element={<ChatPage />} />
        <Route path="chat/:conversationId" element={<ChatPage />} />
        <Route path="memory" element={<MemoryPage />} />
        <Route path="projects" element={<ProjectsPage />} />
        <Route path="projects/:projectId" element={<ProjectDetailPage />} />
        <Route path="knowledge" element={<KnowledgePage />} />
        <Route path="documents" element={<DocumentsPage />} />
        <Route path="data" element={<DataPage />} />
        <Route path="research" element={<ResearchPage />} />
        <Route path="fact-check" element={<FactCheckPage />} />
        <Route path="agents" element={<ControlRoomPage />} />
        <Route path="agents/:runId" element={<RunDetailPage />} />
      </Route>
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
    </Suspense>
  )
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <PreferencesProvider>
        <AuthProvider>
          <BrowserRouter>
            <AppRoutes />
          </BrowserRouter>
        </AuthProvider>
      </PreferencesProvider>
    </QueryClientProvider>
  )
}
