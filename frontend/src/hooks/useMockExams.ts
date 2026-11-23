import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { mockExamsApi } from '../services/api';
import type { GenerateMockRequest, SubmitAttemptRequest } from '../types';

export function useMockExams(params?: {
  page?: number;
  page_size?: number;
  exam_type?: string;
}) {
  return useQuery({
    queryKey: ['mock-exams', params],
    queryFn: () => mockExamsApi.list(params),
  });
}

export function useMockExam(id: string | undefined) {
  return useQuery({
    queryKey: ['mock-exams', id],
    queryFn: () => mockExamsApi.get(id!),
    enabled: !!id,
  });
}

export function useGenerateMockExam() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: GenerateMockRequest) => mockExamsApi.generate(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mock-exams'] });
    },
  });
}

export function useStartAttempt() {
  return useMutation({
    mutationFn: (examId: string) => mockExamsApi.startAttempt(examId),
  });
}

export function useSubmitAttempt() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      examId,
      attemptId,
      data,
    }: {
      examId: string;
      attemptId: string;
      data: SubmitAttemptRequest;
    }) => mockExamsApi.submitAttempt(examId, attemptId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mock-exams'] });
    },
  });
}

export function useAttemptResults(
  examId: string | undefined,
  attemptId: string | undefined,
) {
  return useQuery({
    queryKey: ['mock-exams', examId, 'attempts', attemptId, 'results'],
    queryFn: () => mockExamsApi.getResults(examId!, attemptId!),
    enabled: !!examId && !!attemptId,
  });
}
