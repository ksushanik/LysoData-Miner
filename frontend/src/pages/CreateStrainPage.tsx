import { useNavigate } from 'react-router-dom'
import StrainForm, { StrainFormValues } from '../components/StrainForm'
import { createStrain } from '../services/api'

export default function CreateStrainPage() {
  const navigate = useNavigate()

  const handleSubmit = async (values: StrainFormValues) => {
    try {
      const id = await createStrain(values)
      navigate(`/strains/${id}`)
    } catch (e) {
      alert(`Ошибка создания: ${e}`)
    }
  }

  return (
    <div className="max-w-3xl mx-auto bg-white p-6 shadow">
      <h1 className="text-2xl font-bold mb-4">Новый штамм</h1>
      <StrainForm onSubmit={handleSubmit} submitLabel="Создать" />
    </div>
  )
} 