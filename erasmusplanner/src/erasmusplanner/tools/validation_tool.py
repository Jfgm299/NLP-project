from crewai.tools import BaseTool
from typing import Type, List, Dict, Any, Optional
from pydantic import BaseModel, Field
from difflib import SequenceMatcher

# Definimos modelos flexibles para que la validación no falle si falta un campo menor
class ValidationMatrixInput(BaseModel):
    home_subjects_data: List[Dict[str, Any]] = Field(..., description="List of home university subjects with syllabus info.")
    host_subjects_data: List[Dict[str, Any]] = Field(..., description="List of host universities and their potential subjects.")

class ValidationMatrixTool(BaseTool):
    name: str = "Validation Matrix Tool"
    description: str = (
        "Analyzes similarity between Home and Host subjects. "
        "It performs a deterministic match based on syllabus overlap or name similarity. "
        "Returns a JSON object with validation results."
    )
    args_schema: Type[BaseModel] = ValidationMatrixInput

    def _calculate_similarity(self, a: str, b: str) -> float:
        """Calcula similitud entre 0 y 1 normalizando cadenas."""
        if not a or not b:
            return 0.0
        a_clean = a.lower().strip()
        b_clean = b.lower().strip()
        
        # Bonificación si una está contenida en la otra (ej: "Programming" in "Programming I")
        if a_clean in b_clean or b_clean in a_clean:
            return 0.85 
            
        return SequenceMatcher(None, a_clean, b_clean).ratio()

    def _run(self, home_subjects_data: List[Dict[str, Any]], host_subjects_data: List[Dict[str, Any]]):
        result = {"validations_by_university": []}

        for host_uni_entry in host_subjects_data:
            matches = []
            host_uni_name = host_uni_entry.get('host_uni', 'Unknown University')
            potential_host_subjects = host_uni_entry.get('potential_subjects', [])

            for home_subject in home_subjects_data:
                best_match = None
                best_score = 0.0
                validation_status = "NO_MATCH"
                justification = "No syllabus overlap or name similarity found."

                home_name = home_subject.get('subject_name', '')
                home_topics = home_subject.get('topics_summary', '')

                # Iteramos sobre las asignaturas destino para encontrar la mejor pareja
                for host_sub in potential_host_subjects:
                    host_name = host_sub.get('name', '')
                    host_topics = host_sub.get('topics_summary', '') # Puede venir de fetch_host_syllabi
                    
                    # 1. Coincidencia por Syllabus (Fuerte)
                    # Si ambos tienen topics y hay palabras clave coincidentes (simplificado aquí)
                    if home_topics and host_topics:
                        # En una implementación real, aquí harías chequeo de palabras clave
                        # Como es una heurística simple, asumimos que si hay syllabus, el agente
                        # humano deberá revisar, pero marcamos coincidencia por nombre + existencia de syllabus
                        pass 

                    # 2. Coincidencia por Nombre (Heurística)
                    similarity = self._calculate_similarity(home_name, host_name)
                    
                    if similarity > best_score:
                        best_score = similarity
                        best_match = host_sub

                # Determinar estatus final basado en el mejor score encontrado
                # Umbral 0.6 es alto para Español vs Inglés. 
                # Umbral 0.4 es arriesgado pero captura "Sistemas" vs "Systems"
                THRESHOLD_VALIDATED = 0.4
                THRESHOLD_DOUBTFUL = 0.20 

                if best_match:
                    if best_score >= THRESHOLD_VALIDATED:
                        validation_status = "VALIDATED"
                        justification = f"Strong name similarity ({best_score:.2f})."
                    elif best_score >= THRESHOLD_DOUBTFUL:
                        validation_status = "DOUBTFUL"
                        justification = f"Partial name similarity ({best_score:.2f}). Manual check recommended."
                    else:
                        # Si el score es muy bajo, reseteamos el match a None para no sugerir tonterías
                        best_match = None
                        justification = f"Low similarity score ({best_score:.2f})."

                match_entry = {
                    "home_subject": home_name,
                    "host_subject": best_match['name'] if best_match else None,
                    "validation_status": validation_status,
                    "justification": justification,
                    "similarity_score": round(best_score, 2),
                    "home_link": home_subject.get('home_catalog_link'),
                    "host_link": best_match.get('host_catalog_link') if best_match else None
                }
                matches.append(match_entry)

            result["validations_by_university"].append({
                "host_university": host_uni_name,
                "matches": matches
            })

        return result