'use client'

import { BookOpen, Gavel } from 'lucide-react'

interface ReferencesProps {
  references: {
    laws?: string[]
    cases?: string[]
  }
}

export function References({ references }: ReferencesProps) {
  const laws = references.laws ?? []
  const cases = references.cases ?? []

  if (laws.length === 0 && cases.length === 0) {
    return null
  }

  return (
    <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
      <div className="text-xs text-muted-foreground mb-2">📚 Verified References:</div>
      
      {laws.length > 0 && (
        <div className="mb-2">
          <div className="flex items-center gap-1 text-xs font-medium mb-1">
            <Gavel className="h-3 w-3" />
            Laws:
          </div>
          <ul className="text-xs space-y-1">
            {laws.map((law, index) => (
              <li key={index} className="text-blue-600 dark:text-blue-400">
                • {law}
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {cases.length > 0 && (
        <div>
          <div className="flex items-center gap-1 text-xs font-medium mb-1">
            <BookOpen className="h-3 w-3" />
            Cases:
          </div>
          <ul className="text-xs space-y-1">
            {cases.map((case_, index) => (
              <li key={index} className="text-green-600 dark:text-green-400">
                • {case_}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
