// Task 15: Button that triggers PDF report generation and download
'use client';

interface PDFExportButtonProps {
  targetRoleId?: number;
  disabled?: boolean;
}

export default function PDFExportButton({ targetRoleId, disabled }: PDFExportButtonProps) {
  const handleExport = async () => {
    // Full implementation in Task 15
    alert('PDF export coming in Task 15');
  };

  return (
    <button
      onClick={handleExport}
      disabled={disabled}
      className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
    >
      Export PDF
    </button>
  );
}
