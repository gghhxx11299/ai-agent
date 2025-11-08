"""Code generation utilities for PyQGIS and other scripts"""

import os
from datetime import datetime
from pathlib import Path


def generate_pyqgis_script(options: dict = None) -> str:
    """
    Generate PyQGIS script for automated satellite imagery processing

    Args:
        options: Optional configuration for the script

    Returns:
        Generated PyQGIS script as a string
    """
    options = options or {}
    input_folder = options.get('inputFolder', '/path/to/satellite/images')
    output_folder = options.get('outputFolder', '/path/to/output')
    shapefile_path = options.get('shapefilePath', '/path/to/ethiopia_regions.shp')
    region = options.get('region', 'Ethiopia regions')

    return f'''"""
PyQGIS Script: Automated Satellite Imagery Processing
Purpose: Process Landsat and Sentinel-2 imagery with NDVI calculation and clipping
Author: Gemini Regional Agent
Date: {datetime.now().strftime('%Y-%m-%d')}
"""

import os
from qgis.core import (
    QgsRasterLayer,
    QgsVectorLayer,
    QgsProject,
    QgsRasterCalculatorEntry,
    QgsRasterCalculator,
    QgsCoordinateReferenceSystem
)
from qgis.analysis import QgsRasterCalculator
import processing

# =============================================================================
# CONFIGURATION
# =============================================================================

# Input/Output Paths
INPUT_FOLDER = r"{input_folder}"
OUTPUT_FOLDER = r"{output_folder}"
SHAPEFILE_PATH = r"{shapefile_path}"

# Supported file extensions
RASTER_EXTENSIONS = ['.tif', '.tiff', '.TIF', '.TIFF']

# Band indices for different satellite types
# Landsat 8/9: Band 4 = Red, Band 5 = NIR
# Sentinel-2: Band 4 = Red, Band 8 = NIR
LANDSAT_RED_BAND = 4
LANDSAT_NIR_BAND = 5
SENTINEL_RED_BAND = 4
SENTINEL_NIR_BAND = 8

print("="*70)
print("SATELLITE IMAGERY PROCESSING SCRIPT")
print("="*70)

# =============================================================================
# STEP 1: CREATE OUTPUT FOLDER IF IT DOESN'T EXIST
# =============================================================================
print("\\n[1/5] Checking output folder...")

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)
    print(f"✓ Created output folder: {{OUTPUT_FOLDER}}")
else:
    print(f"✓ Output folder exists: {{OUTPUT_FOLDER}}")

# =============================================================================
# STEP 2: LOAD SHAPEFILE BOUNDARY
# =============================================================================
print("\\n[2/5] Loading shapefile boundary...")

boundary_layer = QgsVectorLayer(SHAPEFILE_PATH, "{region}", "ogr")

if not boundary_layer.isValid():
    print(f"✗ ERROR: Failed to load shapefile: {{SHAPEFILE_PATH}}")
    print("Please check the file path and try again.")
    exit(1)
else:
    print(f"✓ Loaded shapefile: {{SHAPEFILE_PATH}}")
    print(f"  Features: {{boundary_layer.featureCount()}}")
    print(f"  CRS: {{boundary_layer.crs().authid()}}")

QgsProject.instance().addMapLayer(boundary_layer)

# =============================================================================
# STEP 3: FIND ALL RASTER FILES IN INPUT FOLDER
# =============================================================================
print("\\n[3/5] Scanning for raster files...")

raster_files = []
for filename in os.listdir(INPUT_FOLDER):
    if any(filename.endswith(ext) for ext in RASTER_EXTENSIONS):
        raster_files.append(os.path.join(INPUT_FOLDER, filename))

if not raster_files:
    print(f"✗ ERROR: No raster files found in {{INPUT_FOLDER}}")
    print(f"  Supported formats: {{', '.join(RASTER_EXTENSIONS)}}")
    exit(1)

print(f"✓ Found {{len(raster_files)}} raster file(s)")
for i, f in enumerate(raster_files, 1):
    print(f"  {{i}}. {{os.path.basename(f)}}")

# =============================================================================
# STEP 4: PROCESS EACH RASTER IMAGE
# =============================================================================
print("\\n[4/5] Processing raster images...")

processed_count = 0
error_count = 0

for idx, raster_path in enumerate(raster_files, 1):
    print(f"\\n--- Processing {{idx}}/{{len(raster_files)}}: {{os.path.basename(raster_path)}} ---")

    try:
        raster_layer = QgsRasterLayer(raster_path, os.path.basename(raster_path))

        if not raster_layer.isValid():
            print(f"✗ Skipping: Invalid raster layer")
            error_count += 1
            continue

        print(f"  Bands: {{raster_layer.bandCount()}}")
        print(f"  CRS: {{raster_layer.crs().authid()}}")

        filename_lower = os.path.basename(raster_path).lower()

        if 'landsat' in filename_lower or 'lc08' in filename_lower or 'lc09' in filename_lower:
            red_band = LANDSAT_RED_BAND
            nir_band = LANDSAT_NIR_BAND
            satellite_type = 'Landsat'
        elif 'sentinel' in filename_lower or 's2' in filename_lower:
            red_band = SENTINEL_RED_BAND
            nir_band = SENTINEL_NIR_BAND
            satellite_type = 'Sentinel-2'
        else:
            red_band = LANDSAT_RED_BAND
            nir_band = LANDSAT_NIR_BAND
            satellite_type = 'Unknown (using Landsat bands)'

        print(f"  Detected: {{satellite_type}}")
        print(f"  Using: Red Band {{red_band}}, NIR Band {{nir_band}}")

        # Calculate NDVI
        print("  Calculating NDVI...")

        nir_entry = QgsRasterCalculatorEntry()
        nir_entry.ref = 'nir@1'
        nir_entry.raster = raster_layer
        nir_entry.bandNumber = nir_band

        red_entry = QgsRasterCalculatorEntry()
        red_entry.ref = 'red@1'
        red_entry.raster = raster_layer
        red_entry.bandNumber = red_band

        ndvi_formula = '(nir@1 - red@1) / (nir@1 + red@1)'

        base_name = os.path.splitext(os.path.basename(raster_path))[0]
        ndvi_output = os.path.join(OUTPUT_FOLDER, f"{{base_name}}_NDVI.tif")

        calc = QgsRasterCalculator(
            ndvi_formula,
            ndvi_output,
            'GTiff',
            raster_layer.extent(),
            raster_layer.crs(),
            raster_layer.width(),
            raster_layer.height(),
            [nir_entry, red_entry]
        )

        result = calc.processCalculation()

        if result == 0:
            print(f"  ✓ NDVI calculated successfully")
        else:
            print(f"  ✗ NDVI calculation failed (error code: {{result}})")
            error_count += 1
            continue

        # Clip to boundary
        print("  Clipping to boundary shapefile...")

        ndvi_layer = QgsRasterLayer(ndvi_output, f"{{base_name}}_NDVI")

        if not ndvi_layer.isValid():
            print(f"  ✗ Failed to load NDVI result for clipping")
            error_count += 1
            continue

        clipped_output = os.path.join(OUTPUT_FOLDER, f"{{base_name}}_NDVI_clipped.tif")

        params = {{
            'INPUT': ndvi_layer,
            'MASK': boundary_layer,
            'SOURCE_CRS': None,
            'TARGET_CRS': None,
            'NODATA': -9999,
            'ALPHA_BAND': False,
            'CROP_TO_CUTLINE': True,
            'KEEP_RESOLUTION': True,
            'SET_RESOLUTION': False,
            'X_RESOLUTION': None,
            'Y_RESOLUTION': None,
            'MULTITHREADING': False,
            'OPTIONS': '',
            'DATA_TYPE': 0,
            'EXTRA': '',
            'OUTPUT': clipped_output
        }}

        clip_result = processing.run("gdal:cliprasterbymasklayer", params)

        if clip_result and 'OUTPUT' in clip_result:
            print(f"  ✓ Clipped successfully")
            print(f"  ✓ Saved to: {{os.path.basename(clipped_output)}}")
            processed_count += 1

            if os.path.exists(ndvi_output):
                os.remove(ndvi_output)
                print(f"  ✓ Removed intermediate file")
        else:
            print(f"  ✗ Clipping failed")
            error_count += 1

    except Exception as e:
        print(f"  ✗ Error processing file: {{str(e)}}")
        error_count += 1
        continue

# =============================================================================
# STEP 5: SUMMARY
# =============================================================================
print("\\n" + "="*70)
print("PROCESSING COMPLETE")
print("="*70)
print(f"Successfully processed: {{processed_count}} file(s)")
print(f"Errors: {{error_count}} file(s)")
print(f"Output folder: {{OUTPUT_FOLDER}}")
print("="*70)

if processed_count > 0:
    print("\\nLoading first result to canvas...")
    first_result = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith('_clipped.tif')][0]
    result_path = os.path.join(OUTPUT_FOLDER, first_result)
    result_layer = QgsRasterLayer(result_path, first_result)
    if result_layer.isValid():
        QgsProject.instance().addMapLayer(result_layer)
        print(f"✓ Loaded: {{first_result}}")

print("\\n🎉 Script execution finished!\\n")
'''


def save_script(script: str, output_dir: str = 'generated_scripts') -> str:
    """
    Save generated script to file

    Args:
        script: Generated script content
        output_dir: Output directory

    Returns:
        Path to saved file
    """
    # Create output directory if it doesn't exist
    try:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    except (OSError, PermissionError) as e:
        raise Exception(f"Failed to create output directory: {e}")

    # Generate filename with timestamp
    filename = f"satellite_processing_{int(datetime.now().timestamp())}.py"
    filepath = os.path.join(output_dir, filename)

    # Write script to file with proper error handling
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(script)
    except (IOError, OSError, EOFError) as e:
        raise Exception(f"Failed to write script file: {e}")

    return filepath
