# Language support

The registration shell offers English, Hausa, Yorùbá and Igbo navigation labels. The choice is stored only in the browser and can be changed at any time. The preference may be unavailable when browser storage is disabled. English is the default.

This is a partial preview: forms, programme text, status messages, knowledge content, identity screens and other OpenG2P services remain in English. A visible notice appears when another language is selected. The labels are draft translations requiring native-speaker review, including accessibility testing. Do not claim full language support or use these translations for production decisions. Translate and review the entire beneficiary journey, errors, accessibility text, notifications and approved policy content before release. Maintain translations separately from programme rules and beneficiary data.

The registration installer copies `registration-ui/language.js` into its static directory. Existing deployments need the revised `base.html` and `language.js` installed using their normal release process. No database or identity configuration change is required.
