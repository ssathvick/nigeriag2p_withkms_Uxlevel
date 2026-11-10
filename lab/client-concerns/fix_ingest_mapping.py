from pathlib import Path
from overlay import deploy,run
root=Path(__file__).parent;name='g2p_intake_register_section_map_service.py';path='/usr/local/lib/python3.12/site-packages/openg2p_registry_core/services/'+name
s=(root/'runtime'/name).read_text();old='''                    G2PRegisterUITabSection.section_id == section_id,
                )
            )
        ).scalar_one_or_none()''';new='''                    G2PRegisterUITabSection.section_id == section_id,
                ).order_by(G2PRegisterUITabSection.tab_id.asc()).limit(1)
            )
        ).scalar_one_or_none()''';assert old in s;s=s.replace(old,new)
(root/'patched'/name).write_text(s)
for deployment in ['register-staff-portal-api','register-celery-worker']:deploy(deployment,'nsipa-intake-section-mapping',{path:s})
