'use client'

import { useState } from 'react'
import { ChevronDown, Globe } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { useCountryStore } from '@/hooks/useCountryStore'

const countries = [
  { code: 'nigeria', name: 'Nigeria', flag: '🇳🇬' },
  { code: 'ghana', name: 'Ghana', flag: '🇬🇭' },
  { code: 'kenya', name: 'Kenya', flag: '🇰🇪' },
  { code: 'south-africa', name: 'South Africa', flag: '🇿🇦' },
  { code: 'uganda', name: 'Uganda', flag: '🇺🇬' },
  { code: 'tanzania', name: 'Tanzania', flag: '🇹🇿' },
  { code: 'ethiopia', name: 'Ethiopia', flag: '🇪🇹' },
  { code: 'zimbabwe', name: 'Zimbabwe', flag: '🇿🇼' },
]

export function CountrySelector() {
  const [isOpen, setIsOpen] = useState(false)
  const { selectedCountry, setCountry } = useCountryStore()
  
  const currentCountry = countries.find(c => c.code === selectedCountry) || countries[0]

  return (
    <div className="relative">
      <Button
        variant="outline"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2"
      >
        <Globe className="w-4 h-4" />
        <span>{currentCountry.flag}</span>
        <span>{currentCountry.name}</span>
        <ChevronDown className="w-4 h-4" />
      </Button>

      {isOpen && (
        <div className="absolute right-0 top-full mt-1 w-48 bg-white dark:bg-gray-800 border rounded-md shadow-lg z-50">
          {countries.map((country) => (
            <button
              key={country.code}
              onClick={() => {
                setCountry(country.code)
                setIsOpen(false)
              }}
              className={`w-full flex items-center gap-2 px-3 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-700 ${
                selectedCountry === country.code ? 'bg-blue-50 dark:bg-blue-900' : ''
              }`}
            >
              <span>{country.flag}</span>
              <span>{country.name}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
