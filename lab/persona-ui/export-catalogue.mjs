import {modules} from './src/catalogue.js';
import fs from 'node:fs';
fs.writeFileSync('../sitewide-ui/modules.json',JSON.stringify(modules,null,2));
