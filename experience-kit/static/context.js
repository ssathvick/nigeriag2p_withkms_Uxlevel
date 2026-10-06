(function(root){'use strict';const presets=root.NG2PKnowledgeContext;const config=root.OpenG2PExperience||{};
root.NG2PKnowledgeContext={relatedGuides:presets.relatedGuides,resolve(s={}){
 if(s.explicit?.module&&s.explicit?.stage)return presets.resolve(s);
 const rule=(config.screenMappings||[]).find(r=>(!r.hostname||r.hostname===s.hostname)&&(!r.path_prefix||(s.path||'/').startsWith(r.path_prefix))&&(!r.hash_contains||(s.hash||'').includes(r.hash_contains)));
 if(rule)return presets.resolve({...s,explicit:{module:rule.module,stage:rule.stage}});
 return presets.resolve(s);
}};})(window);
