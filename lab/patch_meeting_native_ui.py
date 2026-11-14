from pathlib import Path
ROOT=Path(__file__).parent/'registry-ui-source/src'
def change(file,fn):
 p=ROOT/file;s=p.read_text(encoding='utf-8-sig');p.write_text(fn(s),encoding='utf-8')
# Keep existing cards and colors, adding the explicit third decision and reason validation.
for file in ['features/approval/components/ApprovalCard.tsx','features/approval/components/ApprovalList.tsx','features/approval/hooks/useApprovals.ts']:
 change(file,lambda s:s.replace("'approve' | 'reject'","'approve' | 'reject' | 'return'"))
def approval(s):
 s=s.replace("        setSubmittingAction(action);","        if (action !== 'approve' && !comment.trim()) { setReasonError('Enter a reason before returning or rejecting this record.'); return; }\n        setReasonError('');\n        setSubmittingAction(action);",1)
 s=s.replace("    const [comment, setComment] = useState('');","    const [comment, setComment] = useState('');\n    const [reasonError,setReasonError] = useState('');")
 s=s.replace('<div className="flex items-center gap-4 pt-2">','''{reasonError && <p role="alert" className="text-red-700 text-sm">{reasonError}</p>}
                    <div className="flex flex-wrap items-center gap-3 pt-2">
                        <button type="button" disabled={isInteractionDisabled} onClick={() => handleAction('return')} className="rounded-full px-4 py-2 text-sm font-medium bg-amber-100 text-amber-900 disabled:opacity-50">{submittingAction === 'return' ? t('loading') : 'Return for correction'}</button>''')
 s=s.replace("{submittingAction === 'reject' ? t('loading') : t('reject')}","{submittingAction === 'reject' ? t('loading') : 'Reject permanently'}")
 s=s.replace("{decisionApproved ? t('approve') : t('reject')}","{task.decision_action === 'return' ? 'Returned for correction' : decisionApproved ? t('approve') : 'Rejected permanently'}")
 return s
change('features/approval/components/ApprovalCard.tsx',approval)
# Filter before backend pagination, with URL state shared by dashboard deep links.
def use_tasks(s):
 s=s.replace('    searchText?: string;','    searchText?: string;\n    status?: string;').replace("    searchText = '',","    searchText = '',\n    status = '',")
 s=s.replace('[searchText, artifactType]','[searchText, artifactType, status]').replace('                artifact_type: artifactType,','                artifact_type: artifactType,\n                status: status === "all" ? undefined : status || undefined,').replace('[artifactType, searchText, currentPage, pageSize]','[artifactType, searchText, currentPage, pageSize, status]');return s
change('features/approval/hooks/useMyTasks.ts',use_tasks)
change('features/approval/components/TasksListView.tsx',lambda s:s.replace("import { useCallback, useMemo }", "import { WorkflowFilters } from '@/components/shared/Workflow';\nimport { useCallback, useMemo }").replace('        artifactType,\n        searchText:',"        artifactType,\n        status: searchParams.get('status') || 'all',\n        searchText:").replace('            <div className="px-7.5 pb-10">','            <WorkflowFilters tasks />\n            <div className="px-7.5 pb-10">'))
def use_intake(s):
 s=s.replace('        searchText?: string;','        searchText?: string;\n        status?: string;').replace('                search_text: params?.searchText,','                search_text: params?.searchText,\n                filter_by: params?.status && params.status !== "all" ? JSON.stringify({workflow_status:params.status}) : "",').replace('[registerId, params?.searchText, params?.currentPage, params?.pageSize]','[registerId, params?.searchText, params?.currentPage, params?.pageSize, params?.status]');return s
change('features/intake-form/hooks/useIntakeSubmissions.ts',use_intake)
change('app/[locale]/intake-form/[type]/page.tsx',lambda s:s.replace("import { useState } from 'react';","import { useState,useEffect } from 'react';\nimport { WorkflowFilters } from '@/components/shared/Workflow';").replace('            searchText: searchQuery,','            searchText: searchQuery,\n            status: searchParams.get("status") || "all",').replace('    const pageSize =','    useEffect(()=>setCurrentPage(1),[searchParams.get("status")]);\n    const pageSize =').replace('            <div className="px-7.5">','            <WorkflowFilters draft />\n            <div className="px-7.5">'))
def use_change(s):
 s=s.replace('    searchText?: string;','    searchText?: string;\n    status?: string;').replace("    searchText = '',","    searchText = '',\n    status = 'all',").replace('[searchText]','[searchText,status]').replace('                search_text: searchText,','                search_text: searchText,\n                filter_by: status === "all" ? "" : JSON.stringify({workflow_status:status}),');return s
change('features/change-request/hooks/useChangeRequestSearch.ts',use_change)
change('app/[locale]/change-request/page.tsx',lambda s:s.replace("import { useCallback }", "import { WorkflowFilters } from '@/components/shared/Workflow';\nimport { useCallback }").replace('        searchText: searchQuery,','        searchText: searchQuery,\n        status: searchParams.get("status") || "all",').replace('            <div className="px-7.5">','            <WorkflowFilters />\n            <div className="px-7.5">'))
# Short searchable references on cards; technical IDs are available on demand in details.
change('features/intake-form/types/intake-form.ts',lambda s:s.replace('    record_name: string | null;','    application_reference?: string;\n    remarks?: string|null;\n    record_name: string | null;',1))
def submission_card(s):
 s=s.replace("import { Link }", "import { WorkflowStatus } from '@/components/shared/Workflow';\nimport { Link }")
 s=s.replace('                <h3','                <div className="flex justify-between items-start gap-4"><h3',1).replace('                </h3>','                </h3><WorkflowStatus approval={submission.approval_status} draft={submission.draft_status} summary={submission.awe_request_status_summary}/></div>',1)
 s=s.replace("<KeyValue label={t('submission_id')} value={submission.submission_id} />","<KeyValue label=\"Reference\" value={submission.application_reference || 'Not recorded'} />").replace("                            <KeyValue label={t('form_id')} value={submission.form_id} />",'')
 s=s.replace('grid grid-cols-4','grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4');return s
change('features/intake-form/components/SubmissionCard.tsx',submission_card)
def header(s):
 s=s.replace('import Image from',"import { PrivateIdentifier,WorkflowStatus } from '@/components/shared/Workflow';\nimport Image from",1)
 s=s.replace("{t('intake_submission')}\n            </h3>","{submission?.record_name || t('intake_submission')}\n            </h3>\n            <WorkflowStatus approval={submission?.approval_status} draft={submission?.draft_status} summary={submission?.awe_request_status_summary}/>")
 s=s.replace('{submission?.submission_id}\n                </span>','<PrivateIdentifier value={submission?.submission_id}/>\n                </span>',1)
 marker='            <div className="flex w-full overflow-hidden">'
 start=s.index('const InfoSection');s=s[:start]+s[start:].replace(marker,'            <div className="flex gap-4"><span className="w-1/2">Reference:</span><strong>{submission?.application_reference || "Not recorded"}</strong></div>\n'+marker,1)
 return s
change('features/intake-form/components/SubmissionHeader.tsx',header)
def dedup(s):
 s="import {InfoHint} from '@/components/shared/Workflow';\n"+s
 s=s.replace('{t("intake_possible_duplicates")}','Intake Duplicates<InfoHint text="Possible matches in other intake submissions awaiting registration. Compare their details before deciding."/>').replace('{t("register_possible_duplicates")}','Existing Duplicates<InfoHint text="Possible matches in the approved master registry. Compare the existing household or individual before deciding."/>')
 return s
change('features/intake-form/components/IntakeFormDeduplicationTabs.tsx',dedup)
# Permanent rejection stays read-only; returned intake displays its feedback and native editor.
change('features/intake-form/components/IntakeFormSubmissionView.tsx',lambda s:s.replace('                            <MultiSectionAccordionForms','                            {submission?.remarks && <section className="rounded-lg border border-amber-200 bg-amber-50 p-4"><h2 className="font-semibold">Review feedback</h2><p className="whitespace-pre-wrap">{submission.remarks}</p></section>}\n                            <MultiSectionAccordionForms',1))
# Save draft exits the already-saved form; optional empty sections no longer block submission.
change('features/intake-form/components/MultiSectionAccordionForms.tsx',lambda s:s.replace("isSubmitDisabled={formHandle === null || !allSectionsSaved}","isSubmitDisabled={formHandle === null}").replace("'max-w-[calc(100%-380px)]'","'lg:max-w-[calc(100%-380px)]'").replace('className="flex gap-10"','className="flex flex-col lg:flex-row gap-10"'))
change('features/intake-form/components/IntakeFormSections.tsx',lambda s:s.replace('            {/* <button\n              onClick={onDraftSave}','            <button\n              onClick={onDraftSave}').replace("{t('save_draft')}\n            </button> */}","{t('save_draft')}\n            </button>"))
print('Native workflow components updated.')
