import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import styled from 'styled-components'
import toast from 'react-hot-toast'
import dayjs from 'dayjs'
import { apiClient } from '../../../common/api/client'
import { theme } from '../../../common/styles/GlobalStyle'
import { FiArrowLeft, FiBookmark, FiExternalLink } from 'react-icons/fi'

export function PolicyDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const qc = useQueryClient()

  const { data: policy, isLoading } = useQuery({
    queryKey: ['policy', id],
    queryFn: () => apiClient.get(`/policies/${id}`).then((r) => r.data),
    enabled: !!id,
  })

  const bookmarkMutation = useMutation({
    mutationFn: () => apiClient.post(`/bookmarks/${id}`),
    onSuccess: () => {
      toast.success('북마크에 추가되었습니다!')
      qc.invalidateQueries({ queryKey: ['bookmarks'] })
    },
  })

  if (isLoading) return <Loading>정책 정보를 불러오는 중...</Loading>
  if (!policy) return <Loading>정책을 찾을 수 없습니다.</Loading>

  return (
    <Page>
      <BackBtn onClick={() => navigate(-1)}><FiArrowLeft /> 목록으로</BackBtn>

      <Card>
        <Top>
          <TagRow>
            {policy.category_main && <Tag>{policy.category_main}</Tag>}
            {policy.category_sub && <Tag $sub>{policy.category_sub}</Tag>}
          </TagRow>
          <BtnRow>
            {policy.apply_url && policy.apply_url !== 'nan' && policy.apply_url.startsWith('http') && (
              <ApplyBtn as="a" href={policy.apply_url} target="_blank" rel="noreferrer">
                <FiExternalLink /> 신청하기
              </ApplyBtn>
            )}
            <BookmarkBtn onClick={() => bookmarkMutation.mutate()}>
              <FiBookmark /> 북마크
            </BookmarkBtn>
          </BtnRow>
        </Top>

        <PolicyName>{policy.name}</PolicyName>
        {policy.supervise_inst && <InstName>{policy.supervise_inst}</InstName>}

        <InfoGrid>
          <InfoItem label="신청 기간" value={
            policy.apply_end
              ? `${policy.apply_start ? dayjs(policy.apply_start).format('YYYY.MM.DD') + ' ~ ' : ''}${dayjs(policy.apply_end).format('YYYY.MM.DD')}`
              : (policy.apply_period_text ?? '상시')
          } />
          <InfoItem label="마감까지" value={
            policy.days_left === null ? '상시' :
            policy.days_left < 0 ? '마감됨' :
            `D-${policy.days_left}`
          } />
          <InfoItem label="지원 나이" value={
            policy.min_age || policy.max_age
              ? `${policy.min_age || '제한없음'}세 ~ ${policy.max_age || '제한없음'}세`
              : '제한 없음'
          } />
          <InfoItem label="소득 조건" value={
            policy.earn_min || policy.earn_max
              ? `연 ${policy.earn_min || 0}만원 ~ ${policy.earn_max || '제한없음'}만원`
              : '제한 없음'
          } />
        </InfoGrid>

        {policy.description && (
          <Block>
            <BlockTitle>정책 설명</BlockTitle>
            <BlockText>{policy.description}</BlockText>
          </Block>
        )}

        {policy.support_content && (
          <Block>
            <BlockTitle>지원 내용</BlockTitle>
            <BlockText>{policy.support_content}</BlockText>
          </Block>
        )}

        {policy.apply_method && (
          <Block>
            <BlockTitle>신청 방법</BlockTitle>
            <BlockText>{policy.apply_method}</BlockText>
          </Block>
        )}

        {(policy.ref_url1 || policy.ref_url2) && (
          <Block>
            <BlockTitle>참고 링크</BlockTitle>
            {policy.ref_url1 && <RefLink href={policy.ref_url1} target="_blank" rel="noreferrer">{policy.ref_url1}</RefLink>}
            {policy.ref_url2 && <RefLink href={policy.ref_url2} target="_blank" rel="noreferrer">{policy.ref_url2}</RefLink>}
          </Block>
        )}
      </Card>
    </Page>
  )
}

function InfoItem({ label, value }: { label: string; value: string }) {
  return (
    <InfoBox>
      <InfoLabel>{label}</InfoLabel>
      <InfoValue>{value}</InfoValue>
    </InfoBox>
  )
}

const Page = styled.div`max-width: 760px;`
const BackBtn = styled.button`
  display: flex; align-items: center; gap: 6px; color: ${theme.colors.textSecondary};
  font-size: 14px; margin-bottom: 16px;
  &:hover { color: ${theme.colors.primary}; }
`
const Card = styled.div`background: ${theme.colors.surface}; border: 1px solid ${theme.colors.border}; border-radius: ${theme.radius.lg}; padding: 32px;`
const Top = styled.div`display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;`
const TagRow = styled.div`display: flex; gap: 6px;`
const Tag = styled.span<{ $sub?: boolean }>`
  padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 500;
  background: ${(p) => p.$sub ? '#F1F5F9' : '#EEF2FF'};
  color: ${(p) => p.$sub ? theme.colors.textSecondary : theme.colors.primary};
`
const BtnRow = styled.div`display: flex; gap: 8px;`
const ApplyBtn = styled.a`
  display: flex; align-items: center; gap: 6px; padding: 8px 16px;
  background: ${theme.colors.primary}; color: white; border-radius: ${theme.radius.sm};
  font-size: 13px; font-weight: 600;
  &:hover { background: ${theme.colors.primaryDark}; }
`
const BookmarkBtn = styled.button`
  display: flex; align-items: center; gap: 6px; padding: 8px 16px;
  border: 1.5px solid ${theme.colors.border}; border-radius: ${theme.radius.sm};
  font-size: 13px; font-weight: 500; color: ${theme.colors.textSecondary};
  &:hover { border-color: ${theme.colors.primary}; color: ${theme.colors.primary}; }
`
const PolicyName = styled.h1`font-size: 22px; font-weight: 700; line-height: 1.4; margin-bottom: 4px;`
const InstName = styled.p`font-size: 13px; color: ${theme.colors.textMuted}; margin-bottom: 20px;`
const InfoGrid = styled.div`display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 24px;`
const InfoBox = styled.div`background: #F8FAFC; border-radius: ${theme.radius.sm}; padding: 12px 16px;`
const InfoLabel = styled.p`font-size: 11px; color: ${theme.colors.textMuted}; margin-bottom: 4px;`
const InfoValue = styled.p`font-size: 14px; font-weight: 600;`
const Block = styled.div`margin-bottom: 20px;`
const BlockTitle = styled.h3`font-size: 14px; font-weight: 600; color: ${theme.colors.textSecondary}; margin-bottom: 8px; padding-bottom: 6px; border-bottom: 1px solid ${theme.colors.border};`
const BlockText = styled.p`font-size: 14px; line-height: 1.7; color: ${theme.colors.textPrimary}; white-space: pre-wrap;`
const RefLink = styled.a`display: block; font-size: 13px; color: ${theme.colors.primary}; text-decoration: underline; margin-bottom: 4px; word-break: break-all;`
const Loading = styled.div`padding: 60px; text-align: center; color: ${theme.colors.textSecondary};`
