import assert from 'node:assert/strict';
import {seed,stats,entitlement,nextAction,advance,BUDGET} from './src/jos-model.mjs';
const rows=seed();assert.equal(rows.length,4250);assert.equal(new Set(rows.map(r=>r.id)).size,4250);assert.equal(BUDGET.reduce((s,r)=>s+r.amount,0),1500000);assert.equal(4250*25*12,BUDGET[0].amount);
for(const r of rows){assert.match(r.name,/^Sample household/);assert.ok(entitlement(r)<=25);if(r.enrolment!=='Enrolled')assert.equal(entitlement(r),0)}
let r=rows[0];for(let i=0;i<6;i++)r=advance(r);assert.equal(r.payment,'Reconciled');assert.equal(r.history.length,7);assert.equal(nextAction(r),null);assert.equal(entitlement(r),25);assert.equal(rows[0].enrolment,'Review');
let failed=rows.find(r=>r.payment==='Failed');assert.equal(advance(failed).payment,'Ready');const notMet=rows.find(r=>r.condition==='Not met');assert.equal(entitlement(notMet),20);
const before=stats(rows);const after=stats(rows.map(x=>x.id===r.id?r:x));assert.equal(after.received,before.received+25);assert.equal(after.reconciledAmount,before.reconciledAmount+25);assert.equal(after.enrolled,before.enrolled+1);
for(const key of ['Approved','Submitted','Failed','Ready'])assert.equal(stats([{...r,payment:key}]).received,0);assert.equal(stats([{...r,payment:'Confirmed'}]).received,25);assert.equal(stats([{...r,payment:'Confirmed'}]).reconciledAmount,0);
console.log('PASS: budget, synthetic identities, conditional benefit, immutable six-step flow, failed-payment retry and receipt/reconciliation separation.');console.log(JSON.stringify(before));
