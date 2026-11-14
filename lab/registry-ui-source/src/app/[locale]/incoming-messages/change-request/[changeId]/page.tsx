"use client";

import { useMemo } from "react";
import { useParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { ChangeRequestDetailsView } from "@/features/change-request/components";

export default function ChangeRequestDetailsPage() {
  const t = useTranslations();
  const { changeId } = useParams<{
    changeId: string;
  }>();

  const breadcrumb = useMemo(
    () => [
      {
        label: t("incoming_messages"),
        href: `/incoming-messages`,
      },
      {
        label: t("change_request"),
        // href: `/change-request`,
      },
      { label: changeId },
    ],
    [changeId, t]
  );

  return (
    <ChangeRequestDetailsView
      changeId={changeId}
      breadcrumb={breadcrumb}
    />
  );
}
