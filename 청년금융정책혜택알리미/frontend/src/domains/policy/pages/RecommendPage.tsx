import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import styled from 'styled-components'
import toast from 'react-hot-toast'
import dayjs from 'dayjs'
import { apiClient } from '../../../common/api/client'
import { theme } from '../../../common/styles/GlobalStyle'
import { FiBookmark, FiExternalLink, FiClock } from 'react-icons/fi'

interface Policy {
  id: string
  name: string
  category_main: string | null
  category_sub: string | null
  description: string | null
  apply_url: string | null
  apply_end: string | null
  apply_period_text: string | null
  supervise_inst: string | null
  days_left: number | null
  match_score: number | null
}

function DeadlineBadge({ days }: { days: number | null }) {
  if (days === null) return <Badge $type="normal">상시</Badge>
  if (days < 0) return <Badge $type="closed">마감</Badge>
  if (days === 0) return <Badge $type="urgent">D-DAY</Badge>
  if (days <= 3) return <Badge $type="urgent">D-{days}</Badge>
  if (days <= 7) return <Badge $type="soon">D-{days}</Badge>
  return <Badge $type="normal">D-{days}</Badge>
}

function MatchBar({ score }: { score: number | null }) {
  if (score === null) return null
  const pct = Math.round(score * 100)
  return (
    <MatchWrap>
      <MatchLabel>매칭 {pct}%</MatchLabel>
      <MatchTrack><MatchFill $pct={pct} /></MatchTrack>
    </MatchWrap>
  )
}

export function RecommendPage() {
  const navigate = useNavigate()
  const qc = useQueryClient()

  const { data, isLoading, isError } = useQuery<{ total: number; items: Policy[] }>({
    queryKey: ['recommend', 'policies'],
    queryFn: () => apiClient.get('/recommend/policies').then((r) => r.data),
    retry: false,
  })

  const bookmarkMutation = useMutation({
    mutationFn: (id: string) => apiClient.post(`/bookmarks/${id}`),
    onSuccess: () => {
      toast.success('북마크에 추가되었습니다!')
      qc.invalidateQueries({ queryKey: ['bookmarks'] })
    },
    onError: () => toast.error('북마크 추가에 실패했습니다.'),
  })

  if (isLoading) return <Loading>맞춤 정책을 분석하는 중...</Loading>

  if (isError) return (
    <EmptyState>
      <p>🙋 프로필을 먼저 등록해야 맞춤 추천이 가능해요.</p>
      <GoProfileBtn onClick={() => navigate('/profile')}>프로필 등록하러 가기 →</GoProfileBtn>
    </EmptyState>
  )

  return (
    <Page>
      <Header>
        <div>
          <h1>맞춤 정책 추천</h1>
          <p>내 조건에 맞는 청년 정책 {data?.total ?? 0}개를 찾았어요.</p>
        </div>
      </Header>

      <Grid>
        {data?.items.map((p) => (
          <Card key={p.id} onClick={() => navigate(`/policies/${p.id}`)}>
            <CardTop>
              <TagRow>
                {p.category_main && <Tag>{p.category_main}</Tag>}
                {p.category_sub && <Tag $sub>{p.category_sub}</Tag>}
              </TagRow>
              <DeadlineBadge days={p.days_left} />
            </CardTop>

            <CardName>{p.name}</CardName>
            {p.description && <CardDesc>{p.description.slice(0, 80)}...</CardDesc>}

            <MatchBar score={p.match_score} />

            <CardFooter>
              <Inst>{p.supervise_inst ?? ''}</Inst>
              <Actions onClick={(e) => e.stopPropagation()}>
                {p.apply_url && p.apply_url !== 'nan' && p.apply_url.startsWith('http') && (
                  <IconBtn as="a" href={p.apply_url} target="_blank" rel="noreferrer" title="신청 바로가기">
                    <FiExternalLink />
                  </IconBtn>
                )}
                <IconBtn
                  onClick={() => bookmarkMutation.mutate(p.id)}
                  title="북마크"
                >
                  <FiBookmark />
                </IconBtn>
              </Actions>
            </CardFooter>

            {p.apply_end && (
              <Deadline>
                <FiClock size={12} />
                {dayjs(p.apply_end).format('YYYY.MM.DD')} 마감
              </Deadline>
            )}
            {!p.apply_end && p.apply_period_text && (
              <Deadline><FiClock size={12} /> {p.apply_period_text}</Deadline>
            )}
          </Card>
        ))}
      </Grid>
    </Page>
  )
}

const Page = styled.div``
const Header = styled.div`
  display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px;
  h1 { font-size: 22px; font-weight: 700; margin-bottom: 4px; }
  p { color: ${theme.colors.textSecondary}; font-size: 14px; }
`
const Grid = styled.div`display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px;`
const Card = styled.div`
  background: ${theme.colors.surface}; border: 1px solid ${theme.colors.border};
  border-radius: ${theme.radius.md}; padding: 20px; cursor: pointer;
  transition: all 0.15s; display: flex; flex-direction: column; gap: 10px;
  &:hover { box-shadow: ${theme.shadow.md}; transform: translateY(-2px); border-color: ${theme.colors.primaryLight}; }
`
const CardTop = styled.div`display: flex; justify-content: space-between; align-items: flex-start;`
const TagRow = styled.div`display: flex; gap: 6px; flex-wrap: wrap;`
const Tag = styled.span<{ $sub?: boolean }>`
  padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 500;
  background: ${(p) => p.$sub ? '#F1F5F9' : '#EEF2FF'};
  color: ${(p) => p.$sub ? theme.colors.textSecondary : theme.colors.primary};
`
const Badge = styled.span<{ $type: 'urgent' | 'soon' | 'normal' | 'closed' }>`
  padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; white-space: nowrap;
  background: ${(p) => ({ urgent: '#FEE2E2', soon: '#FEF9C3', normal: '#F0FDF4', closed: '#F1F5F9' }[p.$type])};
  color: ${(p) => ({ urgent: theme.colors.danger, soon: '#D97706', normal: theme.colors.success, closed: theme.colors.textMuted }[p.$type])};
`
const CardName = styled.h3`font-size: 15px; font-weight: 600; line-height: 1.4;`
const CardDesc = styled.p`font-size: 13px; color: ${theme.colors.textSecondary}; line-height: 1.5;`
const CardFooter = styled.div`display: flex; justify-content: space-between; align-items: center; margin-top: 4px;`
const Inst = styled.span`font-size: 12px; color: ${theme.colors.textMuted};`
const Actions = styled.div`display: flex; gap: 6px;`
const IconBtn = styled.button`
  display: flex; align-items: center; justify-content: center;
  width: 30px; height: 30px; border-radius: 6px;
  color: ${theme.colors.textSecondary}; transition: all 0.15s;
  &:hover { background: #EEF2FF; color: ${theme.colors.primary}; }
`
const Deadline = styled.div`
  display: flex; align-items: center; gap: 4px;
  font-size: 12px; color: ${theme.colors.textMuted};
`
const MatchWrap = styled.div`display: flex; align-items: center; gap: 8px;`
const MatchLabel = styled.span`font-size: 12px; font-weight: 600; color: ${theme.colors.primary}; white-space: nowrap;`
const MatchTrack = styled.div`flex: 1; height: 4px; background: #E2E8F0; border-radius: 2px; overflow: hidden;`
const MatchFill = styled.div<{ $pct: number }>`
  height: 100%; width: ${(p) => p.$pct}%; background: ${theme.colors.primary}; border-radius: 2px;
`
const Loading = styled.div`padding: 60px; text-align: center; color: ${theme.colors.textSecondary};`
const EmptyState = styled.div`
  padding: 60px 24px; text-align: center;
  p { font-size: 16px; color: ${theme.colors.textSecondary}; margin-bottom: 16px; }
`
const GoProfileBtn = styled.button`
  padding: 12px 24px; background: ${theme.colors.primary}; color: white;
  border-radius: ${theme.radius.sm}; font-size: 14px; font-weight: 600;
  &:hover { background: ${theme.colors.primaryDark}; }
`
