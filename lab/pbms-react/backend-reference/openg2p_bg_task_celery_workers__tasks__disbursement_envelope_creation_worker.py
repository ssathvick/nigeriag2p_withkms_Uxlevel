import logging
import uuid
from datetime import date, datetime, timezone
from typing import List

from openg2p_bg_task_models.models import DisbursementEnvelope
from openg2p_bg_task_registry_adapters.factory import RegistryFactory
from openg2p_bg_task_registry_adapters.interface import RegistryInterface
from openg2p_bg_task_registry_adapters.schema import BeneficiaryListSummaryPayload
from openg2p_g2p_bridge_models.schemas import (
    DisbursementEnvelopePayload,
)
from openg2p_pbms_models.models import (
    G2PBeneficiaryList,
    G2PBenefitCodes,
    G2PDisbursementCycle,
    G2PProgramDefinition,
    StatusEnum,
)
from sqlalchemy.orm import sessionmaker

from ..app import celery_app, get_engine
from ..config import Settings
from ..helpers.g2p_bridge_helper import G2PBridgeDisbursementHelper

_config = Settings.get_config()
_logger = logging.getLogger(_config.logging_default_logger_name)
_engine = get_engine()


@celery_app.task(name="disbursement_envelope_creation_worker")
def disbursement_envelope_creation_worker(id: int):
    _logger.info(
        "Starting disbursement envelope creation request for beneficiary list id: %s",
        id,
    )
    pbms_session_maker = sessionmaker(
        bind=_engine.get("db_engine_pbms"), expire_on_commit=False
    )
    bg_task_session_maker = sessionmaker(
        bind=_engine.get("db_engine_bg_task"), expire_on_commit=False
    )

    with pbms_session_maker() as pbms_session, bg_task_session_maker() as bg_task_session:
        beneficiary_list = None
        try:
            beneficiary_list = (
                pbms_session.query(G2PBeneficiaryList)
                .filter(G2PBeneficiaryList.id == id)
                .first()
            )

            program_definition: G2PProgramDefinition = (
                pbms_session.query(G2PProgramDefinition)
                .filter(G2PProgramDefinition.id == beneficiary_list.program_id)
                .first()
            )

            disbursement_cycle: G2PDisbursementCycle = (
                pbms_session.query(G2PDisbursementCycle)
                .filter(
                    G2PDisbursementCycle.id == beneficiary_list.disbursement_cycle_id
                )
                .first()
            )

            try:
                registry_interface: RegistryInterface = (
                    RegistryFactory.get_registry_class(
                        program_definition.target_registry,
                    )
                )

                _logger.info(
                    f"Fetching summary for beneficiary_list_id: {beneficiary_list.beneficiary_list_id}"
                )

                summary_payload: BeneficiaryListSummaryPayload = (
                    registry_interface.get_summary_sync(
                        beneficiary_list.beneficiary_list_id, bg_task_session
                    )
                )
                _logger.debug(
                    "Fetched summary for beneficiary_list_id: %s", summary_payload
                )
            except Exception as e:
                raise Exception(
                    f"Error fetching summary for beneficiary_list_id {beneficiary_list.beneficiary_list_id}: {e}"
                ) from e

            disbursement_envelope_request_message: List[
                DisbursementEnvelopePayload
            ] = construct_disbursement_envelope_request_message(
                pbms_session,
                program_definition,
                disbursement_cycle,
                summary_payload,
                beneficiary_list.approval_date,
            )

            # Use the helper class for envelope creation
            bridge_disbursement_helper = G2PBridgeDisbursementHelper(_config, _logger)
            (
                disbursement_envelope_response,
                error,
            ) = bridge_disbursement_helper.create_disbursement_envelopes(
                disbursement_envelope_request_message
            )
            _logger.debug(
                f"Disbursement envelope response: {disbursement_envelope_response}"
            )
            if error:
                raise Exception(f"Error occurred while creating envelope: {error}")

            disbursement_envelopes: List[
                DisbursementEnvelope
            ] = construct_disbursement_envelopes(
                beneficiary_list, disbursement_envelope_response
            )

            # Bulk insert all the disbursement envelopes
            bg_task_session.add_all(disbursement_envelopes)

            beneficiary_list.envelope_creation_number_of_attempts += 1
            beneficiary_list.envelope_creation_status = StatusEnum.complete.value
            beneficiary_list.envelope_creation_processed_date = datetime.now(
                timezone.utc
            )
            beneficiary_list.disbursement_batch_creation_status = (
                StatusEnum.pending.value
            )

            pbms_session.commit()
            bg_task_session.commit()

        except Exception as e:
            _logger.error(
                f"Exception occurred while processing disbursement envelope creation request: {e}"
            )
            pbms_session.rollback()
            bg_task_session.rollback()

            beneficiary_list.envelope_creation_number_of_attempts += 1
            beneficiary_list.envelope_creation_status = (
                StatusEnum.pending.value
                if beneficiary_list.envelope_creation_number_of_attempts
                < _config.worker_max_attempts
                else StatusEnum.failed.value
            )
            beneficiary_list.envelope_creation_latest_error_code = str(e)
            pbms_session.commit()
            raise e

        _logger.info(
            "Completed disbursement envelope creation for benefitiary_list_id %s" % id
        )


def create_disbursement_envelope_payload(
    benefit_code_id: int,
    total_disbursement_quantity: float,
    program_definition: G2PProgramDefinition,
    disbursement_cycle: G2PDisbursementCycle,
    summary_payload: BeneficiaryListSummaryPayload,
    disbursement_schedule_date: date,
    pbms_session,
) -> DisbursementEnvelopePayload:
    benefit_code: G2PBenefitCodes = (
        pbms_session.query(G2PBenefitCodes)
        .filter(
            G2PBenefitCodes.id == benefit_code_id,
        )
        .first()
    )
    disbursement_envelope_payload = DisbursementEnvelopePayload(
        id=str(uuid.uuid4()),
        benefit_program_id=program_definition.id,
        benefit_program_mnemonic=program_definition.program_mnemonic,
        benefit_program_description=program_definition.description,
        target_registry=program_definition.target_registry,
        cycle_code_mnemonic=disbursement_cycle.cycle_mnemonic,
        benefit_code_id=benefit_code_id,
        benefit_code_mnemonic=benefit_code.benefit_mnemonic,
        benefit_code_description=benefit_code.benefit_description,
        benefit_type=benefit_code.benefit_type,
        disbursement_cycle_id=disbursement_cycle.id,
        number_of_beneficiaries=summary_payload.beneficiary_list_summary.number_of_registrants,
        number_of_disbursements=summary_payload.beneficiary_list_summary.number_of_registrants,
        total_disbursement_quantity=total_disbursement_quantity,
        disbursement_schedule_date=disbursement_schedule_date,
        disbursement_frequency=program_definition.disbursement_frequency.value,
        measurement_unit=benefit_code.measurement_unit,
    )
    return disbursement_envelope_payload


def construct_disbursement_envelope_request_message(
    pbms_session,
    program_definition,
    disbursement_cycle,
    summary_payload,
    disbursement_schedule_date,
) -> List[DisbursementEnvelopePayload]:
    disbursement_envelope_request_message: List[DisbursementEnvelopePayload] = []
    for (
        benefit_code_id,
        total_disbursement_quantity,
    ) in summary_payload.beneficiary_list_summary.total_disbursement_quantity.items():
        disbursement_envelope_payload = create_disbursement_envelope_payload(
            int(benefit_code_id),
            total_disbursement_quantity,
            program_definition,
            disbursement_cycle,
            summary_payload,
            disbursement_schedule_date,
            pbms_session,
        )
        disbursement_envelope_request_message.append(disbursement_envelope_payload)
    return disbursement_envelope_request_message


def construct_disbursement_envelopes(
    beneficiary_list, disbursement_envelope_response
) -> List[DisbursementEnvelope]:
    disbursement_envelopes: List[DisbursementEnvelope] = []
    for disbursement_envelope_reponse_message in disbursement_envelope_response.message:
        disbursement_envelope = DisbursementEnvelope(
            id=disbursement_envelope_reponse_message.id,
            beneficiary_list_id=beneficiary_list.beneficiary_list_id,
            benefit_program_id=disbursement_envelope_reponse_message.benefit_program_id,
            benefit_program_mnemonic=disbursement_envelope_reponse_message.benefit_program_mnemonic,
            benefit_code_id=disbursement_envelope_reponse_message.benefit_code_id,
            benefit_type=disbursement_envelope_reponse_message.benefit_type.value,
            disbursement_cycle_id=disbursement_envelope_reponse_message.disbursement_cycle_id,
            cycle_code_mnemonic=disbursement_envelope_reponse_message.cycle_code_mnemonic,
            number_of_beneficiaries=disbursement_envelope_reponse_message.number_of_beneficiaries,
            number_of_disbursements=disbursement_envelope_reponse_message.number_of_disbursements,
            total_disbursement_quantity=disbursement_envelope_reponse_message.total_disbursement_quantity,
            measurement_unit=disbursement_envelope_reponse_message.measurement_unit,
            disbursement_schedule_date=disbursement_envelope_reponse_message.disbursement_schedule_date,
        )
        disbursement_envelopes.append(disbursement_envelope)
        _logger.info(
            f"Envelope creation successful for disbursement envelope id: {disbursement_envelope_reponse_message.id}"
        )
    return disbursement_envelopes
