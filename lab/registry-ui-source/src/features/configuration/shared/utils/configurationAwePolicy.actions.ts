import { NestedValues } from '@/shared/types/types';

/** Backend AWE policy routes use registerDefinition permissions. */
export const CONFIGURATION_AWE_POLICY_ACTIONS = {
    view: 'registerDefinition:view',
    create: 'registerDefinition:create',
    edit: 'registerDefinition:edit',
    delete: 'registerDefinition:delete',
} as const;

export type ConfigurationAwePolicyAction = NestedValues<typeof CONFIGURATION_AWE_POLICY_ACTIONS>;
