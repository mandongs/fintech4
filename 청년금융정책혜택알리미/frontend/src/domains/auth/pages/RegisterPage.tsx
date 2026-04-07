import { useForm } from 'react-hook-form'
import { useNavigate, Link } from 'react-router-dom'
import styled from 'styled-components'
import toast from 'react-hot-toast'
import { apiClient } from '../../../common/api/client'
import { useAuthStore } from '../store/authStore'
import { theme } from '../../../common/styles/GlobalStyle'

interface FormValues {
  email: string
  password: string
  passwordConfirm: string
}

export function RegisterPage() {
  const { register, handleSubmit, watch, formState: { errors, isSubmitting } } = useForm<FormValues>()
  const setTokens = useAuthStore((s) => s.setTokens)
  const navigate = useNavigate()

  const onSubmit = async ({ email, password }: FormValues) => {
    try {
      const res = await apiClient.post('/auth/register', { email, password })
      setTokens(res.data.access_token, res.data.refresh_token)
      toast.success('회원가입이 완료되었습니다!')
      navigate('/profile')
    } catch (e: any) {
      toast.error(e.response?.data?.detail ?? '회원가입에 실패했습니다.')
    }
  }

  return (
    <Page>
      <Card>
        <Logo>💰 청년혜택 플랫폼</Logo>
        <Title>회원가입</Title>
        <form onSubmit={handleSubmit(onSubmit)}>
          <Field>
            <Label>이메일</Label>
            <Input type="email" placeholder="email@example.com"
              {...register('email', { required: '이메일을 입력해주세요.' })} />
            {errors.email && <Error>{errors.email.message}</Error>}
          </Field>
          <Field>
            <Label>비밀번호 (8자 이상)</Label>
            <Input type="password" placeholder="비밀번호"
              {...register('password', { required: true, minLength: { value: 8, message: '8자 이상 입력해주세요.' } })} />
            {errors.password && <Error>{errors.password.message}</Error>}
          </Field>
          <Field>
            <Label>비밀번호 확인</Label>
            <Input type="password" placeholder="비밀번호 확인"
              {...register('passwordConfirm', {
                required: true,
                validate: (v) => v === watch('password') || '비밀번호가 일치하지 않습니다.',
              })} />
            {errors.passwordConfirm && <Error>{errors.passwordConfirm.message}</Error>}
          </Field>
          <SubmitBtn type="submit" disabled={isSubmitting}>
            {isSubmitting ? '처리 중...' : '가입하기'}
          </SubmitBtn>
        </form>
        <Footer>이미 계정이 있으신가요? <Link to="/login">로그인</Link></Footer>
      </Card>
    </Page>
  )
}

const Page = styled.div`
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #EEF2FF 0%, #F8FAFC 100%);
`
const Card = styled.div`
  background: ${theme.colors.surface}; border-radius: ${theme.radius.xl};
  box-shadow: ${theme.shadow.lg}; padding: 48px 40px; width: 100%; max-width: 420px;
`
const Logo = styled.div`
  font-size: 20px; font-weight: 700; color: ${theme.colors.primary}; text-align: center; margin-bottom: 8px;
`
const Title = styled.h1`font-size: 24px; font-weight: 700; text-align: center; margin-bottom: 32px;`
const Field = styled.div`margin-bottom: 16px;`
const Label = styled.label`display: block; font-size: 14px; font-weight: 500; color: ${theme.colors.textSecondary}; margin-bottom: 6px;`
const Input = styled.input`
  width: 100%; padding: 12px 14px; border: 1.5px solid ${theme.colors.border};
  border-radius: ${theme.radius.sm}; font-size: 15px; transition: border 0.15s;
  &:focus { outline: none; border-color: ${theme.colors.primary}; }
`
const Error = styled.p`color: ${theme.colors.danger}; font-size: 12px; margin-top: 4px;`
const SubmitBtn = styled.button`
  width: 100%; padding: 14px; background: ${theme.colors.primary}; color: white;
  border-radius: ${theme.radius.sm}; font-size: 16px; font-weight: 600; margin-top: 8px;
  transition: background 0.15s;
  &:hover { background: ${theme.colors.primaryDark}; }
  &:disabled { opacity: 0.6; cursor: not-allowed; }
`
const Footer = styled.p`
  text-align: center; margin-top: 24px; color: ${theme.colors.textSecondary}; font-size: 14px;
  a { color: ${theme.colors.primary}; font-weight: 600; }
`
