import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Strain, TestResult, CollectionNumber } from 'types';
import { fetchStrainDetails } from 'services/api';
import { ArrowLeft, Dna, Beaker, Thermometer, Droplet, Microscope, Ruler, FlaskConical, TestTube, ChevronsRight } from 'lucide-react';

const DetailCard = ({ title, children, icon }: { title: string, children: React.ReactNode, icon?: React.ReactNode }) => (
    <div className="bg-white shadow-lg rounded-lg overflow-hidden mb-6">
        <div className="bg-gray-100 px-6 py-3 border-b border-gray-200 flex items-center">
            {icon && <div className="mr-3 text-gray-600">{icon}</div>}
            <h3 className="text-xl font-semibold text-gray-800">{title}</h3>
        </div>
        <div className="p-6">
            {children}
        </div>
    </div>
);

const InfoRow = ({ label, value, unit }: { label: string, value: string | number | undefined | null, unit?: string }) => {
    if (value === null || value === undefined || value === '') {
        return null;
    }
    return (
        <div className="grid grid-cols-3 gap-4 py-2 border-b border-gray-100 last:border-b-0">
            <dt className="text-sm font-medium text-gray-600">{label}</dt>
            <dd className="text-sm text-gray-900 col-span-2">{value} {unit}</dd>
        </div>
    );
};

const InfoField = ({ label, children, fullWidth = false }: { label: string, children: React.ReactNode, fullWidth?: boolean }) => {
    if (!children) return null;
    return (
        <div className={fullWidth ? "col-span-1 md:col-span-2 lg:col-span-3" : ""}>
            <p className="text-sm font-semibold text-gray-500">{label}</p>
            <p className="text-base text-gray-900 break-words">{children}</p>
        </div>
    );
}

const TestGrid = ({ children }: { children: React.ReactNode }) => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-8 gap-y-3">
        {children}
    </div>
);

const CATEGORY_DEFINITIONS: Record<string, { title: string; icon: React.ReactNode }> = {
    morphological: { title: "Морфологические свойства", icon: <Microscope size={22} /> },
    physiological: { title: "Физиологические свойства", icon: <Thermometer size={22} /> },
    biochemical_enzymes: { title: "Биохимические свойства: Ферменты", icon: <FlaskConical size={22} /> },
    biochemical_breakdown: { title: "Биохимические свойства: Разложение", icon: <Droplet size={22} /> },
    biochemical_utilization: { title: "Биохимические свойства: Утилизация сахаров", icon: <TestTube size={22} /> },
    other_biochemical: { title: "Прочие биохимические характеристики", icon: <ChevronsRight size={22} /> },
};

const formatTestName = (name: string) => {
    return name.replace(/\s*\((мин|макс|опт)\)\s*\(\1\)/gi, ' ($1)');
};

const suffixOrder: Record<string, number> = { 'мин': 0, 'опт': 1, 'макс': 2 };

const StrainDetail: React.FC = () => {
    const { strainId } = useParams<{ strainId: string }>();
    const [strain, setStrain] = useState<Strain | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const getStrainDetails = async () => {
            if (!strainId) return;
            try {
                setLoading(true);
                const data = await fetchStrainDetails(strainId);
                setStrain(data);
                setError(null);
            } catch (err) {
                setError('Failed to fetch strain details. The record may be incomplete or missing.');
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        getStrainDetails();
    }, [strainId]);

    const renderTestResults = (category: string) => {
        const results = strain?.test_results?.filter((r: TestResult) => r.category?.toLowerCase() === category.toLowerCase()) || [];
        if (results.length === 0) {
            return <p className="text-sm italic text-gray-500">n.d.</p>;
        }

        const sortedResults = [...results].sort((a, b) => {
            const suffixA = (a.test_name.match(/\((мин|опт|макс)\)/i) || [])[1]?.toLowerCase();
            const suffixB = (b.test_name.match(/\((мин|опт|макс)\)/i) || [])[1]?.toLowerCase();
            const orderA = suffixA ? suffixOrder[suffixA] ?? 99 : 99;
            const orderB = suffixB ? suffixOrder[suffixB] ?? 99 : 99;
            if (a.test_name.split(' ')[0] === b.test_name.split(' ')[0] && orderA !== orderB) {
                return orderA - orderB;
            }
            return a.test_name.localeCompare(b.test_name, 'ru');
        });

        return (
            <TestGrid>
                {sortedResults.map((res: TestResult, index: number) => (
                    <InfoRow key={index} label={formatTestName(res.test_name)} value={res.result} />
                ))}
            </TestGrid>
        );
    };

    if (loading) return <div className="text-center py-10">Загрузка данных о штамме...</div>;
    if (error) return <div className="text-center py-10 text-red-500">{error}</div>;
    if (!strain) return <div className="text-center py-10">Штамм не найден.</div>;

    const { strain: strainData } = strain;

    return (
        <div className="container mx-auto p-4 md:p-8 bg-gray-50 min-h-screen">
            <div className="mb-8">
                <Link to="/strains" className="inline-flex items-center text-blue-600 hover:text-blue-800 transition-colors">
                    <ArrowLeft className="mr-2" size={18} />
                    Назад к списку штаммов
                </Link>
                <h1 className="text-4xl font-bold text-gray-900 mt-4">{strainData.strain_identifier}</h1>
                <p className="text-lg text-gray-600 italic">{strainData.scientific_name}</p>
            </div>

            <DetailCard title="Общая информация" icon={<Dna size={22} />}>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-6 gap-y-6">
                    <InfoField label="Идентификатор">{strainData.strain_identifier}</InfoField>
                    <InfoField label="Научное название">{strainData.scientific_name}</InfoField>
                    <InfoField label="Распространенное название">{strainData.common_name}</InfoField>
                    <InfoField label="Источник изоляции">{strainData.isolation_source}</InfoField>
                    <InfoField label="Место изоляции">{strainData.isolation_location}</InfoField>
                    <InfoField label="Дата изоляции">{strainData.isolation_date}</InfoField>
                    <InfoField label="GC-состав">{strainData.gc_content_range}</InfoField>
                    <InfoField label="Источник данных">{strainData.data_source?.source_name}</InfoField>
                    <InfoField label="Номера в коллекциях" fullWidth>
                        {strainData.collection_numbers?.map((cn: CollectionNumber) => cn.full_identifier).join(', ')}
                    </InfoField>
                    <InfoField label="Описание" fullWidth>
                        <span className="whitespace-pre-wrap">{strainData.description}</span>
                    </InfoField>
                </div>
            </DetailCard>

            {/* Карточки с результатами тестов */}
            {Object.entries(CATEGORY_DEFINITIONS).map(([categoryCode, { title, icon }]) => (
                <DetailCard key={categoryCode} title={title} icon={icon}>
                    {renderTestResults(categoryCode)}
                </DetailCard>
            ))}

        </div>
    );
};

export default StrainDetail; 