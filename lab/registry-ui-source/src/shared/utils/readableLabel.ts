import {registryDisplayText} from './registryDisplayText';
/** For labels only. Never apply this fallback to stored values, IDs or schema keys. */
export function readableLabel(value:string){
 const known=registryDisplayText(value);if(known!==value)return known;
 const words=value.replace(/([a-z])([A-Z])/g,'$1 $2').replace(/[_-]+/g,' ').trim();
 return words?words[0].toUpperCase()+words.slice(1):'Field';
}
