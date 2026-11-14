import { useMutation } from '@tanstack/react-query'

import { api } from './client'
import type { components } from './schema'

type ReadingCreate = components['schemas']['ReadingCreate']

export function useCreateReading() {
  return useMutation({
    mutationFn: async (body: ReadingCreate = {}) => {
      const { data, error } = await api.POST('/api/readings', { body })
      if (error) throw new Error('Failed to draw cards')
      return data
    },
  })
}
