import { CONFIGURATION_REGISTERS_ACTIONS } from "./configurationRegisters.actions";
import { CONFIGURATION_REGISTRY_ACTIONS } from "./configurationRegistry.actions";

// TODO add for ingest, outgest, data model once the config pages are done
export const CONFIG_VIEW_ACTIONS = [
    CONFIGURATION_REGISTRY_ACTIONS.view,
    CONFIGURATION_REGISTERS_ACTIONS.view,
] as const;

