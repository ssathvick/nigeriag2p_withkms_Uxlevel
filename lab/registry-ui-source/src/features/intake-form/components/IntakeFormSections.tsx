"use client";

import {
  SectionsContainer,
  WidgetProvider,
} from '@openg2p/registry-widgets';
import type { SectionChanges } from '@openg2p/registry-widgets';
import { dataSourceRequestHandler } from '@/features/register/utils/dataSourceRequestHandler';
import { useTranslations } from 'next-intl';

interface Props {
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
}

export default function IntakeFormSections({
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
}: Props) {
  const t = useTranslations();

  return (
    <WidgetProvider
      store={widgetStore}
      schemaData={schemaData}
      translate={t}
      dataSourceRequestHandler={dataSourceRequestHandler}
    >
      <div className="flex flex-col gap-1">
        <SectionsContainer
          sections={sectionsConfig}
          mode="IntakeForm"
          isDraft={showActions}
          onSectionSave={onSectionSave}
          onFormReady={onFormReady}
        />

        {showActions && (
          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              onClick={onCancel}
              className="px-8 py-2.5 rounded-full bg-secondary-second text-neutral-first font-bold text-[14px] hover:bg-secondary-third transition-colors"
            >
              {t('cancel')}
            </button>
            {/* <button
              onClick={onDraftSave}
              className="px-8 py-2.5 rounded-full bg-secondary-second text-neutral-first font-bold text-[14px] hover:bg-secondary-third transition-colors"
            >
              {t('save_draft')}
            </button> */}

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
