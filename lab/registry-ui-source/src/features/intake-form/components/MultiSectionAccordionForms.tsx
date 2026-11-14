import { useCallback, useMemo, useState, useEffect } from 'react';
import { useTranslations,useLocale } from 'next-intl';
import { useRouter } from '@/i18n/navigation';
import { toast } from 'react-toastify';
import {
  createWidgetStore,
} from '@openg2p/registry-widgets';
import type { SectionChanges } from '@openg2p/registry-widgets';
import type { SectionsFormHandle } from '@openg2p/registry-widgets';
import { IntakeFormSection } from '../types/intake-form';
import FormDetailsCard from './FormDetailsCard';
import HouseholdLocationCapture from './HouseholdLocationCapture';
import { useIntakeDeduplication } from '../hooks/useIntakeDeduplication';
import DeduplicationCardForIntake from './DeduplicationCardForIntake';
import IntakeFormSections from './IntakeFormSections';
import IntakeFormDeduplicationTabs from './IntakeFormDeduplicationTabs';
import {InfoHint} from '@/components/shared/Workflow';

export type SectionStatus = 'Saved' | 'Draft' | null;

export interface AccordionFormsProps {
  formDetailsCard?: boolean;
  sections: IntakeFormSection[];
  form_name?: string;
  form_description?: string;
  schemaData?: any;
  onAction?: (sectionChanges?: SectionChanges, type?: 'submit' | 'draft', section?: IntakeFormSection) => void|Promise<unknown>;
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
  const locale=useLocale();
  const router = useRouter();
  const widgetStore = useMemo(() => createWidgetStore(), []);

  const [householdConfirmed,setHouseholdConfirmed]=useState(false);
  const [formHandle, setFormHandle] = useState<SectionsFormHandle | null>(null);
  const [savedSections, setSavedSections] = useState<string[]>([]);
  const [dirtySections,setDirtySections]=useState<Record<string,boolean>>({});
  const hasUnsavedChanges=Object.values(dirtySections).some(Boolean);
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
    if(registerType==='household'&&!householdConfirmed){toast.warn('Confirm the household records are accurate before submitting for review.');return;}
    if(hasUnsavedChanges){toast.warn('Save each changed section before reviewing and submitting.');return;}
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

  const handleDraftSave = async () => {
    let savedId=submissionId;
    if(hasUnsavedChanges && formHandle){
      const changes=formHandle.getStructuredData();
      for(const change of changes){
        const section=sections.find(s=>s.section_id===change.section_id || s.section_ui_schema?.['section-id']===change.section_id);
        if(!section || !change.section_id || !dirtySections[change.section_id])continue;
        const keys=new Set<string>();
        const collect=(node:any)=>{if(!node||typeof node!=='object')return;if(typeof node['widget-data-path']==='string'){const key=node['widget-data-path'].split('.').pop();if(key&&key!=='records')keys.add(key)};for(const value of Object.values(node)){if(Array.isArray(value))value.forEach(collect);else if(value&&typeof value==='object')collect(value)}};
        collect(section.section_ui_schema);
        const hasValues=change.records.some((row:any)=>row?.edit_action==='DELETE'||[...keys].some(key=>row?.[key]!==undefined&&row?.[key]!==null&&row?.[key]!==''));
        if(!hasValues && !change.files?.length)continue;
        const result=await onAction?.(change,'draft',section);
        if(result===false)return;
        if(result&&typeof result==='object'&&'submission_id' in result)savedId=String(result.submission_id);
      }
    }
    // Reload the saved native draft so refresh and further edits retain its server identity.
    window.location.assign(`/${locale}/intake-form/${registerType}${savedId?'/submission/'+savedId:''}`);
  }

  return (
    <div className="registry-native-form mx-auto pt-0 pb-6 flex flex-col">
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

          <div className="flex flex-col lg:flex-row gap-10">
            <div className={`flex-1 flex flex-col gap-4 ${registerType!=='household'&&(formDetailsCard || showActions) ? 'lg:max-w-[calc(100%-380px)]' : ''}`}>
              <div className="flex flex-wrap gap-3 text-sm" aria-label="Section guidance">{sections.map(section=><span key={section.section_id}>{section.section_description || section.section_mnemonic.replaceAll('_',' ')}<InfoHint text={section.section_id==='hh_composition_headship'?'Record the sponsor, informed consent and respondent before household details. Save a draft before submitting for independent review.':section.section_id==='hh_members'?'Add each household member and their relationship to the head. Supply either age or date of birth. National ID authentication is not connected.':section.section_id.includes('location')?'Enter known location details. Optional location fields can be left blank; coordinates do not verify residence.':'Review known information in this section. Optional fields may be left blank. Save changes before submitting; approved records require an independently reviewed change request.'}/></span>)}</div>

              {showActions&&registerType==='household'&&<HouseholdLocationCapture store={widgetStore} onCaptured={()=>setDirtySections(previous=>({...previous,hh_survey_consent:true}))}/>}
              <IntakeFormSections
                confirmation={showActions&&registerType==='household'&&<label className="flex items-start gap-3 rounded-xl border border-primary-second bg-white p-5 text-sm"><input type="checkbox" className="mt-1 h-5 w-5 shrink-0" checked={householdConfirmed} onChange={e=>setHouseholdConfirmed(e.target.checked)}/><span>I confirm these household records are accurate and understand that registration does not guarantee programme eligibility.</span></label>}
                sectionsConfig={sectionsConfig}
                schemaData={schemaData}
                showActions={showActions}
                onSectionSave={handleSectionSave}
                onFormReady={(handle: SectionsFormHandle) => setFormHandle(handle)}
                onCancel={handleCancel}
                onSubmit={handleSubmit}
                onDraftSave={handleDraftSave}
                isSubmitDisabled={formHandle === null}
                widgetStore={widgetStore}
                onDirtyChange={(id,dirty)=>setDirtySections(previous=>({...previous,[id]:dirty}))}
              />
            </div>

            {registerType!=='household'&&(formDetailsCard || showActions) && (
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
