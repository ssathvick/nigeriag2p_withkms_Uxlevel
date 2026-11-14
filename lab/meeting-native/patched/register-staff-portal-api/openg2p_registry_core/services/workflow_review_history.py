from sqlalchemy import text
async def review_history(session, artifact_id):
    result = await session.execute(text("SELECT e.event_type,e.actor,e.occurred_at::text AS occurred_at,e.request_id,e.status,e.stage_order,COALESCE(c.comment,h.reason) AS reason FROM awe_req_events e LEFT JOIN g2p_registry_return_history h ON h.event_id=e.event_id LEFT JOIN g2p_registry_review_comments c ON c.event_id=e.event_id WHERE e.artifact_id=:id AND e.applied=true AND (e.event_type IN ('stage_started','stage_completed','request_approved','request_rejected','request_returned','request_cancelled') OR e.event_type LIKE 'decision_%') ORDER BY e.occurred_at,e.received_at"), {"id":artifact_id})
    events = [dict(row._mapping) for row in result]
    exists = (await session.execute(text("SELECT to_regclass('public.g2p_mbr_source_archive')"))).scalar()
    if exists:
        old = await session.execute(text("SELECT 'decision_' || (d.body->>'action') AS event_type,d.body->>'actor' AS actor,d.body->>'created_at' AS occurred_at,d.body->>'request_id' AS request_id,d.body->>'action' AS status,(d.body->>'stage_order')::integer AS stage_order,d.body->>'comment' AS reason FROM g2p_mbr_source_archive d JOIN g2p_mbr_source_archive r ON r.source_db='awe' AND r.source_table='approval_request' AND r.body->>'id'=d.body->>'request_id' WHERE d.source_db='awe' AND d.source_table='approval_decision' AND r.body->>'artifact_id'=:id"), {"id":artifact_id})
        events += [dict(row._mapping) for row in old]
    return sorted(events, key=lambda e:e.get('occurred_at') or '')
