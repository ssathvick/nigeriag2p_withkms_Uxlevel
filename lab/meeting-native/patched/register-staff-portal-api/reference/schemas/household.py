from datetime import date
from typing import Optional

from openg2p_registry_core.schemas import (
    G2PRegisterBaseSchema,
    G2PGeoSchema,
    G2PRegisterHistorySchema,
    G2PGeoHistorySchema,
    G2PIntakeFormSchemaBase,
)
from ..models.enums import (
    CookingFuelEnum,
    DwellingTypeEnum,
    HeadshipTypeEnum,
    LightingSourceEnum,
    MobilePhoneTypeEnum,
    SanitationTypeEnum,
    TenureStatusEnum,
    WaterSourceTypeEnum,
)


class G2PSchemaHousehold:
    location_accuracy_m: Optional[float] = None
    location_captured_at: Optional[str] = None
    location_capture_source: Optional[str] = None


    # household-survey-parity: additive, nullable, shared by intake/master/history.
    survey_serial_number: Optional[str] = None
    household_heads_count: Optional[int] = None
    head_list_complete: Optional[str] = None
    major_shock_experienced: Optional[str] = None
    shock_types: Optional[list] = None
    owns_assets: Optional[str] = None
    grows_crops: Optional[str] = None
    crops_grown: Optional[list] = None
    registration_confirmed: Optional[str] = None
    owns_radio: Optional[str] = None
    owns_television: Optional[str] = None
    owns_generator: Optional[str] = None
    owns_mobile_phone: Optional[str] = None
    owns_torch_light: Optional[str] = None
    owns_kerosene_stove: Optional[str] = None
    owns_fixed_telephone: Optional[str] = None
    owns_house: Optional[str] = None
    owns_land: Optional[str] = None
    owns_refrigerator: Optional[str] = None
    owns_freezer: Optional[str] = None
    owns_sofa: Optional[str] = None
    owns_table: Optional[str] = None
    owns_hifi: Optional[str] = None
    owns_mattress: Optional[str] = None
    owns_bed: Optional[str] = None
    owns_computer: Optional[str] = None
    owns_washing_machine: Optional[str] = None
    television_count: Optional[int] = None
    generator_count: Optional[int] = None


    sponsor_name: Optional[str] = None
    consent_status: Optional[str] = None
    respondent_name: Optional[str] = None
    enumerator_name: Optional[str] = None
    survey_community: Optional[str] = None
    health_insurance_status: Optional[str] = None
    income_source: Optional[str] = None
    monthly_household_income: Optional[float] = None

    household_head_internal_record_id: Optional[str] = None
    household_head_name: Optional[str] = None
    headship_type: Optional[HeadshipTypeEnum] = None

    sponsor_name: Optional[str] = None
    consent_status: Optional[str] = None
    respondent_name: Optional[str] = None
    enumerator_name: Optional[str] = None
    survey_community: Optional[str] = None
    health_insurance_status: Optional[str] = None
    income_source: Optional[str] = None
    monthly_household_income: Optional[float] = None

    husband_dead: Optional[bool] = None
    husband_dead_date: Optional[date] = None

    size_total: Optional[int] = None
    size_adults: Optional[int] = None
    size_children_u5: Optional[int] = None
    size_school_age: Optional[int] = None
    size_elderly: Optional[int] = None
    number_of_female_members: Optional[int] = None
    number_of_male_members: Optional[int] = None
    elderly_member_present: Optional[bool] = None

    dwelling_type: Optional[DwellingTypeEnum] = None
    roof_material: Optional[str] = None
    wall_material: Optional[str] = None
    floor_material: Optional[str] = None
    tenure_status: Optional[TenureStatusEnum] = None
    rooms_count: Optional[int] = None
    overcrowding_indicator: Optional[float] = None

    water_source_type: Optional[WaterSourceTypeEnum] = None
    water_distance_minutes: Optional[int] = None
    sanitation_type: Optional[SanitationTypeEnum] = None
    lighting_source: Optional[LightingSourceEnum] = None
    cooking_fuel_type: Optional[CookingFuelEnum] = None
    mobile_phone_type: Optional[MobilePhoneTypeEnum] = None


class G2PRegisterSchemaHousehold(G2PRegisterBaseSchema, G2PGeoSchema, G2PSchemaHousehold):
    """
    Schema for Household register.
    Inherits fields from G2PRegisterBaseSchema and G2PGeoSchema.
    Attributes inherited from G2PSchemaHousehold are specific to the Household domain.
    """


class G2PRegisterHistorySchemaHousehold(G2PRegisterHistorySchema, G2PGeoHistorySchema, G2PSchemaHousehold):
    """
    Schema for Household history.
    Inherits fields from G2PRegisterHistorySchema and G2PGeoHistorySchema.
    Retain the same household domain fields as the primary register in version snapshots.
    """

    sponsor_name: Optional[str] = None
    consent_status: Optional[str] = None
    respondent_name: Optional[str] = None
    enumerator_name: Optional[str] = None
    survey_community: Optional[str] = None
    health_insurance_status: Optional[str] = None
    income_source: Optional[str] = None
    monthly_household_income: Optional[float] = None

    husband_dead: Optional[bool] = None
    husband_dead_date: Optional[date] = None


class G2PIntakeFormSchemaHousehold(
    G2PIntakeFormSchemaBase, G2PRegisterBaseSchema, G2PGeoSchema, G2PSchemaHousehold
):
    """
    Schema for Household intake form.
    Inherits intake form base, register base, geo, and G2PSchemaHousehold for data collection.
    """
