import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, FileText, X } from 'lucide-react';

interface FileUploadProps {
  onFilesSelected: (files: File[]) => void;
  acceptedFiles?: File[];
  onRemoveFile?: (index: number) => void;
  maxFiles?: number;
  disabled?: boolean;
}

export default function FileUpload({
  onFilesSelected,
  acceptedFiles = [],
  onRemoveFile,
  maxFiles = 10,
  disabled = false,
}: FileUploadProps) {
  const onDrop = useCallback(
    (files: File[]) => {
      onFilesSelected(files);
    },
    [onFilesSelected],
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles,
    disabled,
  });

  return (
    <div className="space-y-3">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer ${
          isDragActive
            ? 'border-accent bg-accent/5'
            : 'border-border hover:border-accent/50 hover:bg-surface-secondary/50'
        } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input {...getInputProps()} />
        <UploadCloud
          className={`h-10 w-10 mx-auto mb-3 ${
            isDragActive ? 'text-accent' : 'text-text-secondary/50'
          }`}
        />
        {isDragActive ? (
          <p className="text-accent font-medium">Drop PDF files here</p>
        ) : (
          <>
            <p className="text-text font-medium">
              Drag & drop PDF files here
            </p>
            <p className="text-text-secondary text-sm mt-1">
              or click to browse files
            </p>
          </>
        )}
      </div>

      {acceptedFiles.length > 0 && (
        <ul className="space-y-2" aria-label="Selected files">
          {acceptedFiles.map((file, i) => (
            <li
              key={`${file.name}-${i}`}
              className="flex items-center gap-3 px-4 py-2.5 bg-surface-secondary rounded-lg border border-border"
            >
              <FileText className="h-4 w-4 text-accent shrink-0" />
              <span className="text-sm text-text truncate flex-1">
                {file.name}
              </span>
              <span className="text-xs text-text-secondary whitespace-nowrap">
                {(file.size / 1024).toFixed(0)} KB
              </span>
              {onRemoveFile && (
                <button
                  onClick={() => onRemoveFile(i)}
                  className="p-0.5 rounded hover:bg-border transition-colors"
                  aria-label={`Remove ${file.name}`}
                >
                  <X className="h-3.5 w-3.5 text-text-secondary" />
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
