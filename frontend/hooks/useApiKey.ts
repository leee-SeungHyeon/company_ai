import { useState, useEffect } from "react"

export function useApiKey() {
  const [apiKey, setApiKey] = useState("")

  useEffect(() => {
    const stored = localStorage.getItem("api_key") || process.env.NEXT_PUBLIC_DEFAULT_API_KEY || ""
    setApiKey(stored)
  }, [])

  const saveApiKey = (key: string) => {
    localStorage.setItem("api_key", key)
    setApiKey(key)
  }

  return { apiKey, saveApiKey }
}
