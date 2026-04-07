import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import styled from 'styled-components'
import toast from 'react-hot-toast'
import dayjs from 'dayjs'
import { apiClient } from '../../../common/api/client'
import { theme } from '../../../common/styles/GlobalStyle'
import { FiBell, FiTrash2, FiExternalLink } from 'react-icons/fi'

interface Bookmark {
  id: string
  policy_id: string
  policy_name: string
  notify_enabled: boolean
  created_at: string
  days_left: number | null
}

function DaysBadge({ days }: { days: number | null }) {
  if (days === null) return <Badge $c="#10B981" $bg="#F0FDF4">상시</Badge>
  if (days < 0) return <Badge $c="#94A3B8" $bg="#F1F5F9">마감</Badge>
  if (days === 0) return <Badge $c="#EF4444" $bg="#FEE2E2">D-DAY</Badge>
  if (days <= 3) return <Badge $c="#EF4444" $bg="#FEE2E2">D-{days} 🔴</Badge>
  if (days <= 7) return <Badge $c="#D97706" $bg="#FEF9C3">D-{days} 🟡</Badge>
  return <Badge $c="#4F46E5" $bg="#EEF2FF">D-{days}</Badge>
}

export function AlertPage() {
  const qc = useQueryClient()

  const { data: bookmarks = [], isLoading } = useQuery<Bookmark[]>({
    queryKey: ['bookmarks'],
    queryFn: () => apiClient.get('/bookmarks').then((r) => r.data),
  })

  const { data: alerts = [] } = useQuery({
    queryKey: ['alerts'],
    queryFn: () => apiClient.get('/alerts?days=30').then((r) => r.data),
  })

  const removeMutation = useMutation({
    mutationFn: (policy_id: string) => apiClient.delete(`/bookmarks/${policy_id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['bookmarks'] })
      toast.success('북마크가 해제되었습니다.')
    },
  })

  const urgentAlerts = alerts.filter((a: any) => a.days_left !== null && a.days_left <= 7)

  return (
    <Page>
      <Header>
        <h1>D-day 알림</h1>
        <p>마감 임박 정책과 내 북마크를 한 곳에서 관리하세요.</p>
      </Header>

      {urgentAlerts.length > 0 && (
        <Section>
          <SectionTitle $urgent>🚨 마감 7일 이내</SectionTitle>
          {urgentAlerts.map((a: any) => (
            <AlertCard key={a.id} $urgent>
              <AlertLeft>
                <DaysBadge days={a.days_left} />
                <AlertName>{a.name}</AlertName>
              </AlertLeft>
              <AlertRight>
                <AlertDate>{a.apply_end ? dayjs(a.apply_end).format('MM/DD 마감') : ''}</AlertDate>
                {a.apply_url && a.apply_url !== 'nan' && a.apply_url.startsWith('http') && (
                  <a href={a.apply_url} target="_blank" rel="noreferrer">
                    <FiExternalLink size={14} />
                  </a>
                )}
              </AlertRight>
            </AlertCard>
          ))}
        </Section>
      )}

      <Section>
        <SectionTitle>
          <FiBell />
          내 북마크 ({bookmarks.length})
        </SectionTitle>
        {isLoading && <Empty>불러오는 중...</Empty>}
        {!isLoading && bookmarks.length === 0 && (
          <Empty>북마크한 정책이 없습니다. 추천 탭에서 관심 정책을 저장해보세요!</Empty>
        )}
        {bookmarks.map((bm) => (
          <BookmarkCard key={bm.id}>
            <BmLeft>
              <DaysBadge days={bm.days_left} />
              <BmName>{bm.policy_name}</BmName>
            </BmLeft>
            <BmRight>
              <BmDate>저장일 {dayjs(bm.created_at).format('MM.DD')}</BmDate>
              <DeleteBtn onClick={() => removeMutation.mutate(bm.policy_id)} title="북마크 해제">
                <FiTrash2 size={14} />
              </DeleteBtn>
            </BmRight>
          </BookmarkCard>
        ))}
      </Section>
    </Page>
  )
}

const Page = styled.div``
const Header = styled.div`
  margin-bottom: 24px;
  h1 { font-size: 22px; font-weight: 700; margin-bottom: 4px; }
  p { color: ${theme.colors.textSecondary}; font-size: 14px; }
`
const Section = styled.div`
  background: ${theme.colors.surface}; border: 1px solid ${theme.colors.border};
  border-radius: ${theme.radius.md}; padding: 20px; margin-bottom: 16px;
`
const SectionTitle = styled.h2<{ $urgent?: boolean }>`
  display: flex; align-items: center; gap: 8px; font-size: 15px; font-weight: 600;
  margin-bottom: 16px; color: ${(p) => p.$urgent ? theme.colors.danger : theme.colors.textPrimary};
`
const Badge = styled.span<{ $c: string; $bg: string }>`
  padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 700;
  color: ${(p) => p.$c}; background: ${(p) => p.$bg}; white-space: nowrap;
`
const AlertCard = styled.div<{ $urgent?: boolean }>`
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 16px; border-radius: ${theme.radius.sm}; margin-bottom: 8px;
  background: ${(p) => p.$urgent ? '#FFF5F5' : '#F8FAFC'};
  border: 1px solid ${(p) => p.$urgent ? '#FECACA' : theme.colors.border};
`
const AlertLeft = styled.div`display: flex; align-items: center; gap: 10px;`
const AlertName = styled.span`font-size: 14px; font-weight: 500;`
const AlertRight = styled.div`display: flex; align-items: center; gap: 8px; color: ${theme.colors.textMuted};`
const AlertDate = styled.span`font-size: 12px;`

const BookmarkCard = styled.div`
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 16px; border-radius: ${theme.radius.sm}; margin-bottom: 8px;
  border: 1px solid ${theme.colors.border};
  &:hover { background: #F8FAFC; }
`
const BmLeft = styled.div`display: flex; align-items: center; gap: 10px;`
const BmName = styled.span`font-size: 14px; font-weight: 500;`
const BmRight = styled.div`display: flex; align-items: center; gap: 10px;`
const BmDate = styled.span`font-size: 12px; color: ${theme.colors.textMuted};`
const DeleteBtn = styled.button`
  color: ${theme.colors.textMuted}; display: flex; align-items: center;
  &:hover { color: ${theme.colors.danger}; }
`
const Empty = styled.p`color: ${theme.colors.textMuted}; font-size: 14px; padding: 16px 0;`
