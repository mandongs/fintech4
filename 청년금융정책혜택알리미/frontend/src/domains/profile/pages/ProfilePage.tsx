import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import styled from 'styled-components'
import toast from 'react-hot-toast'
import { apiClient } from '../../../common/api/client'
import { theme } from '../../../common/styles/GlobalStyle'

interface ProfileForm {
  birth_date: string
  annual_income: number
  region_name: string
  region_code: string
  marriage_status: string
  employment_type: string
  job_code: string
  school_code: string
}

const MARRIAGE_OPTIONS = ['미혼', '기혼', '이혼']
const EMPLOYMENT_OPTIONS = ['재직', '구직', '자영업', '프리랜서', '학생', '기타']
const JOB_OPTIONS = [
  { label: '선택 안 함', value: '' },
  { label: '재직자', value: '0013001' },
  { label: '구직자', value: '0013002' },
  { label: '창업자', value: '0013003' },
  { label: '프리랜서', value: '0013004' },
  { label: '학생', value: '0013005' },
  { label: '농어업인', value: '0013010' },
]
const SCHOOL_OPTIONS = [
  { label: '선택 안 함', value: '' },
  { label: '고졸 이하', value: '0049001' },
  { label: '대학 재학', value: '0049002' },
  { label: '대졸', value: '0049003' },
  { label: '대학원 재학', value: '0049004' },
  { label: '대학원졸', value: '0049005' },
]

export function ProfilePage() {
  const qc = useQueryClient()
  const { data: profile } = useQuery({
    queryKey: ['profile'],
    queryFn: () => apiClient.get('/profile').then((r) => r.data),
  })

  const { register, handleSubmit, reset, watch, formState: { isSubmitting } } = useForm<ProfileForm>()

  useEffect(() => {
    if (profile) reset(profile)
  }, [profile, reset])

  const mutation = useMutation({
    mutationFn: (data: ProfileForm) => apiClient.post('/profile', data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['profile'] })
      qc.invalidateQueries({ queryKey: ['recommend'] })
      toast.success('프로필이 저장되었습니다!')
    },
    onError: () => toast.error('저장에 실패했습니다.'),
  })

  const persona = profile?.persona

  return (
    <Page>
      <Header>
        <h1>내 프로필</h1>
        <p>정확한 정보를 입력할수록 더 정확한 혜택을 추천받을 수 있어요.</p>
      </Header>

      {persona && (
        <PersonaBadge>
          <span>✨</span>
          <div>
            <b>내 유형: {persona}</b>
            <small>프로필 기반으로 분석된 금융 성향입니다.</small>
          </div>
        </PersonaBadge>
      )}

      <Form onSubmit={handleSubmit((d) => mutation.mutate(d))}>
        <Section>
          <SectionTitle>기본 정보</SectionTitle>
          <Grid>
            <Field>
              <Label>생년월일 *</Label>
              <Input type="date" {...register('birth_date', { required: true })} />
            </Field>
            <Field>
              <Label>연소득 (만원)</Label>
              <Input type="number" placeholder="예: 2400" {...register('annual_income', { valueAsNumber: true })} />
            </Field>
            <Field>
              <Label>결혼 상태</Label>
              <Select {...register('marriage_status')}>
                <option value="">선택</option>
                {MARRIAGE_OPTIONS.map((o) => <option key={o} value={o}>{o}</option>)}
              </Select>
            </Field>
            <Field>
              <Label>고용 형태</Label>
              <Select {...register('employment_type')}>
                <option value="">선택</option>
                {EMPLOYMENT_OPTIONS.map((o) => <option key={o} value={o}>{o}</option>)}
              </Select>
            </Field>
          </Grid>
        </Section>

        <Section>
          <SectionTitle>지역 정보</SectionTitle>
          <Grid>
            <Field>
              <Label>거주 지역명</Label>
              <Input placeholder="예: 서울 강남구" {...register('region_name')} />
            </Field>
            <Field>
              <Label>지역 코드 (시군구)</Label>
              <Input placeholder="예: 11680" {...register('region_code')} />
              <Helper>
                <a href="https://www.code.go.kr/stdcode/regCodeL.do" target="_blank" rel="noreferrer">코드 조회 →</a>
              </Helper>
            </Field>
          </Grid>
        </Section>

        <Section>
          <SectionTitle>추가 조건</SectionTitle>
          <Grid>
            <Field>
              <Label>직업 유형</Label>
              <Select {...register('job_code')}>
                {JOB_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
              </Select>
            </Field>
            <Field>
              <Label>학력</Label>
              <Select {...register('school_code')}>
                {SCHOOL_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
              </Select>
            </Field>
          </Grid>
        </Section>

        <SaveBtn type="submit" disabled={isSubmitting}>
          {isSubmitting ? '저장 중...' : '프로필 저장'}
        </SaveBtn>
      </Form>
    </Page>
  )
}

const Page = styled.div`max-width: 720px;`
const Header = styled.div`
  margin-bottom: 24px;
  h1 { font-size: 24px; font-weight: 700; margin-bottom: 6px; }
  p { color: ${theme.colors.textSecondary}; font-size: 14px; }
`
const PersonaBadge = styled.div`
  display: flex; align-items: center; gap: 12px;
  background: linear-gradient(135deg, #EEF2FF, #F0FDF4);
  border: 1px solid ${theme.colors.primaryLight};
  border-radius: ${theme.radius.md}; padding: 16px 20px; margin-bottom: 24px;
  span { font-size: 28px; }
  div { display: flex; flex-direction: column; gap: 2px; }
  b { font-size: 15px; color: ${theme.colors.primary}; }
  small { font-size: 12px; color: ${theme.colors.textSecondary}; }
`
const Form = styled.form``
const Section = styled.div`
  background: ${theme.colors.surface}; border-radius: ${theme.radius.md};
  border: 1px solid ${theme.colors.border}; padding: 24px; margin-bottom: 16px;
`
const SectionTitle = styled.h2`font-size: 15px; font-weight: 600; margin-bottom: 16px; color: ${theme.colors.textPrimary};`
const Grid = styled.div`display: grid; grid-template-columns: 1fr 1fr; gap: 16px;`
const Field = styled.div``
const Label = styled.label`display: block; font-size: 13px; font-weight: 500; color: ${theme.colors.textSecondary}; margin-bottom: 6px;`
const Input = styled.input`
  width: 100%; padding: 10px 12px; border: 1.5px solid ${theme.colors.border};
  border-radius: ${theme.radius.sm}; font-size: 14px;
  &:focus { outline: none; border-color: ${theme.colors.primary}; }
`
const Select = styled.select`
  width: 100%; padding: 10px 12px; border: 1.5px solid ${theme.colors.border};
  border-radius: ${theme.radius.sm}; font-size: 14px; background: white;
  &:focus { outline: none; border-color: ${theme.colors.primary}; }
`
const Helper = styled.p`font-size: 11px; color: ${theme.colors.primary}; margin-top: 4px; a { text-decoration: underline; }`
const SaveBtn = styled.button`
  padding: 14px 32px; background: ${theme.colors.primary}; color: white;
  border-radius: ${theme.radius.sm}; font-size: 15px; font-weight: 600;
  &:hover { background: ${theme.colors.primaryDark}; }
  &:disabled { opacity: 0.6; cursor: not-allowed; }
`
