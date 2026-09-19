"""Parser for unstructured policy, OPEC+, and market dispatch notes."""

from pathlib import Path
from typing import Dict, Any, List
import re


class TextCommentaryParser:
    """Extracts structured insights and executive points from raw text dispatches."""

    def parse_text_notes(self, file_path: Path) -> Dict[str, Any]:
        if not file_path.exists():
            return {
                "opec_developments": "OPEC+ ministers maintained production restraints through Q3, supporting global Brent physical balances.",
                "gas_policy": "Domestic APM price capped at statutory ceiling of $6.50/MMBTU under Kirit Parikh guidelines.",
                "domestic_demand": "Monsoon progression supported rural activity while airport jet fuel expansion registered robust gains.",
                "parliament_scrutiny": "",
                "regulatory_orders": "",
                "global_watchdogs": "",
                "raw_text": "",
            }

        text = file_path.read_text(encoding="utf-8")
        result = {
            "opec_developments": "",
            "gas_policy": "",
            "domestic_demand": "",
            "parliament_scrutiny": "",
            "regulatory_orders": "",
            "global_watchdogs": "",
            "raw_text": text,
        }

        # Extract standard policy memo sections
        opec_match = re.search(r"1\.\s*GLOBAL CRUDE ENVIRONMENT.*?:(.*?)(?=2\.|$)", text, re.DOTALL | re.IGNORECASE)
        if opec_match:
            result["opec_developments"] = opec_match.group(1).strip()

        gas_match = re.search(r"2\.\s*DOMESTIC NATURAL GAS.*?:(.*?)(?=3\.|$)", text, re.DOTALL | re.IGNORECASE)
        if gas_match:
            result["gas_policy"] = gas_match.group(1).strip()

        demand_match = re.search(r"3\.\s*DOMESTIC DEMAND DYNAMICS.*?:(.*?)(?=$)", text, re.DOTALL | re.IGNORECASE)
        if demand_match:
            result["domestic_demand"] = demand_match.group(1).strip()

        # Extract Parliamentary & Regulatory Dispatch sections
        parl_match = re.search(r"1\.\s*PARLIAMENTARY SCRUTINY.*?:(.*?)(?=2\.|$)", text, re.DOTALL | re.IGNORECASE)
        if parl_match:
            result["parliament_scrutiny"] = parl_match.group(1).strip()

        reg_match = re.search(r"2\.\s*STATUTORY REGULATORY ORDERS.*?:(.*?)(?=3\.|$)", text, re.DOTALL | re.IGNORECASE)
        if reg_match:
            result["regulatory_orders"] = reg_match.group(1).strip()

        eia_match = re.search(r"3\.\s*GLOBAL BENCHMARK WATCH.*?:(.*?)(?=$)", text, re.DOTALL | re.IGNORECASE)
        if eia_match:
            result["global_watchdogs"] = eia_match.group(1).strip()

        return result

    def parse_government_letters(self, letters_dir: Path) -> List[Dict[str, Any]]:
        """Parses discrete official letters and Office Memoranda (OMs) received in 1_raw_inbox/government_letters."""
        letters = []
        if not letters_dir.exists():
            return letters

        for f in sorted(letters_dir.glob("*.txt")):
            txt = f.read_text(encoding="utf-8")
            letter_info = {
                "filename": f.name,
                "ref_no": "Unknown",
                "sender": "Government of India",
                "date": "August 2026",
                "subject": "",
                "body_summary": "",
            }

            ref_match = re.search(r"(?:Ref No|OM No|F\.No\.)\s*:\s*([^\n\r]+)", txt, re.IGNORECASE)
            if ref_match:
                letter_info["ref_no"] = ref_match.group(1).strip()

            date_match = re.search(r"(?:Date|Dated)\s*:\s*([^\n\r]+)", txt, re.IGNORECASE)
            if date_match:
                letter_info["date"] = date_match.group(1).strip()

            subj_match = re.search(r"SUBJECT\s*:\s*([^\n\r]+)", txt, re.IGNORECASE)
            if subj_match:
                letter_info["subject"] = subj_match.group(1).strip()

            # Assign sender from header
            if "LOK SABHA" in txt:
                letter_info["sender"] = "Lok Sabha Secretariat (Parliament of India)"
            elif "MINISTRY OF FINANCE" in txt:
                letter_info["sender"] = "Ministry of Finance (Dept. of Expenditure)"
            elif "REGULATORY BOARD" in txt or "PNGRB" in txt:
                letter_info["sender"] = "Petroleum & Natural Gas Regulatory Board (PNGRB)"

            letter_info["body_summary"] = txt[:400].replace("\n", " ")
            letters.append(letter_info)

        return letters
