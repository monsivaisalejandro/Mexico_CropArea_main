import earthaccess
import os
from typing import List, Tuple, Optional

class Sentinel1Downloader:
    """Manejador optimizado para búsqueda y descarga de datos Sentinel-1."""
    
    def __init__(self):
        self.auth = earthaccess.login()
        self.short_names = ["Sentinel-1A_DP_GRD_HIGH", "Sentinel-1B_DP_GRD_HIGH"]

    def search_granules(
        self, 
        bbox: Tuple[float, float, float, float], 
        temporal: Tuple[str, str],
        limit: Optional[int] = None,
        cloud_hosted: bool = True
    ) -> List:
        """
        Busca gránulos con un límite opcional de resultados.
        
        :param limit: Cantidad máxima de gránulos a recuperar en total.
        """
        all_results = []
        for sn in self.short_names:
            current_limit = limit - len(all_results) if limit else 0
            if limit and current_limit <= 0:
                break

            results = earthaccess.search_data(
                short_name=sn,
                cloud_hosted=cloud_hosted,
                temporal=temporal,
                bounding_box=bbox,
                count=current_limit  # 'count' es el parámetro nativo de earthaccess
            )
            all_results.extend(results)
            
        print(f"Total de gránulos encontrados: {len(all_results)}")
        return all_results

    def download(self, granules: List, output_path: str = "./downloads"):
        """
        Descarga los gránulos en la ruta especificada.
        
        :param output_path: Directorio destino. Se crea automáticamente si no existe.
        """
        if not granules:
            print("No hay gránulos seleccionados para la descarga.")
            return []

        # Asegurar que el directorio existe
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            print(f"Directorio creado: {output_path}")

        # La función download de earthaccess devuelve la lista de rutas locales
        downloaded_files = earthaccess.download(granules, local_path=output_path)
        return downloaded_files
