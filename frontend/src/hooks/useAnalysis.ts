import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { analysisApi } from '../services/api';
import type { RunAnalysisRequest } from '../types';

export function useAnalysis(section: string | undefined) {
  return useQuery({
    queryKey: ['analysis', section],
    queryFn: () => analysisApi.getBySection(section!),
    enabled: !!section,
  });
}

export function useAnalysisSummary() {
  return useQuery({
    queryKey: ['analysis', 'summary'],
    queryFn: () => analysisApi.getSummary(),
  });
}

export function useRunAnalysis() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: RunAnalysisRequest) => analysisApi.run(data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({
        queryKey: ['analysis', variables.section],
      });
      queryClient.invalidateQueries({ queryKey: ['analysis', 'summary'] });
    },
  });
}
