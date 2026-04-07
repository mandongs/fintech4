import { useSyncExternalStore } from 'react'

interface AuthState {
  accessToken: string | null
  refreshToken: string | null
}

interface AuthActions {
  setTokens: (access: string, refresh: string) => void
  logout: () => void
}

type FullState = AuthState & AuthActions

const STORAGE_KEY = 'youth-finance-auth'

function getStored(): AuthState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : { accessToken: null, refreshToken: null }
  } catch {
    return { accessToken: null, refreshToken: null }
  }
}

// ── 싱글턴 스토어 ─────────────────────────────────────
let _state: AuthState = getStored()
const _listeners = new Set<() => void>()

function _notify() {
  _listeners.forEach((l) => l())
}

function _setState(partial: Partial<AuthState>) {
  _state = { ..._state, ...partial }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(_state))
  _notify()
}

function _subscribe(listener: () => void) {
  _listeners.add(listener)
  return () => _listeners.delete(listener)
}

function _getSnapshot(): AuthState {
  return _state
}

// ── 액션 ─────────────────────────────────────────────
const actions: AuthActions = {
  setTokens: (access, refresh) =>
    _setState({ accessToken: access, refreshToken: refresh }),
  logout: () =>
    _setState({ accessToken: null, refreshToken: null }),
}

// ── React Hook ────────────────────────────────────────
export function useAuthStore<T>(selector: (s: FullState) => T): T {
  const state = useSyncExternalStore(_subscribe, _getSnapshot)
  return selector({ ...state, ...actions })
}

// non-hook (axios interceptor 등)에서 사용
useAuthStore.getState = (): FullState => ({
  ..._getSnapshot(),
  ...actions,
})
