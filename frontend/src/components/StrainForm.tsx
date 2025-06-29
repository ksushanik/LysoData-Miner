import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { StrainPayload } from '../services/api'

const schema = z.object({
  strain_identifier: z.string().min(2, 'Обязательное поле'),
  scientific_name: z.string().optional(),
  common_name: z.string().optional(),
  description: z.string().optional(),
  isolation_source: z.string().optional(),
  isolation_location: z.string().optional(),
  isolation_date: z.string().optional(),
  gc_content_min: z.coerce.number().optional(),
  gc_content_max: z.coerce.number().optional(),
  gc_content_optimal: z.coerce.number().optional(),
  notes: z.string().optional(),
  is_active: z.boolean().optional()
})

export type StrainFormValues = z.infer<typeof schema>

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

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-1">Идентификатор *</label>
        <input {...register('strain_identifier')} className="w-full border px-3 py-2 rounded" />
        {errors.strain_identifier && <p className="text-red-600 text-sm">{errors.strain_identifier.message}</p>}
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

      <div className="grid grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">GC min %</label>
          <input type="number" step="0.01" {...register('gc_content_min')} className="w-full border px-3 py-2 rounded" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">GC max %</label>
          <input type="number" step="0.01" {...register('gc_content_max')} className="w-full border px-3 py-2 rounded" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">GC opt %</label>
          <input type="number" step="0.01" {...register('gc_content_optimal')} className="w-full border px-3 py-2 rounded" />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Примечания</label>
        <textarea {...register('notes')} className="w-full border px-3 py-2 rounded" rows={2} />
      </div>

      <button type="submit" disabled={isSubmitting} className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700">
        {isSubmitting ? 'Сохранение…' : submitLabel}
      </button>
    </form>
  )
} 