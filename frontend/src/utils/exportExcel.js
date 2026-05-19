import * as XLSX from 'xlsx'

/**
 * Export data to an Excel file.
 * @param {Array} columns - AntD Table columns array (with title + dataIndex)
 * @param {Array} data - Array of row objects
 * @param {string} filename - Download filename (without extension)
 */
export function exportToExcel(columns, data, filename) {
  // Filter columns that have no dataIndex (like action/操作 columns)
  const exportCols = columns.filter(col => col.dataIndex && col.key !== 'action')

  // Build worksheet data
  const header = exportCols.map(col => col.title || col.dataIndex)
  const rows = data.map(row =>
    exportCols.map(col => {
      const value = row[col.dataIndex]
      // Handle null/undefined
      if (value === null || value === undefined) return ''
      // Strip HTML tags (e.g. from Tag components)
      const str = String(value).replace(/<[^>]*>/g, '')
      return str
    })
  )

  const wsData = [header, ...rows]
  const ws = XLSX.utils.aoa_to_sheet(wsData)

  // Auto-width columns
  const colWidths = exportCols.map((col, i) => {
    const maxLen = Math.max(
      header[i].length,
      ...rows.map(r => String(r[i] || '').length)
    )
    return { wch: Math.min(maxLen + 4, 60) }
  })
  ws['!cols'] = colWidths

  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, 'Sheet1')
  XLSX.writeFile(wb, `${filename}.xlsx`)
}
