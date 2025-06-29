import React, { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { StrainPayload, fetchTestCategories, TestCategoryWithTests } from '../services/api'
import type { Test, TestValue, BooleanTestValue, NumericTestValue } from '../types'
import BooleanTestInput from './BooleanTestInput'
import NumericTestInput from './NumericTestInput'
import TextTestInput from './TextTestInput'

// ------------------
// Validation schema
// ------------------
const schema = z.object({
  strain_identifier: z.string().min(2, 'Обязательное поле'),
  scientific_name: z.string().optional(),
  common_name: z.string().optional(),
  description: z.string().optional(),
  isolation_source: z.string().optional(),
  isolation_location: z.string().optional(),
  isolation_date: z.string().optional(),
  notes: z.string().optional(),
  is_active: z.boolean().optional()
})

export type StrainFormValues = z.infer<typeof schema> & { test_results: any[] }

interface Props {
  initial?: Partial<StrainPayload>
  onSubmit: (values: StrainFormValues) => Promise<void> | void
  submitLabel?: string
}

export default function StrainForm({ initial = {}, onSubmit, submitLabel = 'Сохранить' }: Props) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm<StrainFormValues>({
    resolver: zodResolver(schema),
    defaultValues: initial as any
  })

  // ------------------
  // Test categories & values state
  // ------------------
  const [categories, setCategories] = useState<TestCategoryWithTests[]>([])
  const [testValues, setTestValues] = useState<Record<number, TestValue>>({})
  const [loadingTests, setLoadingTests] = useState(true)

  useEffect(() => {
    let mounted = true
    fetchTestCategories(true)
      .then((cats) => {
        if (mounted) setCategories(cats)
      })
      .catch((e) => console.error('Ошибка загрузки тестов:', e))
      .finally(() => setLoadingTests(false))
    return () => {
      mounted = false
    }
  }, [])

  // ------------------
  // Helpers
  // ------------------
  const upsertTestValue = (test: Test, partial: Partial<TestValue> | undefined) => {
    setTestValues((prev) => {
      const copy = { ...prev }
      if (partial === undefined) {
        delete copy[test.test_id]
        return copy
      }
      copy[test.test_id] = {
        ...copy[test.test_id],
        ...partial,
        test_id: test.test_id,
        test_code: test.test_code,
        test_type: test.test_type
      } as TestValue
      return copy
    })
  }

  const convertToBackendResults = (): any[] => {
    const results: any[] = []
    Object.values(testValues).forEach((tv) => {
      if (tv.test_type === 'boolean' && tv.boolean_value) {
        const val = tv.boolean_value as BooleanTestValue
        results.push({ type: 'boolean', test_id: tv.test_id, result_code: val.value })
      } else if (tv.test_type === 'numeric' && tv.numeric_value) {
        const nv = tv.numeric_value as NumericTestValue
        if (nv.mode === 'exact' && nv.exact !== undefined) {
          results.push({ type: 'numeric', test_id: tv.test_id, value_type: 'single', numeric_value: nv.exact })
        } else if (nv.mode === 'range' && nv.range) {
          results.push({ type: 'numeric', test_id: tv.test_id, value_type: 'minimum', numeric_value: nv.range.min })
          results.push({ type: 'numeric', test_id: tv.test_id, value_type: 'maximum', numeric_value: nv.range.max })
        }
      } else if (tv.test_type === 'text' && tv.text_value !== undefined) {
        results.push({ type: 'text', test_id: tv.test_id, text_value: tv.text_value })
      }
    })
    return results
  }

  // ------------------
  // Submit handler
  // ------------------
  const onValidSubmit = (data: z.infer<typeof schema>) => {
    const payload: StrainFormValues = {
      ...data,
      test_results: convertToBackendResults()
    }
    return onSubmit(payload)
  }

  // ------------------
  // Render helpers
  // ------------------
  const renderTestInput = (test: Test) => {
    const current = testValues[test.test_id]
    switch (test.test_type) {
      case 'boolean':
        return (
          <BooleanTestInput
            key={test.test_id}
            test={test}
            value={current?.boolean_value as BooleanTestValue | undefined}
            onChange={(val) =>
              upsertTestValue(test, val ? { boolean_value: val } : undefined)
            }
          />
        )
      case 'numeric':
        return (
          <NumericTestInput
            key={test.test_id}
            test={test}
            value={current?.numeric_value as NumericTestValue | undefined}
            onChange={(val) =>
              upsertTestValue(test, val ? { numeric_value: val } : undefined)
            }
          />
        )
      case 'text':
      default:
        return (
          <TextTestInput
            key={test.test_id}
            test={test}
            value={current?.text_value}
            onChange={(val) =>
              upsertTestValue(test, val ? { text_value: val } : undefined)
            }
          />
        )
    }
  }

  // ------------------
  // Component render
  // ------------------
  return (
    <form onSubmit={handleSubmit(onValidSubmit)} className="space-y-6">
      {/* BASIC STRAIN FIELDS */}
      <div className="space-y-4 bg-white p-4 rounded-lg shadow">
        <div>
          <label className="block text-sm font-medium mb-1">Идентификатор *</label>
          <input {...register('strain_identifier')} className="w-full border px-3 py-2 rounded" />
          {errors.strain_identifier && (
            <p className="text-red-600 text-sm">{errors.strain_identifier.message}</p>
          )}
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Научное название</label>
          <input {...register('scientific_name')} className="w-full border px-3 py-2 rounded" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Описание</label>
          <textarea {...register('description')} className="w-full border px-3 py-2 rounded" rows={3} />
        </div>
        <div className="flex space-x-4">
          <div className="flex-1">
            <label className="block text-sm font-medium mb-1">Источник изоляции</label>
            <input {...register('isolation_source')} className="w-full border px-3 py-2 rounded" />
          </div>
          <div className="flex-1">
            <label className="block text-sm font-medium mb-1">Место изоляции</label>
            <input {...register('isolation_location')} className="w-full border px-3 py-2 rounded" />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Дата изоляции</label>
          <input type="date" {...register('isolation_date')} className="border px-3 py-2 rounded" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Примечания</label>
          <textarea {...register('notes')} className="w-full border px-3 py-2 rounded" rows={2} />
        </div>
      </div>

      {/* TEST RESULTS SECTION */}
      <div className="space-y-3">
        <h2 className="text-xl font-semibold">Результаты тестов</h2>
        {loadingTests && <p>Загрузка тестов…</p>}
        {!loadingTests && categories.length === 0 && <p className="text-gray-500">Тесты не найдены</p>}

        {categories.map((cat) => (
          <details key={cat.category_id} className="border rounded-lg overflow-hidden">
            <summary className="cursor-pointer bg-gray-100 px-4 py-2 text-sm font-medium select-none">
              {cat.category_name} ({cat.tests.length})
            </summary>
            <div className="p-4 grid md:grid-cols-2 gap-4">
              {cat.tests.map((t) => renderTestInput(t))}
            </div>
          </details>
        ))}
      </div>

      {/* SUBMIT BUTTON */}
      <button
        type="submit"
        disabled={isSubmitting}
        className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
      >
        {isSubmitting ? 'Сохранение…' : submitLabel}
      </button>
    </form>
  )
} 