'use client';
import ApplicationState from './ApplicationState';
export default function Forbidden(){return <ApplicationState kind="forbidden" title="Access restricted" description="Your role does not have access to this page. Return to the dashboard to see the tools and queues available to your account."/>}
