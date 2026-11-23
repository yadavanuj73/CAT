import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { predictionsApi } from '../services/api';
import type { GeneratePredictionsRequest } from '../types';

export function usePredictions(params?: {
  section?: string;
  topic?: string;
  min_confidence?: number;
}) {
  return useQuery({
    queryKey: ['predictions', params],
    queryFn: () => predictionsApi.list(params),
  });
}

export function usePredictionEvidence(id: string | undefined) {
  return useQuery({
    queryKey: ['predictions', id, 'evidence'],
    queryFn: () => predictionsApi.getEvidence(id!),
    enabled: !!id,
  });
}

export function useGeneratePredictions() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: GeneratePredictionsRequest) =>
      predictionsApi.generate(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['predictions'] });
    },
  });
}
