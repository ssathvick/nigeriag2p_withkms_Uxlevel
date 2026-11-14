'use client';
import ApplicationState from '@/components/shared/ApplicationState';
export default function Error({reset}:{error:Error&{digest?:string};reset:()=>void}){return <ApplicationState kind="error" title="We could not load this page" description="Please try again. Your saved registry records are not changed by this page error." onRetry={reset}/>}
