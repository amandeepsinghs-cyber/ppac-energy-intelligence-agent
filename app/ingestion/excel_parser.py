"""Excel Parser for multi-format OMC operational submissions."""

from pathlib import Path
from typing import List, Tuple
import pandas as pd

from app.canonical.models import (
    HydrocarbonConsumptionRecord,
    ProductType,
    DataStage,
)


class OmcExcelParser:
    """Parses multi-tab OMC sales workbooks with fuzzy header matching."""

    SHEET_PRODUCT_MAPPING = {
        "MS": ProductType.MS,
        "MOTOR SPIRIT": ProductType.MS,
        "PETROL": ProductType.MS,
        "HSD": ProductType.HSD,
        "DIESEL": ProductType.HSD,
        "HIGH SPEED DIESEL": ProductType.HSD,
        "LPG": ProductType.LPG,
        "LIQUEFIED PETROLEUM GAS": ProductType.LPG,
        "ATF": ProductType.ATF,
        "BITUMEN": ProductType.BITUMEN,
        "NAPHTHA": ProductType.NAPHTHA,
    }

    COLUMN_ENTITY_ALIASES = ["entity", "company", "omc", "corporation"]
    COLUMN_VOLUME_ALIASES = ["volume_tmt", "vol_tmt", "sales_tmt", "quantity_tmt", "volume"]
    COLUMN_PRIOR_ALIASES = ["prior_month_tmt", "last_month_tmt", "previous_month_tmt", "prior_tmt"]
    COLUMN_SECTOR_ALIASES = ["sector", "category", "segment"]

    def parse_workbook(
        self, file_path: Path, period_id: str, data_stage: DataStage = DataStage.PROVISIONAL
    ) -> Tuple[List[HydrocarbonConsumptionRecord], List[dict]]:
        """
        Parses all sheets in the workbook.
        Returns:
            records: List of canonical HydrocarbonConsumptionRecord.
            raw_comparisons: List of dicts with current vs prior month for anomaly evaluation.
        """
        records: List[HydrocarbonConsumptionRecord] = []
        comparisons: List[dict] = []

        xl = pd.ExcelFile(file_path)
        file_name = file_path.name

        for sheet_name in xl.sheet_names:
            normalized_sheet = sheet_name.strip().upper()
            product_type = self.SHEET_PRODUCT_MAPPING.get(normalized_sheet)
            if not product_type:
                continue

            df = xl.parse(sheet_name)
            col_map = self._resolve_columns(df.columns)

            if "entity" not in col_map or "volume" not in col_map:
                continue

            for idx, row in df.iterrows():
                entity_val = str(row[col_map["entity"]]).strip()
                vol_val = float(row[col_map["volume"]])
                sector_val = str(row[col_map.get("sector", "Sector")]).strip() if "sector" in col_map else "Total"
                cell_ref = f"Sheet: {sheet_name} (Row {idx + 2})"

                record = HydrocarbonConsumptionRecord(
                    period_id=period_id,
                    data_stage=data_stage,
                    entity_id=entity_val,
                    product_type=product_type,
                    sector=sector_val,
                    volume_tmt=vol_val,
                    source_file=file_name,
                    source_reference=cell_ref,
                )
                records.append(record)

                prior_val = None
                if "prior" in col_map and pd.notna(row[col_map["prior"]]):
                    prior_val = float(row[col_map["prior"]])

                comparisons.append({
                    "entity": entity_val,
                    "product": product_type,
                    "sector": sector_val,
                    "current_volume": vol_val,
                    "prior_volume": prior_val,
                    "source_reference": cell_ref,
                })

        return records, comparisons

    def _resolve_columns(self, columns) -> dict:
        mapping = {}
        for col in columns:
            c_lower = str(col).strip().lower()
            if any(alias in c_lower for alias in self.COLUMN_ENTITY_ALIASES):
                mapping["entity"] = col
            elif any(alias in c_lower for alias in self.COLUMN_PRIOR_ALIASES):
                mapping["prior"] = col
            elif any(alias in c_lower for alias in self.COLUMN_VOLUME_ALIASES):
                mapping["volume"] = col
            elif any(alias in c_lower for alias in self.COLUMN_SECTOR_ALIASES):
                mapping["sector"] = col
        return mapping
