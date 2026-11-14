"use client";

import {
  SectionsContainer,
  WidgetProvider,
} from '@openg2p/registry-widgets';
import type { SectionChanges } from '@openg2p/registry-widgets';
import { dataSourceRequestHandler } from '@/features/register/utils/dataSourceRequestHandler';
import { useTranslations } from 'next-intl';

interface Props {
  confirmation?: React.ReactNode;
  sectionsConfig: any[];
  schemaData: any;
  showActions: boolean;
  onSectionSave: (sectionChanges: SectionChanges) => void;
  onFormReady: (handle: any) => void;
  onCancel: () => void;
  onSubmit: () => void;
  onDraftSave: () => void;
  isSubmitDisabled: boolean;
  widgetStore: any;
  onDirtyChange?: (sectionId:string,isDirty:boolean)=>void;
}

export default function IntakeFormSections({
  confirmation,
  sectionsConfig,
  schemaData,
  showActions,
  onSectionSave,
  onFormReady,
  onCancel,
  onSubmit,
  onDraftSave,
  isSubmitDisabled,
  widgetStore,
  onDirtyChange,
}: Props) {
  const t = useTranslations();

  return (
    <WidgetProvider
      theme={{colors:{primary:'#1a6554',primaryDark:'#155447',primaryLight:'#edf5ef',primaryAccent:'#1a6554'},section:{titleColor:'#155447',dividerColor:'#bfd7cb'},button:{primaryBorder:'#1a6554',primaryColor:'#155447'},widget:{inputFocusBorderColor:'#1a6554',tableEditingRowBg:'#edf5ef'}}}
      store={widgetStore}
      schemaData={schemaData}
      translate={(key,values)=>t.has(key)?t(key,values):key}
      dataSourceRequestHandler={dataSourceRequestHandler}
    >
      <div className="flex flex-col gap-1">
        <SectionsContainer
          sections={sectionsConfig}
          mode="IntakeForm"
          isDraft={showActions}
          onSectionSave={onSectionSave}
          onFormReady={onFormReady}
          onSectionDirtyChange={onDirtyChange}
        />

        {confirmation}
        {showActions && (
          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              onClick={onCancel}
              className="px-8 py-2.5 rounded-full bg-secondary-second text-neutral-first font-bold text-[14px] hover:bg-secondary-third transition-colors"
            >
              {t('cancel')}
            </button>
            <button
              onClick={onDraftSave}
              className="px-8 py-2.5 rounded-full bg-secondary-second text-neutral-first font-bold text-[14px] hover:bg-secondary-third transition-colors"
            >
              {t('save_draft')}
            </button>

            <button
              onClick={onSubmit}
              className="px-8 py-2.5 rounded-full bg-neutral-first text-neutral-second font-bold text-[14px]
                   disabled:bg-secondary-second disabled:text-secondary-third disabled:cursor-not-allowed"
              disabled={isSubmitDisabled}
            >
              {t('submit')}
            </button>
          </div>
        )}
      </div>
    </WidgetProvider>
  );
}
