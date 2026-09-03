import { useState } from 'react'
import { generateAdvisory } from '../services/advisoryService'

export function useAdvisory() {
  const [state, setState] = useState({ data: null, loading: false, error: '' })
  const submit = async (payload) => {
    setState({ data: null, loading: true, error: '' })
    try {
      const data = await generateAdvisory(payload)
      setState({ data, loading: false, error: '' })
      return data
    } catch (error) {
      console.error(error)
      setState({ data: null, loading: false, error: 'Unable to generate personalized advisory.' })
      return null
    }
  }
  return { ...state, submit }
}
