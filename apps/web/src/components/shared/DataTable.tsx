import React from 'react';

interface Column<T> {
  header: string;
  accessor: keyof T | ((item: T) => React.ReactNode);
  className?: string;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  onRowClick?: (item: T) => void;
  isLoading?: boolean;
}

export function DataTable<T extends { id: string | number }>({
  columns,
  data,
  onRowClick,
  isLoading
}: DataTableProps<T>) {
  if (isLoading) {
    return (
      <div className="w-full space-y-4 animate-pulse">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-12 bg-white/5 rounded-lg w-full" />
        ))}
      </div>
    );
  }

  return (
    <div className="w-full overflow-x-auto rounded-xl border border-white/10 bg-black/20 backdrop-blur-sm">
      <table className="w-full text-left border-collapse">
        <thead className="bg-white/5 text-white/50 text-xs uppercase tracking-wider">
          <tr>
            {columns.map((col, i) => (
              <th key={i} className={`px-6 py-4 font-medium ${col.className || ''}`}>
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-white/5">
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="px-6 py-12 text-center text-white/30">
                No data available
              </td>
            </tr>
          ) : (
            data.map((item) => (
              <tr
                key={item.id}
                onClick={() => onRowClick?.(item)}
                className={`group hover:bg-white/5 transition-colors cursor-pointer`}
              >
                {columns.map((col, i) => (
                  <td key={i} className={`px-6 py-4 text-sm text-white/80 ${col.className || ''}`}>
                    {typeof col.accessor === 'function'
                      ? col.accessor(item)
                      : (item[col.accessor] as React.ReactNode)}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
