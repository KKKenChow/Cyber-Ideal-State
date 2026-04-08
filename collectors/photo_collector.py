"""
Photo collector for analyzing photo metadata
"""
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from PIL import Image
import exifread
from .base import BaseCollector, CollectorError, parse_timestamp


class PhotoCollector(BaseCollector):
    """Collect photo metadata from image files"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.photo_dir = config.get("path")
        
        if not self.photo_dir:
            raise CollectorError("Photo directory path not provided")
        
        if not os.path.exists(self.photo_dir):
            raise CollectorError(f"Photo directory not found: {self.photo_dir}")
    
    def validate(self) -> bool:
        """Validate photo directory"""
        return os.path.isdir(self.photo_dir)
    
    def collect(self) -> Dict[str, Any]:
        """Collect photo metadata"""
        if not self.validate():
            raise CollectorError("Photo directory validation failed")
        
        photos = []
        
        # Walk through directory
        for root, dirs, files in os.walk(self.photo_dir):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    file_path = os.path.join(root, file)
                    photo_data = self._analyze_photo(file_path)
                    if photo_data:
                        photos.append(photo_data)
        
        self.collected_data["images"] = photos
        self.collected_data["metadata"] = {
            "source": "photo",
            "collected_at": datetime.now().isoformat(),
            "total_images": len(photos)
        }
        
        return self.collected_data
    
    def _analyze_photo(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Analyze a single photo"""
        try:
            # Get basic info
            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path)
            
            # Extract EXIF data
            exif_data = self._extract_exif(file_path)
            
            # Get image dimensions
            try:
                with Image.open(file_path) as img:
                    width, height = img.size
                    format_name = img.format
            except:
                width, height = 0, 0
                format_name = None
            
            return {
                "file_path": file_path,
                "file_name": file_name,
                "file_size": file_size,
                "width": width,
                "height": height,
                "format": format_name,
                **exif_data
            }
        except Exception as e:
            print(f"Failed to analyze photo {file_path}: {e}")
            return None
    
    def _extract_exif(self, file_path: str) -> Dict[str, Any]:
        """Extract EXIF metadata"""
        exif_data = {
            "timestamp": None,
            "location": None,
            "camera": None,
            "description": None
        }
        
        try:
            with open(file_path, 'rb') as f:
                tags = exifread.process_file(f, details=False)
                
                # Extract timestamp
                date_time = tags.get('EXIF DateTimeOriginal')
                if date_time:
                    timestamp = parse_timestamp(str(date_time))
                    exif_data["timestamp"] = timestamp.isoformat() if timestamp else None
                
                # Extract location (GPS)
                lat = tags.get('GPS GPSLatitude')
                lat_ref = tags.get('GPS GPSLatitudeRef')
                lon = tags.get('GPS GPSLongitude')
                lon_ref = tags.get('GPS GPSLongitudeRef')
                
                if lat and lon and lat_ref and lon_ref:
                    exif_data["location"] = self._convert_gps(lat, lat_ref, lon, lon_ref)
                
                # Extract camera info
                make = tags.get('Image Make')
                model = tags.get('Image Model')
                if make or model:
                    exif_data["camera"] = f"{make} {model}".strip()
                
                # Extract description
                description = tags.get('Image ImageDescription')
                if description:
                    exif_data["description"] = str(description)
                    
        except Exception:
            pass
        
        return exif_data
    
    def _convert_gps(self, lat, lat_ref, lon, lon_ref) -> Optional[Dict[str, float]]:
        """Convert GPS coordinates to decimal degrees"""
        try:
            # Convert latitude
            lat_deg = lat.values[0].num / lat.values[0].den
            lat_min = lat.values[1].num / lat.values[1].den
            lat_sec = lat.values[2].num / lat.values[2].den
            lat_decimal = lat_deg + (lat_min / 60) + (lat_sec / 3600)
            if str(lat_ref) == 'S':
                lat_decimal = -lat_decimal
            
            # Convert longitude
            lon_deg = lon.values[0].num / lon.values[0].den
            lon_min = lon.values[1].num / lon.values[1].den
            lon_sec = lon.values[2].num / lon.values[2].den
            lon_decimal = lon_deg + (lon_min / 60) + (lon_sec / 3600)
            if str(lon_ref) == 'W':
                lon_decimal = -lon_decimal
            
            return {
                "latitude": lat_decimal,
                "longitude": lon_decimal
            }
        except:
            return None
