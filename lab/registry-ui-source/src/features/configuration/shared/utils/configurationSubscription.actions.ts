import { NestedValues } from "@/shared/types/types";

export const CONFIGURATION_SUBSCRIPTION_ACTIONS = {
    view: "ingestSubscription:view",
    create: "ingestSubscription:create",
} as const;

export type ConfigurationSubscriptionAction = NestedValues<typeof CONFIGURATION_SUBSCRIPTION_ACTIONS>;
