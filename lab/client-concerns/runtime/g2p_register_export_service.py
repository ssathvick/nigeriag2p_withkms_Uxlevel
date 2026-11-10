from datetime import datetime, timedelta

from openg2p_fastapi_common.context import dbengine
from openg2p_fastapi_common.service import BaseService
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from ..errors import G2PRegistryErrorCodes, G2PRegistryException
from ..models import (
    ExportSelectionModeEnum,
    G2PRegisterDefinition,
    G2PRegisterExportDataQueue,
    ProcessStatusEnum,
)
from ..schemas import (
    ExportRegisterRecordsData,
    ExportRegisterRecordsRequestPayload,
    RegisterExportQueueData,
)


class G2PRegisterExportService(BaseService):
    async def enqueue_export(
        self,
        payload: ExportRegisterRecordsRequestPayload,
        *,
        requested_by: str,
        policy_mnemonics: list[str] | None,
        data_policies: list[dict] | None,
        batch_size: int,
        search_text: str | None = None,
        filter_by: dict | str | None = None,
        sort_by: str | None = None,
    ) -> ExportRegisterRecordsData:
        session_maker = async_sessionmaker(dbengine.get(), expire_on_commit=False)
        async with session_maker() as session:
            register_exists = await session.scalar(
                select(G2PRegisterDefinition.register_id).where(
                    G2PRegisterDefinition.register_id == payload.register_id
                )
            )
            if not register_exists:
                raise G2PRegistryException(
                    code=G2PRegistryErrorCodes.REGISTER_NOT_FOUND.value[1],
                    message=G2PRegistryErrorCodes.REGISTER_NOT_FOUND.value[0],
                )

            selected_ids = [
                record_id
                for record_id in (payload.selected_internal_record_ids or [])
                if record_id
            ]
            if selected_ids:
                selection_mode = ExportSelectionModeEnum.SELECTED
                # Preserve selection order while removing accidental duplicates.
                selected_ids = list(dict.fromkeys(selected_ids))
                search_text = None
                filter_by = None
                sort_by = None
            else:
                selection_mode = ExportSelectionModeEnum.SEARCH_FILTER
                selected_ids = None
                search_text = search_text or None
                filter_by = filter_by or None
                sort_by = sort_by or None

            queue_item = G2PRegisterExportDataQueue(
                register_id=payload.register_id,
                requested_by=requested_by,
                queued_at=datetime.now(),
                export_format=payload.export_format.value,
                selection_mode=selection_mode.value,
                selected_internal_record_ids=selected_ids,
                search_text=search_text,
                filter_by=filter_by,
                sort_by=sort_by,
                policy_mnemonics=policy_mnemonics or [],
                data_policies=data_policies or [],
                batch_size=max(1, batch_size),
                export_status=ProcessStatusEnum.PENDING.value,
            )
            session.add(queue_item)
            await session.commit()
            await session.refresh(queue_item)

            return ExportRegisterRecordsData(
                export_id=queue_item.export_id,
                status=ProcessStatusEnum.PENDING,
            )

    async def get_exports_for_user(
        self,
        *,
        requested_by: str,
        current_page: int,
        page_size: int,
        visibility_days: int,
    ) -> tuple[list[RegisterExportQueueData], int]:
        session_maker = async_sessionmaker(dbengine.get(), expire_on_commit=False)
        async with session_maker() as session:
            cutoff = datetime.now() - timedelta(days=max(1, visibility_days))
            conditions = [
                G2PRegisterExportDataQueue.requested_by == requested_by,
                G2PRegisterExportDataQueue.queued_at >= cutoff,
            ]
            total_items = await session.scalar(
                select(func.count())
                .select_from(G2PRegisterExportDataQueue)
                .where(*conditions)
            )
            offset = (max(1, current_page) - 1) * max(1, page_size)
            queue_items = (
                await session.execute(
                    select(G2PRegisterExportDataQueue)
                    .where(*conditions)
                    .order_by(G2PRegisterExportDataQueue.queued_at.desc())
                    .offset(offset)
                    .limit(max(1, page_size))
                )
            ).scalars().all()

            now = datetime.now()
            exports: list[RegisterExportQueueData] = []
            for queue_item in queue_items:
                is_completed = (
                    queue_item.export_status == ProcessStatusEnum.COMPLETED.value
                    or queue_item.export_status == ProcessStatusEnum.COMPLETED
                )
                url_is_valid = (
                    queue_item.file_url_expires_at is None
                    or queue_item.file_url_expires_at > now
                )
                exports.append(
                    RegisterExportQueueData(
                        export_id=queue_item.export_id,
                        register_id=queue_item.register_id,
                        export_status=queue_item.export_status,
                        queued_at=queue_item.queued_at,
                        export_latest_timestamp=queue_item.export_latest_timestamp,
                        total_records_exported=queue_item.total_records_exported,
                        export_format=queue_item.export_format,
                        file_presigned_url=(
                            queue_item.file_presigned_url
                            if is_completed and url_is_valid
                            else None
                        ),
                        file_url_expires_at=queue_item.file_url_expires_at,
                        export_latest_error_code=queue_item.export_latest_error_code,
                    )
                )

            return exports, int(total_items or 0)
