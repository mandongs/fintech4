import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import styled from 'styled-components'
import { apiClient } from '../../../common/api/client'
import { theme } from '../../../common/styles/GlobalStyle'

const TYPE_TABS = [
  { key: '', label: '전체' },
  { key: 'saving', label: '적금' },
  { key: 'deposit', label: '예금' },
  { key: 'rent', label: '전세대출' },
  { key: 'mortgage', label: '주택담보대출' },
  { key: 'credit', label: '신용대출' },
]

interface Product {
  id: string
  company_name: string
  product_name: string
  product_type: string
  join_method: string | null
  is_youth_product: boolean
  max_limit: number | null
  match_reason: string | null
}

function formatLimit(n: number | null): string {
  if (!n) return '한도 별도 문의'
  if (n >= 100000000) return `${(n / 100000000).toFixed(0)}억원`
  if (n >= 10000) return `${(n / 10000).toFixed(0)}만원`
  return `${n.toLocaleString()}원`
}

const TYPE_ICON: Record<string, string> = {
  saving: '💰', deposit: '🏦', mortgage: '🏠', rent: '🏢', credit: '💳',
}

export function FinancialPage() {
  const [activeType, setActiveType] = useState('')

  const { data, isLoading, isError } = useQuery<{ total: number; items: Product[] }>({
    queryKey: ['recommend', 'financial', activeType],
    queryFn: () =>
      apiClient.get('/recommend/financial', {
        params: activeType ? { product_type: activeType } : {},
      }).then((r) => r.data),
    retry: false,
  })

  return (
    <Page>
      <Header>
        <h1>맞춤 금융상품</h1>
        <p>내 조건에 맞는 금융상품을 추천해드려요.</p>
      </Header>

      <Tabs>
        {TYPE_TABS.map((t) => (
          <Tab key={t.key} $active={activeType === t.key} onClick={() => setActiveType(t.key)}>
            {t.label}
          </Tab>
        ))}
      </Tabs>

      {isLoading && <Loading>금융상품을 분석하는 중...</Loading>}
      {isError && <Error>프로필을 먼저 등록해주세요.</Error>}

      <Grid>
        {data?.items.map((p) => (
          <Card key={p.id}>
            <CardTop>
              <TypeIcon>{TYPE_ICON[p.product_type] ?? '📄'}</TypeIcon>
              {p.is_youth_product && <YouthBadge>청년 특화</YouthBadge>}
            </CardTop>
            <Company>{p.company_name}</Company>
            <ProductName>{p.product_name}</ProductName>
            {p.max_limit && <Limit>최대 {formatLimit(p.max_limit)}</Limit>}
            {p.match_reason && <Reason>{p.match_reason}</Reason>}
            {p.join_method && <JoinMethod>{p.join_method}</JoinMethod>}
          </Card>
        ))}
      </Grid>
    </Page>
  )
}

const Page = styled.div``
const Header = styled.div`
  margin-bottom: 20px;
  h1 { font-size: 22px; font-weight: 700; margin-bottom: 4px; }
  p { color: ${theme.colors.textSecondary}; font-size: 14px; }
`
const Tabs = styled.div`display: flex; gap: 8px; margin-bottom: 24px; flex-wrap: wrap;`
const Tab = styled.button<{ $active: boolean }>`
  padding: 8px 16px; border-radius: 20px; font-size: 13px; font-weight: 500;
  border: 1.5px solid ${(p) => p.$active ? theme.colors.primary : theme.colors.border};
  background: ${(p) => p.$active ? '#EEF2FF' : 'white'};
  color: ${(p) => p.$active ? theme.colors.primary : theme.colors.textSecondary};
  transition: all 0.15s;
  &:hover { border-color: ${theme.colors.primary}; color: ${theme.colors.primary}; }
`
const Grid = styled.div`display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px;`
const Card = styled.div`
  background: ${theme.colors.surface}; border: 1px solid ${theme.colors.border};
  border-radius: ${theme.radius.md}; padding: 20px; display: flex; flex-direction: column; gap: 8px;
  transition: all 0.15s;
  &:hover { box-shadow: ${theme.shadow.md}; border-color: ${theme.colors.primaryLight}; }
`
const CardTop = styled.div`display: flex; justify-content: space-between; align-items: center;`
const TypeIcon = styled.span`font-size: 24px;`
const YouthBadge = styled.span`
  padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 700;
  background: #ECFDF5; color: ${theme.colors.success};
`
const Company = styled.p`font-size: 12px; color: ${theme.colors.textMuted};`
const ProductName = styled.h3`font-size: 15px; font-weight: 600; line-height: 1.4;`
const Limit = styled.p`font-size: 18px; font-weight: 700; color: ${theme.colors.primary};`
const Reason = styled.p`
  font-size: 12px; color: ${theme.colors.success}; background: #F0FDF4;
  padding: 6px 10px; border-radius: 6px;
`
const JoinMethod = styled.p`font-size: 12px; color: ${theme.colors.textMuted};`
const Loading = styled.div`padding: 60px; text-align: center; color: ${theme.colors.textSecondary};`
const Error = styled.div`padding: 32px; text-align: center; color: ${theme.colors.danger};`
