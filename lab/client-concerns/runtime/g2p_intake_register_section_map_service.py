"""Map intake-form sections onto register UI tab/section placements.

Intake ingest writes register history. Version history on the register is
filtered by register ``tab_id`` + ``section_id``. Intake forms often reuse the
same section row; sometimes they use a dedicated intake section (crops). This
service resolves the register placement and, when the two sections differ,
transforms records into the register section shape.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from openg2p_fastapi_common.service import BaseService
from sqlalchemy import select

from ..models import (
    G2PIntakeFormUITab,
    G2PIntakeFormUITabSection,
    G2PRegisterSection,
    G2PRegisterUITabSection,
)

_logger = logging.getLogger("g2p-intake-register-section-map-service")


@dataclass(frozen=True)
class IntakeRegisterSectionMapping:
    intake_section_id: str
    intake_section: G2PRegisterSection
    register_tab_id: str
    register_section_id: str
    register_section: G2PRegisterSection
    section_register_id: str
    needs_transform: bool


class G2PIntakeRegisterSectionMapService(BaseService):
    async def list_form_intake_sections(self, form_id: str, session) -> list[G2PRegisterSection]:
        """Intake UI sections for a form, in tab/section order. Not unique by register."""
        sections = (
            await session.execute(
                select(G2PRegisterSection)
                .join(
                    G2PIntakeFormUITabSection,
                    G2PRegisterSection.section_id == G2PIntakeFormUITabSection.section_id,
                )
                .join(
                    G2PIntakeFormUITab,
                    G2PIntakeFormUITabSection.tab_id == G2PIntakeFormUITab.tab_id,
                )
                .where(G2PIntakeFormUITab.form_id == form_id)
                .order_by(
                    G2PIntakeFormUITab.tab_order.asc(),
                    G2PIntakeFormUITabSection.section_order.asc(),
                    G2PRegisterSection.section_id.asc(),
                )
            )
        ).scalars().all()
        return list(sections)

    async def map_intake_section_to_register(
        self,
        intake_section: G2PRegisterSection,
        subject_register_id: str,
        session,
    ) -> IntakeRegisterSectionMapping | None:
        """Resolve the register tab/section that should own this intake section's history."""
        exact = await self._register_tab_section(
            subject_register_id, intake_section.section_id, session
        )
        if exact:
            return IntakeRegisterSectionMapping(
                intake_section_id=intake_section.section_id,
                intake_section=intake_section,
                register_tab_id=exact.tab_id,
                register_section_id=intake_section.section_id,
                register_section=intake_section,
                section_register_id=intake_section.section_register_id,
                needs_transform=False,
            )

        candidates = await self._register_sections_for_child_register(
            subject_register_id,
            intake_section.section_register_id,
            session,
        )
        chosen = self._pick_register_section(intake_section, candidates)
        if not chosen:
            _logger.warning(
                "No register tab/section for intake section %s on register %s",
                intake_section.section_id,
                subject_register_id,
            )
            return None

        register_section, tab_id = chosen
        return IntakeRegisterSectionMapping(
            intake_section_id=intake_section.section_id,
            intake_section=intake_section,
            register_tab_id=tab_id,
            register_section_id=register_section.section_id,
            register_section=register_section,
            section_register_id=register_section.section_register_id,
            needs_transform=register_section.section_id != intake_section.section_id,
        )

    async def map_form_sections(
        self,
        form_id: str,
        subject_register_id: str,
        session,
    ) -> list[IntakeRegisterSectionMapping]:
        mappings: list[IntakeRegisterSectionMapping] = []
        for intake_section in await self.list_form_intake_sections(form_id, session):
            mapping = await self.map_intake_section_to_register(
                intake_section, subject_register_id, session
            )
            if mapping:
                mappings.append(mapping)
        return mappings

    def transform_records(
        self,
        mapping: IntakeRegisterSectionMapping,
        records: list[dict],
    ) -> list[dict]:
        """Adapt intake records to the register section.

        Most Farmer sections share the same section row (no rewrite). When the
        intake section is a dedicated form schema (crops), field names on the
        row still match the register table; copy them and drop form-only keys.
        """
        if not mapping.needs_transform:
            return [dict(record) for record in records]

        drop = {"submission_id", "section_id"}
        transformed = []
        for record in records:
            transformed.append(
                {key: value for key, value in record.items() if key not in drop}
            )
        return transformed

    def pick_submission_section_payload(
        self,
        mapping: IntakeRegisterSectionMapping,
        section_payloads: list[dict],
    ) -> dict | None:
        """Find the intake submission payload that belongs to a register section."""
        for payload in section_payloads or []:
            if payload.get("section_id") == mapping.register_section_id:
                return payload
        for payload in section_payloads or []:
            if payload.get("section_id") == mapping.intake_section_id:
                return payload
        for payload in section_payloads or []:
            if payload.get("section_register_id") == mapping.section_register_id:
                return payload
        return None

    async def _register_tab_section(
        self,
        subject_register_id: str,
        section_id: str,
        session,
    ) -> G2PRegisterUITabSection | None:
        return (
            await session.execute(
                select(G2PRegisterUITabSection).where(
                    G2PRegisterUITabSection.register_id == subject_register_id,
                    G2PRegisterUITabSection.section_id == section_id,
                )
            )
        ).scalar_one_or_none()

    async def _register_sections_for_child_register(
        self,
        subject_register_id: str,
        section_register_id: str,
        session,
    ) -> list[tuple[G2PRegisterSection, str]]:
        rows = (
            await session.execute(
                select(G2PRegisterSection, G2PRegisterUITabSection.tab_id)
                .join(
                    G2PRegisterUITabSection,
                    G2PRegisterUITabSection.section_id == G2PRegisterSection.section_id,
                )
                .where(
                    G2PRegisterUITabSection.register_id == subject_register_id,
                    G2PRegisterSection.section_register_id == section_register_id,
                )
                .order_by(G2PRegisterUITabSection.section_order.asc())
            )
        ).all()
        return [(row[0], row[1]) for row in rows]

    def _pick_register_section(
        self,
        intake_section: G2PRegisterSection,
        candidates: list[tuple[G2PRegisterSection, str]],
    ) -> tuple[G2PRegisterSection, str] | None:
        if not candidates:
            return None
        if len(candidates) == 1:
            return candidates[0]

        mnemonic_matches = [
            candidate
            for candidate in candidates
            if candidate[0].section_mnemonic == intake_section.section_mnemonic
        ]
        if len(mnemonic_matches) == 1:
            return mnemonic_matches[0]

        if intake_section.is_list:
            list_matches = [
                candidate for candidate in candidates if candidate[0].is_list
            ]
            if len(list_matches) == 1:
                return list_matches[0]

        _logger.warning(
            "Ambiguous register mapping for intake section %s (%s candidates)",
            intake_section.section_id,
            len(candidates),
        )
        return None
