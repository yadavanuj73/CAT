import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { papersApi } from '../services/api';

export function usePapers(params?: {
  page?: number;
  page_size?: number;
  year?: number;
  section?: string;
}) {
  return useQuery({
    queryKey: ['papers', params],
    queryFn: () => papersApi.list(params),
  });
}

export function usePaper(id: string | undefined) {
  return useQuery({
    queryKey: ['papers', id],
    queryFn: () => papersApi.get(id!),
    enabled: !!id,
  });
}

export function useUploadPaper() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      file,
      metadata,
    }: {
      file: File;
      metadata: {
        title: string;
        year: number;
        slot?: string;
        section?: string;
        source?: string;
      };
    }) => papersApi.upload(file, metadata),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['papers'] });
    },
  });
}

export function useExtractPaper() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => papersApi.extract(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['papers'] });
    },
  });
}

export function useDeletePaper() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => papersApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['papers'] });
    },
  });
}
