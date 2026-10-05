import { useCallback, useMemo, useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { useRouter } from 'next/navigation';
import { toast } from 'react-toastify';
import {
  createWidgetStore,
} from '@openg2p/registry-widgets';
import type { SectionChanges } from '@openg2p/registry-widgets';
import type { SectionsFormHandle } from '@openg2p/registry-widgets';
import { IntakeFormSection } from '../types/intake-form';
import FormDetailsCard from './FormDetailsCard';
import { useIntakeDeduplication } from '../hooks/useIntakeDeduplication';
import DeduplicationCardForIntake from './DeduplicationCardForIntake';
import IntakeFormSections from './IntakeFormSections';
import IntakeFormDeduplicationTabs from './IntakeFormDeduplicationTabs';

export type SectionStatus = 'Saved' | 'Draft' | null;

export interface AccordionFormsProps {
  formDetailsCard?: boolean;
  sections: IntakeFormSection[];
  form_name?: string;
  form_description?: string;
  schemaData?: any;
  onAction?: (sectionChanges?: SectionChanges, type?: 'submit' | 'draft', section?: IntakeFormSection) => void;
  onCancel?: () => void;
  showActions?: boolean;
  submissionId?: string;
  registerType?: string;
}

export default function MultiSectionAccordionForms({

  formDetailsCard = false,
  sections,
  form_name,
  form_description,
  schemaData = {},
  onAction,
  onCancel,
  showActions = true,
  submissionId,
  registerType,
}: AccordionFormsProps) {

  const t = useTranslations();
  const router = useRouter();
  const widgetStore = useMemo(() => createWidgetStore(), []);

  const [formHandle, setFormHandle] = useState<SectionsFormHandle | null>(null);
  const [savedSections, setSavedSections] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState<"intake_forms" | "intake_possible_duplicates" | "register_possible_duplicates">("intake_forms");

  const { results: intakeResults, loading: intakeLoading } = useIntakeDeduplication(submissionId || "", "intake-form");
  const { results: regResults, loading: regLoading } = useIntakeDeduplication(submissionId || "", "register");

  useEffect(() => {
    if (schemaData) {
      const alreadySaved = sections
        .filter((s) => schemaData[s.section_register_id] || submissionId)
        .map((s) => s.section_id);
      setSavedSections((prev) => Array.from(new Set([...prev, ...alreadySaved])));
    }
  }, [schemaData, sections, submissionId]);

  const allSectionsSaved = useMemo(() => {
    return sections.every(
      (section) =>
        savedSections.includes(section.section_id) ||
        !!schemaData[section.section_register_id]
    );
  }, [sections, savedSections, schemaData]);

  const sectionsConfig = useMemo(
    () =>
      sections.map((section) => ({
        ...section.section_ui_schema,
      })),
    [sections]
  );

  const intakeFormHeading = useMemo(() => form_name, [form_name]);
  const intakeFormDescription = useMemo(() => form_description, [form_description]);


  const handleSectionSave = useCallback(
    async (sectionChanges: SectionChanges) => {
      const section = sections.find((section) => section?.section_ui_schema?.['section-id'] === sectionChanges.section_id);
      if (section && !savedSections.includes(section.section_id)) {
        setSavedSections((prev) => [...prev, section.section_id]);
      }
      onAction?.(sectionChanges, 'draft', section);
    },
    [sections, onAction, savedSections]
  )

  const handleSubmit = async () => {
    if (!formHandle) {
      return;
    }
    const isValid = await formHandle.validate();
    if (!isValid) {
      toast.warn(t('fill_required_fields'));
      return;
    }
    onAction?.(undefined, 'submit');
  };

  const handleCancel = () => {
    onCancel?.();
    window.location.reload();
  };

  const handleDraftSave = () => {
    router.push(`/intake-form/${registerType}`)
  }

  return (
    <div className="mx-auto pt-0 pb-6 flex flex-col">
      {submissionId && !showActions && (
        <IntakeFormDeduplicationTabs
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          intakeResultsCount={intakeResults.length}
          regResultsCount={regResults.length}
          t={t}
        />
      )}

      {activeTab === "intake_forms" && (
        <div>
          {(intakeFormHeading || intakeFormDescription) && (
            <div className="pt-6 border-t-2 border-neutral-second mb-4">
              {intakeFormHeading && (
                <h3 className="text-[24px] font-medium leading-[100%] text-neutral-first mb-4">
                  {intakeFormHeading}
                </h3>
              )}
              {intakeFormDescription && (
                <div className="text-secondary-third text-[16px] font-normal leading-[100%] flex flex-col gap-4 whitespace-pre-wrap pr-10">
                  {intakeFormDescription}
                </div>
              )}
            </div>
          )}

          <div className="flex gap-10">
            <div className={`flex-1 flex flex-col gap-4 ${formDetailsCard || showActions ? 'max-w-[calc(100%-380px)]' : ''}`}>
              <IntakeFormSections
                sectionsConfig={sectionsConfig}
                schemaData={schemaData}
                showActions={showActions}
                onSectionSave={handleSectionSave}
                onFormReady={(handle: SectionsFormHandle) => setFormHandle(handle)}
                onCancel={handleCancel}
                onSubmit={handleSubmit}
                onDraftSave={handleDraftSave}
                isSubmitDisabled={formHandle === null || !allSectionsSaved}
                widgetStore={widgetStore}
              />
            </div>

            {(formDetailsCard || showActions) && (
              <div className="shrink-0">
                <FormDetailsCard
                  title={intakeFormHeading}
                  description={intakeFormDescription}
                />

              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === "intake_possible_duplicates" && (
        <div>
          <DeduplicationCardForIntake results={intakeResults} loading={intakeLoading} type="intake-form" t={t} />
        </div>
      )}

      {activeTab === "register_possible_duplicates" && (
        <div>
          <DeduplicationCardForIntake results={regResults} loading={regLoading} type="register" t={t} />
        </div>
      )}
    </div>
  );
}

