import type { LucideIcon } from 'lucide-react'
import {
  Activity,
  BarChart3,
  Bot,
  BookOpen,
  Brain,
  CheckCheck,
  Code2,
  FileText,
  FlaskConical,
  Gauge,
  GitBranch,
  Image,
  LayoutDashboard,
  Mic,
  Network,
  Plug,
  ScanText,
  Search,
  Settings,
  Shield,
  Swords,
  Timer,
  Users,
  MessagesSquare,
  FolderKanban,
} from 'lucide-react'

export type ModuleStatus = 'live' | 'planned'

export interface ModuleInfo {
  id: string
  name: string
  path: string
  icon: LucideIcon
  status: ModuleStatus
  phase: number
  adminOnly?: boolean
  summary: string
}

/**
 * Single source of truth for navigation. Only `live` modules appear in the sidebar; planned ones are
 * listed honestly on the Modules page with their roadmap phase (no dead buttons).
 */
export const MODULES: ModuleInfo[] = [
  { id: 'dashboard', name: 'Dashboard', path: '/app', icon: LayoutDashboard, status: 'live', phase: 3, summary: 'Overview of your workspace and usage.' },
  { id: 'chat', name: 'Chat', path: '/app/chat', icon: MessagesSquare, status: 'live', phase: 6, summary: 'Universal assistant with multiple model providers.' },
  { id: 'projects', name: 'Projects', path: '/app/projects', icon: FolderKanban, status: 'live', phase: 7, summary: 'Group chats, files and instructions; resume work later (A1).' },
  { id: 'memory', name: 'Memory', path: '/app/memory', icon: Brain, status: 'live', phase: 7, summary: 'View, edit, disable and delete what AURA remembers (A2).' },
  { id: 'research', name: 'AI Research', path: '/app/research', icon: Search, status: 'live', phase: 8, summary: 'Planned research with cited sources (M01).' },
  { id: 'agents', name: 'Agent Control Room', path: '/app/agents', icon: Bot, status: 'live', phase: 8, summary: 'Live view of agent steps, tools and approvals (M03, A3).' },
  { id: 'factcheck', name: 'Fact Checker', path: '/app/fact-check', icon: CheckCheck, status: 'live', phase: 9, summary: 'Supporting and contradicting evidence for claims (M02).' },
  { id: 'knowledge', name: 'Knowledge Base', path: '/app/knowledge', icon: BookOpen, status: 'live', phase: 9, summary: 'Upload documents and get cited answers (M05).' },
  { id: 'documents', name: 'Document Studio', path: '/app/documents', icon: FileText, status: 'live', phase: 10, summary: 'Editable DOCX, PPTX, XLSX and PDF output (M06).' },
  { id: 'data', name: 'Data Studio', path: '/app/data', icon: BarChart3, status: 'live', phase: 11, summary: 'CSV/XLSX analysis and charts (M07).' },
  { id: 'coding', name: 'Coding Lab', path: '/app/coding', icon: Code2, status: 'live', phase: 12, summary: 'Code explanation, review and tests; execution disabled in beta (M11).' },
  { id: 'workflows', name: 'Workflows', path: '/app/workflows', icon: GitBranch, status: 'live', phase: 12, summary: 'Visual workflows with approvals (M12, M13).' },
  { id: 'mcp', name: 'Integrations (MCP)', path: '/app/integrations', icon: Plug, status: 'planned', phase: 13, summary: 'Permissioned tool integrations (M14).' },
  { id: 'ocr', name: 'OCR', path: '/app/ocr', icon: ScanText, status: 'planned', phase: 13, summary: 'Text extraction from images and scans (M08).' },
  { id: 'audio', name: 'Audio', path: '/app/audio', icon: Mic, status: 'planned', phase: 13, summary: 'Transcription of uploaded audio (M09).' },
  { id: 'vision', name: 'Vision', path: '/app/vision', icon: Image, status: 'planned', phase: 13, summary: 'Image understanding (M10).' },
  { id: 'graph', name: 'Knowledge Graph', path: '/app/graph', icon: Network, status: 'planned', phase: 13, summary: 'Entities and relationships with provenance (M15).' },
  { id: 'arena', name: 'Model Arena', path: '/app/arena', icon: Swords, status: 'planned', phase: 13, summary: 'Side-by-side model comparison (A4).' },
  { id: 'evaluation', name: 'Evaluation Center', path: '/app/evaluation', icon: FlaskConical, status: 'planned', phase: 13, summary: 'Repeatable quality and regression tests (M20, A5).' },
  { id: 'automation', name: 'Automation', path: '/app/automation', icon: Timer, status: 'planned', phase: 12, summary: 'Schedules and task history (M13).' },
  { id: 'usage', name: 'Usage', path: '/app/usage', icon: Gauge, status: 'planned', phase: 6, summary: 'Your quotas and provider usage (M18).' },
  { id: 'security', name: 'Security Center', path: '/app/security', icon: Shield, status: 'planned', phase: 13, summary: 'Sessions, data export and deletion (M19).' },
  { id: 'settings', name: 'Settings', path: '/app/settings', icon: Settings, status: 'live', phase: 3, summary: 'Appearance, language and memory preferences.' },
  { id: 'admin', name: 'Admin', path: '/app/admin', icon: Users, status: 'planned', phase: 14, adminOnly: true, summary: 'Users, moderation, quotas and service health (M17).' },
  { id: 'modules', name: 'All modules', path: '/app/modules', icon: Activity, status: 'live', phase: 3, summary: 'Status of every AURA module.' },
]
