from sqlalchemy import JSON as SurveyJSON
from datetime import date

from openg2p_registry_core.models.g2p_intake_form import G2PIntakeForm
from sqlalchemy import Boolean, Date, Integer, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column
from openg2p_registry_core.models import (
    G2PRegister,
    G2PRegisterHistory,
    G2PGeo,
    G2PGeoHistory,
)
from ..services import G2PRegisterDomainServiceHousehold
from .enums import (
    CookingFuelEnum,
    DwellingTypeEnum,
    HeadshipTypeEnum,
    LightingSourceEnum,
    MobilePhoneTypeEnum,
    SanitationTypeEnum,
    TenureStatusEnum,
    WaterSourceTypeEnum,
)


class G2PHousehold:
    location_accuracy_m: Mapped[float] = mapped_column(Numeric, nullable=True)
    location_captured_at: Mapped[str] = mapped_column(String, nullable=True)
    location_capture_source: Mapped[str] = mapped_column(String, nullable=True)


    # household-survey-parity: additive, nullable, shared by intake/master/history.
    survey_serial_number: Mapped[str] = mapped_column(String, nullable=True)
    household_heads_count: Mapped[int] = mapped_column(Integer, nullable=True)
    head_list_complete: Mapped[str] = mapped_column(String, nullable=True)
    major_shock_experienced: Mapped[str] = mapped_column(String, nullable=True)
    shock_types: Mapped[list] = mapped_column(SurveyJSON, nullable=True)
    owns_assets: Mapped[str] = mapped_column(String, nullable=True)
    grows_crops: Mapped[str] = mapped_column(String, nullable=True)
    crops_grown: Mapped[list] = mapped_column(SurveyJSON, nullable=True)
    registration_confirmed: Mapped[str] = mapped_column(String, nullable=True)
    owns_radio: Mapped[str] = mapped_column(String, nullable=True)
    owns_television: Mapped[str] = mapped_column(String, nullable=True)
    owns_generator: Mapped[str] = mapped_column(String, nullable=True)
    owns_mobile_phone: Mapped[str] = mapped_column(String, nullable=True)
    owns_torch_light: Mapped[str] = mapped_column(String, nullable=True)
    owns_kerosene_stove: Mapped[str] = mapped_column(String, nullable=True)
    owns_fixed_telephone: Mapped[str] = mapped_column(String, nullable=True)
    owns_house: Mapped[str] = mapped_column(String, nullable=True)
    owns_land: Mapped[str] = mapped_column(String, nullable=True)
    owns_refrigerator: Mapped[str] = mapped_column(String, nullable=True)
    owns_freezer: Mapped[str] = mapped_column(String, nullable=True)
    owns_sofa: Mapped[str] = mapped_column(String, nullable=True)
    owns_table: Mapped[str] = mapped_column(String, nullable=True)
    owns_hifi: Mapped[str] = mapped_column(String, nullable=True)
    owns_mattress: Mapped[str] = mapped_column(String, nullable=True)
    owns_bed: Mapped[str] = mapped_column(String, nullable=True)
    owns_computer: Mapped[str] = mapped_column(String, nullable=True)
    owns_washing_machine: Mapped[str] = mapped_column(String, nullable=True)
    television_count: Mapped[int] = mapped_column(Integer, nullable=True)
    generator_count: Mapped[int] = mapped_column(Integer, nullable=True)


    sponsor_name: Mapped[str] = mapped_column(String, nullable=True)
    consent_status: Mapped[str] = mapped_column(String, nullable=True)
    respondent_name: Mapped[str] = mapped_column(String, nullable=True)
    enumerator_name: Mapped[str] = mapped_column(String, nullable=True)
    survey_community: Mapped[str] = mapped_column(String, nullable=True)
    health_insurance_status: Mapped[str] = mapped_column(String, nullable=True)
    income_source: Mapped[str] = mapped_column(String, nullable=True)
    monthly_household_income: Mapped[float] = mapped_column(Numeric, nullable=True)

    household_head_internal_record_id: Mapped[str] = mapped_column(
        String, nullable=True, index=True
    )
    household_head_name: Mapped[str] = mapped_column(String, nullable=True)
    headship_type: Mapped[HeadshipTypeEnum] = mapped_column(String, nullable=True)

    husband_dead: Mapped[bool] = mapped_column(
        Boolean, nullable=True, server_default=text("false")
    )
    husband_dead_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    size_total: Mapped[int] = mapped_column(Integer, nullable=True)
    size_adults: Mapped[int] = mapped_column(Integer, nullable=True)
    size_children_u5: Mapped[int] = mapped_column(Integer, nullable=True)
    size_school_age: Mapped[int] = mapped_column(Integer, nullable=True)
    size_elderly: Mapped[int] = mapped_column(Integer, nullable=True)
    number_of_female_members: Mapped[int] = mapped_column(Integer, nullable=True)
    number_of_male_members: Mapped[int] = mapped_column(Integer, nullable=True)
    elderly_member_present: Mapped[bool] = mapped_column(Boolean, nullable=True)

    dwelling_type: Mapped[DwellingTypeEnum] = mapped_column(String, nullable=True)
    roof_material: Mapped[str] = mapped_column(String, nullable=True)
    wall_material: Mapped[str] = mapped_column(String, nullable=True)
    floor_material: Mapped[str] = mapped_column(String, nullable=True)
    tenure_status: Mapped[TenureStatusEnum] = mapped_column(String, nullable=True)
    rooms_count: Mapped[int] = mapped_column(Integer, nullable=True)
    overcrowding_indicator: Mapped[float] = mapped_column(Numeric, nullable=True)

    water_source_type: Mapped[WaterSourceTypeEnum] = mapped_column(String, nullable=True)
    water_distance_minutes: Mapped[int] = mapped_column(Integer, nullable=True)
    sanitation_type: Mapped[SanitationTypeEnum] = mapped_column(String, nullable=True)
    lighting_source: Mapped[LightingSourceEnum] = mapped_column(String, nullable=True)
    cooking_fuel_type: Mapped[CookingFuelEnum] = mapped_column(String, nullable=True)
    mobile_phone_type: Mapped[MobilePhoneTypeEnum] = mapped_column(String, nullable=True)


class G2PRegisterHousehold(G2PRegister, G2PGeo, G2PHousehold):
    __tablename__ = "g2p_register_households"

    def get_search_text_fields(self) -> str:
        """Return household fields used to build search_text."""
        return G2PRegisterDomainServiceHousehold().construct_search_text(self.to_dict())

    def get_record_name_fields(self) -> str:
        """Return household record_name from domain service implementation."""
        return G2PRegisterDomainServiceHousehold().construct_record_name(self.to_dict())


class G2PRegisterHistoryHousehold(G2PRegisterHistory, G2PGeoHistory, G2PHousehold):
    __tablename__ = "g2p_register_history_households"


class G2PIntakeFormHousehold(G2PIntakeForm, G2PRegister, G2PGeo, G2PHousehold):
    __tablename__ = "g2p_intake_form_households"

    def get_search_text_fields(self) -> str:
        """Return household fields used to build search_text."""
        return G2PRegisterDomainServiceHousehold().construct_search_text(self.to_dict())

    def get_record_name_fields(self) -> str:
        """Return household intake record_name from domain service implementation."""
        return G2PRegisterDomainServiceHousehold().construct_intake_record_name(self.to_dict())
