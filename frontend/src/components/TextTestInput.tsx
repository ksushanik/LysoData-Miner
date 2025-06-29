import React from 'react'
import type { Test } from '../types'

interface TextTestInputProps {
  test: Test
  value?: string
  onChange: (value: string | undefined) => void
  className?: string
}

const TextTestInput: React.FC<TextTestInputProps> = ({ test, value, onChange, className = '' }) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value.trim()
    onChange(val === '' ? undefined : val)
  }

  const clearValue = () => onChange(undefined)

  return (
    <div className={`space-y-2 ${className}`}>
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-gray-700">{test.test_name}</label>
        <button
          type="button"
          onClick={clearValue}
          className="text-xs text-gray-400 hover:text-gray-600"
          title="Очистить значение"
        >
          ✕
        </button>
      </div>

      <input
        type="text"
        value={value ?? ''}
        onChange={handleChange}
        placeholder="Введите значение"
        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
      />

      {test.description && (
        <p className="text-xs text-gray-500 italic mt-1">{test.description}</p>
      )}
    </div>
  )
}

export default TextTestInput 