import { useNavigate, useParams } from 'react-router-dom'
import { useEffect, useState } from 'react'
import StrainForm, { StrainFormValues } from '../components/StrainForm'
import { fetchStrainDetails, updateStrain } from '../services/api'

export default function EditStrainPage() {
  const { strainId } = useParams<{ strainId: string }>()
  const navigate = useNavigate()
  const [initial, setInitial] = useState<any>(null)

  useEffect(() => {
    if (!strainId) return
    fetchStrainDetails(strainId)
      .then((data) => {
        const s = data.strain
        setInitial({
          strain_identifier: s.strain_identifier,
          scientific_name: s.scientific_name,
          common_name: s.common_name,
          description: s.description,
          isolation_source: s.isolation_source,
          isolation_location: s.isolation_location,
          isolation_date: s.isolation_date,
          gc_content_min: undefined,
          gc_content_max: undefined,
          gc_content_optimal: undefined,
          notes: s.notes,
          is_active: s.is_active
        })
      })
      .catch((e) => alert(e))
  }, [strainId])

  const handleSubmit = async (values: StrainFormValues) => {
    try {
      await updateStrain(Number(strainId), values)
      navigate(`/strains/${strainId}`)
    } catch (e) {
      alert(`Ошибка сохранения: ${e}`)
    }
  }

  if (!initial) return <p>Загрузка…</p>

  return (
    <div className="max-w-3xl mx-auto bg-white p-6 shadow">
      <h1 className="text-2xl font-bold mb-4">Редактировать штамм</h1>
      <StrainForm initial={initial} onSubmit={handleSubmit} submitLabel="Сохранить" />
    </div>
  )
} 