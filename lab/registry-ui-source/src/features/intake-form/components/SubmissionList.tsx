'use client';

import { IntakeFormSubmission } from '../types/intake-form';
import { IntakeFormSubmissionCard } from './SubmissionCard';

interface Props {
    submissions: IntakeFormSubmission[];
    registerType: string;
}

export default function IntakeFormSubmissionList({ submissions, registerType }: Props) {
    return (
        <div className="space-y-4">
            {submissions.map((submission) => (
                <IntakeFormSubmissionCard
                    key={submission.submission_id}
                    submission={submission}
                    registerType={registerType}
                />
            ))}
        </div>
    );
}
