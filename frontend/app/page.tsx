"use client"

import { useState, useRef, useEffect } from "react"
import { useApiKey } from "@/hooks/useApiKey"

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000"

interface Message {
  role: "user" | "assistant"
  content: string
}

export default function Home() {
  const { apiKey, saveApiKey } = useApiKey()
  const [apiKeyInput, setApiKeyInput] = useState("")
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    setApiKeyInput(apiKey)
  }, [apiKey])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || !apiKey || loading) return

    const userMessage: Message = { role: "user", content: input }
    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setLoading(true)

    const assistantMessage: Message = { role: "assistant", content: "" }
    setMessages((prev) => [...prev, assistantMessage])

    try {
      const res = await fetch(`${API_BASE}/api/qa/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${apiKey}`,
        },
        body: JSON.stringify({ query: input }),
      })

      const reader = res.body!.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const lines = decoder.decode(value).split("\n")
        for (const line of lines) {
          if (!line.startsWith("data: ")) continue
          const data = line.slice(6)
          if (data === "[DONE]") break
          setMessages((prev) => {
            const updated = [...prev]
            updated[updated.length - 1] = {
              role: "assistant",
              content: updated[updated.length - 1].content + data,
            }
            return updated
          })
        }
      }
    } catch {
      setMessages((prev) => {
        const updated = [...prev]
        updated[updated.length - 1] = {
          role: "assistant",
          content: "오류가 발생했습니다. API Key와 서버 상태를 확인해주세요.",
        }
        return updated
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* 헤더 */}
      <header className="bg-white border-b px-6 py-4 flex items-center justify-between">
        <h1 className="text-lg font-semibold text-gray-800">사내 지식 베이스</h1>
        <div className="flex items-center gap-2">
          <input
            type="password"
            placeholder="API Key 입력"
            value={apiKeyInput}
            onChange={(e) => setApiKeyInput(e.target.value)}
            className="text-sm border rounded px-3 py-1.5 w-48 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={() => saveApiKey(apiKeyInput)}
            className="text-sm bg-blue-500 text-white px-3 py-1.5 rounded hover:bg-blue-600"
          >
            저장
          </button>
          {apiKey && <span className="text-xs text-green-500">● 연결됨</span>}
        </div>
      </header>

      {/* 메시지 목록 */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 mt-20">
            <p className="text-4xl mb-4">📚</p>
            <p className="text-lg">사내 규정이나 업무 절차를 질문해보세요.</p>
            <p className="text-sm mt-2">예) 연차는 몇 일이야? / IT 보안 정책 알려줘</p>
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-2xl px-4 py-3 rounded-2xl text-sm whitespace-pre-wrap ${
                msg.role === "user"
                  ? "bg-blue-500 text-white rounded-br-sm"
                  : "bg-white text-gray-800 border rounded-bl-sm shadow-sm"
              }`}
            >
              {msg.content || (loading && msg.role === "assistant" ? "▋" : "")}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* 입력창 */}
      <div className="bg-white border-t px-4 py-4">
        {!apiKey && (
          <p className="text-xs text-red-400 mb-2 text-center">API Key를 입력해주세요.</p>
        )}
        <div className="flex gap-2 max-w-3xl mx-auto">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault()
                handleSend()
              }
            }}
            placeholder="질문을 입력하세요... (Enter로 전송, Shift+Enter로 줄바꿈)"
            rows={1}
            className="flex-1 border rounded-xl px-4 py-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleSend}
            disabled={loading || !apiKey || !input.trim()}
            className="bg-blue-500 text-white px-5 rounded-xl hover:bg-blue-600 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            전송
          </button>
        </div>
      </div>
    </div>
  )
}
