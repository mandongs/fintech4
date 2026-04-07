import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import styled from 'styled-components'
import { theme } from '../styles/GlobalStyle'
import { useAuthStore } from '../../domains/auth/store/authStore'
import { FiBell, FiCreditCard, FiHome, FiMessageSquare, FiUser, FiLogOut } from 'react-icons/fi'

const NAV_ITEMS = [
  { to: '/recommend', label: '맞춤추천', icon: <FiHome /> },
  { to: '/alerts', label: 'D-day 알림', icon: <FiBell /> },
  { to: '/financial', label: '금융상품', icon: <FiCreditCard /> },
  { to: '/chat', label: 'AI 상담', icon: <FiMessageSquare /> },
  { to: '/profile', label: '내 프로필', icon: <FiUser /> },
]

export function Layout() {
  const logout = useAuthStore((s) => s.logout)
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <Wrapper>
      <Sidebar>
        <Logo>
          <span>💰</span>
          <span>청년혜택</span>
        </Logo>
        <Nav>
          {NAV_ITEMS.map(({ to, label, icon }) => (
            <NavItem key={to} to={to}>
              {icon}
              <span>{label}</span>
            </NavItem>
          ))}
        </Nav>
        <LogoutBtn onClick={handleLogout}>
          <FiLogOut />
          <span>로그아웃</span>
        </LogoutBtn>
      </Sidebar>
      <Main>
        <Outlet />
      </Main>
    </Wrapper>
  )
}

const Wrapper = styled.div`
  display: flex;
  min-height: 100vh;
`

const Sidebar = styled.aside`
  width: 220px;
  background: ${theme.colors.surface};
  border-right: 1px solid ${theme.colors.border};
  display: flex;
  flex-direction: column;
  padding: 24px 16px;
  position: fixed;
  top: 0; left: 0; bottom: 0;
`

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 700;
  color: ${theme.colors.primary};
  margin-bottom: 32px;
  padding: 0 8px;
`

const Nav = styled.nav`
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
`

const NavItem = styled(NavLink)`
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: ${theme.radius.sm};
  color: ${theme.colors.textSecondary};
  font-size: 14px;
  font-weight: 500;
  transition: all 0.15s;

  svg { font-size: 18px; flex-shrink: 0; }

  &:hover {
    background: #F1F5FE;
    color: ${theme.colors.primary};
  }
  &.active {
    background: #EEF2FF;
    color: ${theme.colors.primary};
    font-weight: 600;
  }
`

const LogoutBtn = styled.button`
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: ${theme.radius.sm};
  color: ${theme.colors.textMuted};
  font-size: 14px;
  width: 100%;
  transition: all 0.15s;

  &:hover {
    background: #FEF2F2;
    color: ${theme.colors.danger};
  }
`

const Main = styled.main`
  margin-left: 220px;
  flex: 1;
  padding: 32px;
  max-width: 1100px;
`
