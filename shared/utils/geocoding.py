# shared/utils/geocoding.py
"""
Geocoding utilities for Oregon SQM sites
"""

import requests
import time
import json
from typing import Dict, List, Tuple, Optional
import logging
import geocoder

logger = logging.getLogger(__name__)

class OregonGeocoder:
    """Geocode Oregon SQM site locations"""
    
    def __init__(
            self,
        ):
        """
        Initialize the OregonGeocoder with optional caching
        """
        self.cache_file = "shared/data/geospatial/sites_geocodes.csv"
        
        self.cache = self._load_cache() if use_cache else {}
        
    def _load_cache(self) -> Dict:
        """Load geocoding cache to avoid repeat API calls"""
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _save_cache(self):
        """Save geocoding cache"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def geocode_site(
            self,
            site_name: str,
            state: str = "Oregon"
        ) -> Optional[Tuple[float, float]]:
        """Geocode a single site name to lat/lon coordinates using geocoder library (OSM)"""
        # Lazy import so rest of module works even if dependency not yet installed
        
        cache_key = f"{site_name}, {state}"
        if cache_key in self.cache:
            logger.info(f"Cache hit for: {cache_key}")
            coords = self.cache[cache_key]
            return (coords['lat'], coords['lon']) if coords else None
        
        query = f"{site_name}, {state}, USA"
        
        try:
            # Respect free service rate limits
            time.sleep(5)
            
            # Oregon bounding box: west, south, east, north
            viewbox = "-124.8,41.9,-116.4,46.3"
            g = geocoder.osm(
                query,
                viewbox=viewbox,
                bounded=1,
                countrycodes="us",
                maxRows=1,
                timeout=10,
                headers={"User-Agent": "OregonSQM-Dashboard/1.0 (viditagrawal91@gmail.com)"}
            )
            
            if g.ok and g.latlng:
                lat, lon = g.latlng
                self.cache[cache_key] = {'lat': lat, 'lon': lon}
                self._save_cache()
                logger.info(f"Geocoded {site_name}: ({lat:.3f}, {lon:.3f})")
                return (lat, lon)
            else:
                logger.warning(f"No results for: {query}")
                self.cache[cache_key] = None
                self._save_cache()
                return None
        
        except Exception as e:
            logger.error(f"Geocoding failed for {site_name}: {e}")
            return None
    
    def geocode_batch(self, site_names: List[str]) -> Dict[str, Optional[Tuple[float, float]]]:
        """Geocode multiple sites with progress tracking"""
        results = {}
        
        logger.info(f"Geocoding {len(site_names)} sites...")
        
        for i, site_name in enumerate(site_names, 1):
            logger.info(f"[{i}/{len(site_names)}] Processing: {site_name}")
            coords = self.geocode_site(site_name)
            results[site_name] = coords
            
        successful = sum(1 for coords in results.values() if coords is not None)
        logger.info(f"✅ Geocoded {successful}/{len(site_names)} sites successfully")
        
        return results