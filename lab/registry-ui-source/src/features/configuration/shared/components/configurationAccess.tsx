'use client';
import {createContext,useContext} from 'react';
export type ConfigurationAccess={view:string;create:string;edit:string;delete:string};
const registry={view:'registryConfiguration:view',create:'registryConfiguration:edit',edit:'registryConfiguration:edit',delete:'registryConfiguration:edit'};
const actions=(prefix:string):ConfigurationAccess=>({view:prefix+':view',create:prefix+':create',edit:prefix+':edit',delete:prefix+':delete'});
export const configurationSections=[
 {id:'registry-details',group:'Registry',title:'Registry details',path:'/configuration/registry/details',description:'Manage the registry identity, logo and default settings.',access:registry},
 {id:'registry-themes',group:'Registry',title:'Themes',path:'/configuration/registry/themes',description:'Manage the colours and visual identity used across the registry.',access:registry},
 {id:'registry-languages',group:'Registry',title:'Languages',path:'/configuration/registry/languages',description:'Manage available languages and registry translations.',access:registry},
 {id:'registers',group:'Data and registration',title:'Registers',path:'/configuration/registers',description:'Configure registry definitions, sections, tabs, schemas and scores.',access:actions('registerDefinition')},
 {id:'intake-forms',group:'Data and registration',title:'Registration forms',path:'/configuration/intake-forms',description:'Configure the forms, tabs and sections used for registration.',access:{...actions('intakeFormDefinition'),create:'intakeFormDefinition:edit',delete:'intakeFormDefinition:edit'}},
 {id:'data-models',group:'Data and registration',title:'Data models',path:'/configuration/data-models',description:'Manage the structures used to exchange and process registry data.',access:actions('dataModel')},
 {id:'ingest-key-paths',group:'Incoming data',title:'Key paths',path:'/configuration/ingest-configurations/key-paths',description:'Map incoming fields to the registry data model.',access:actions('ingestKeyPath')},
 {id:'ingest-semantic-patterns',group:'Incoming data',title:'Semantic patterns',path:'/configuration/ingest-configurations/semantic-patterns',description:'Manage how incoming values are interpreted and transformed.',access:{...actions('ingestExpression'),delete:'ingestExpression:edit'}},
 {id:'ingest-manage-subscription',group:'Incoming data',title:'Subscriptions',path:'/configuration/ingest-configurations/manage-subscription',description:'Manage incoming data subscriptions and their activity.',access:{...actions('ingestSubscription'),edit:'ingestSubscription:create',delete:'ingestSubscription:create'}},
 {id:'ingest-templates',group:'Incoming data',title:'Incoming templates',path:'/configuration/ingest-configurations/templates',description:'Manage templates used to import and transform records.',access:actions('ingestTemplate')},
 {id:'outgest-topics',group:'Outgoing data',title:'Topics',path:'/configuration/outgest-configurations/topics',description:'Configure the topics used to share registry data.',access:actions('outgestTopic')},
 {id:'outgest-templates',group:'Outgoing data',title:'Outgoing templates',path:'/configuration/outgest-configurations/templates',description:'Manage the templates used for outgoing registry messages.',access:actions('outgestTemplate')},
 {id:'data-policies',group:'Governance',title:'Data policies',path:'/configuration/data-policies',description:'Configure access rules for the records in each register.',access:{...registry,view:'registerDefinition:view'}},
 {id:'awe-policy-config',group:'Governance',title:'Approval policies',path:'/configuration/awe-policy-config',description:'Manage the approval policies connected to registry workflows.',access:actions('registerDefinition')},
];
export function sectionForPath(path:string){const start=path.indexOf('/configuration');const normalized=start>=0?path.slice(start):path;return configurationSections.find(s=>normalized===s.path||normalized.startsWith(s.path+'/'))||configurationSections[0]}
export const ConfigurationAccessContext=createContext<ConfigurationAccess|null>(null);
export const useConfigurationAccess=()=>useContext(ConfigurationAccessContext);
