import { useState, useRef, useEffect } from 'react'
import styled, { keyframes } from 'styled-components'
import ReactMarkdown from 'react-markdown'
import { apiClient } from '../../../common/api/client'
import { theme } from '../../../common/styles/GlobalStyle'
import { FiSend } from 'react-icons/fi'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

const QUICK_QUESTIONS = [
  '이번 달 신청할 수 있는 지원금 있어?',
  '청년 전세대출 조건이 뭐야?',
  '연소득 3000만원이면 어떤 혜택 받을 수 있어?',
  '마감 임박한 정책 알려줘',
]

export function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: '안녕하세요! 청년 금융 혜택 AI 상담사입니다. 궁금한 것을 자유롭게 물어보세요. 😊\n\n예: "이번 달 신청할 수 있는 지원금 있어?" 또는 "청년 전세대출 조건이 뭐야?"',
    },
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  const sendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return

    const userMsg: Message = { role: 'user', content: text }
    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setIsLoading(true)

    try {
      // history 변환 (최근 6턴)
      const history = messages.slice(-6).map((m) => ({
        role: m.role === 'assistant' ? 'model' : 'user',
        parts: m.content,
      }))

      const res = await apiClient.post('/chat', { question: text, history })
      const assistantMsg: Message = { role: 'assistant', content: res.data.answer }
      setMessages((prev) => [...prev, assistantMsg])
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: '죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요.' },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    sendMessage(input)
  }

  return (
    <Page>
      <Header>
        <h1>AI 상담</h1>
        <p>자연어로 질문하면 내 상황에 맞는 답변을 드려요.</p>
      </Header>

      <ChatContainer>
        <MessageList>
          {messages.map((msg, i) => (
            <MessageRow key={i} $isUser={msg.role === 'user'}>
              {msg.role === 'assistant' && <Avatar>🤖</Avatar>}
              <Bubble $isUser={msg.role === 'user'}>
                {msg.role === 'assistant' ? (
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                ) : (
                  msg.content
                )}
              </Bubble>
            </MessageRow>
          ))}

          {isLoading && (
            <MessageRow $isUser={false}>
              <Avatar>🤖</Avatar>
              <Bubble $isUser={false}>
                <TypingDots>
                  <span /><span /><span />
                </TypingDots>
              </Bubble>
            </MessageRow>
          )}
          <div ref={bottomRef} />
        </MessageList>

        <InputArea>
          <QuickBtns>
            {QUICK_QUESTIONS.map((q) => (
              <QuickBtn key={q} onClick={() => sendMessage(q)} disabled={isLoading}>
                {q}
              </QuickBtn>
            ))}
          </QuickBtns>

          <InputRow onSubmit={handleSubmit}>
            <TextInput
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="질문을 입력하세요... (예: 나 취업 준비 중인데 받을 수 있는 거 있어?)"
              disabled={isLoading}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  sendMessage(input)
                }
              }}
            />
            <SendBtn type="submit" disabled={isLoading || !input.trim()}>
              <FiSend />
            </SendBtn>
          </InputRow>
        </InputArea>
      </ChatContainer>
    </Page>
  )
}

const bounce = keyframes`
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
`

const Page = styled.div`display: flex; flex-direction: column; height: calc(100vh - 64px);`
const Header = styled.div`
  margin-bottom: 16px; flex-shrink: 0;
  h1 { font-size: 22px; font-weight: 700; margin-bottom: 4px; }
  p { color: ${theme.colors.textSecondary}; font-size: 14px; }
`
const ChatContainer = styled.div`
  flex: 1; display: flex; flex-direction: column; background: ${theme.colors.surface};
  border: 1px solid ${theme.colors.border}; border-radius: ${theme.radius.lg}; overflow: hidden;
`
const MessageList = styled.div`flex: 1; overflow-y: auto; padding: 24px; display: flex; flex-direction: column; gap: 16px;`
const MessageRow = styled.div<{ $isUser: boolean }>`
  display: flex; flex-direction: ${(p) => p.$isUser ? 'row-reverse' : 'row'};
  align-items: flex-start; gap: 10px;
`
const Avatar = styled.div`font-size: 24px; flex-shrink: 0; margin-top: 4px;`
const Bubble = styled.div<{ $isUser: boolean }>`
  max-width: 72%; padding: 12px 16px; border-radius: ${theme.radius.md};
  font-size: 14px; line-height: 1.6;
  background: ${(p) => p.$isUser ? theme.colors.primary : '#F1F5F9'};
  color: ${(p) => p.$isUser ? 'white' : theme.colors.textPrimary};
  ${(p) => p.$isUser ? 'border-bottom-right-radius: 4px;' : 'border-bottom-left-radius: 4px;'}

  /* 마크다운 스타일 */
  p { margin-bottom: 8px; }
  p:last-child { margin-bottom: 0; }
  ul, ol { padding-left: 16px; margin-bottom: 8px; }
  li { margin-bottom: 4px; }
  strong { font-weight: 700; }
  a { color: ${theme.colors.primaryLight}; text-decoration: underline; }
`
const TypingDots = styled.div`
  display: flex; align-items: center; gap: 4px; padding: 4px 0;
  span {
    width: 8px; height: 8px; border-radius: 50%;
    background: ${theme.colors.textMuted}; display: inline-block;
    animation: ${bounce} 1.4s infinite ease-in-out both;
    &:nth-child(1) { animation-delay: 0s; }
    &:nth-child(2) { animation-delay: 0.16s; }
    &:nth-child(3) { animation-delay: 0.32s; }
  }
`
const InputArea = styled.div`
  border-top: 1px solid ${theme.colors.border}; padding: 16px 20px;
  display: flex; flex-direction: column; gap: 10px;
`
const QuickBtns = styled.div`display: flex; gap: 8px; flex-wrap: wrap;`
const QuickBtn = styled.button`
  padding: 6px 12px; border: 1.5px solid ${theme.colors.border};
  border-radius: 20px; font-size: 12px; color: ${theme.colors.textSecondary};
  transition: all 0.15s; background: white;
  &:hover:not(:disabled) { border-color: ${theme.colors.primary}; color: ${theme.colors.primary}; background: #EEF2FF; }
  &:disabled { opacity: 0.5; }
`
const InputRow = styled.form`display: flex; gap: 10px; align-items: flex-end;`
const TextInput = styled.textarea`
  flex: 1; padding: 12px 14px; border: 1.5px solid ${theme.colors.border};
  border-radius: ${theme.radius.sm}; font-size: 14px; resize: none; min-height: 44px; max-height: 120px;
  &:focus { outline: none; border-color: ${theme.colors.primary}; }
  &::placeholder { color: ${theme.colors.textMuted}; }
  &:disabled { background: #F8FAFC; }
`
const SendBtn = styled.button`
  width: 44px; height: 44px; border-radius: ${theme.radius.sm}; flex-shrink: 0;
  background: ${theme.colors.primary}; color: white; display: flex; align-items: center; justify-content: center;
  font-size: 18px; transition: background 0.15s;
  &:hover:not(:disabled) { background: ${theme.colors.primaryDark}; }
  &:disabled { opacity: 0.4; cursor: not-allowed; }
`
