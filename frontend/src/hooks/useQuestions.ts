import { useQuery } from '@tanstack/react-query';
import { questionsApi } from '../services/api';
import type { QuestionFilters } from '../types';

export function useQuestions(filters?: QuestionFilters) {
  return useQuery({
    queryKey: ['questions', filters],
    queryFn: () => questionsApi.list(filters),
  });
}

export function useQuestion(id: string | undefined) {
  return useQuery({
    queryKey: ['questions', id],
    queryFn: () => questionsApi.get(id!),
    enabled: !!id,
  });
}

export function useQuestionStats() {
  return useQuery({
    queryKey: ['questions', 'stats'],
    queryFn: () => questionsApi.getStats(),
  });
}
