import chalk from 'chalk';
import { writeFile } from 'fs/promises';
import { join } from 'path';

/**
 * Code generation utilities for various geospatial and agricultural automation tasks
 */

/**
 * Generate PyQGIS script for automated satellite imagery processing
 * @param {Object} options - Script generation options
 * @returns {string} - Generated PyQGIS script
 */
export function generatePyQGISScript(options = {}) {
  const {
    inputFolder = '/path/to/satellite/images',
    outputFolder = '/path/to/output',
    shapefilePath = '/path/to/ethiopia_regions.shp',
    region = 'Ethiopia regions',
  } = options;

  return `"""
PyQGIS Script: Automated Satellite Imagery Processing
Purpose: Process Landsat and Sentinel-2 imagery with NDVI calculation and clipping
Author: Multi-AI Regional Intelligence Agent
Date: ${new Date().toISOString().split('T')[0]}
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
INPUT_FOLDER = r"${inputFolder}"
OUTPUT_FOLDER = r"${outputFolder}"
SHAPEFILE_PATH = r"${shapefilePath}"

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
    print(f"✓ Created output folder: {OUTPUT_FOLDER}")
else:
    print(f"✓ Output folder exists: {OUTPUT_FOLDER}")

# =============================================================================
# STEP 2: LOAD SHAPEFILE BOUNDARY
# =============================================================================
print("\\n[2/5] Loading shapefile boundary...")

# Load the shapefile for clipping
boundary_layer = QgsVectorLayer(SHAPEFILE_PATH, "${region}", "ogr")

if not boundary_layer.isValid():
    print(f"✗ ERROR: Failed to load shapefile: {SHAPEFILE_PATH}")
    print("Please check the file path and try again.")
    exit(1)
else:
    print(f"✓ Loaded shapefile: {SHAPEFILE_PATH}")
    print(f"  Features: {boundary_layer.featureCount()}")
    print(f"  CRS: {boundary_layer.crs().authid()}")

# Add boundary to project for visualization (optional)
QgsProject.instance().addMapLayer(boundary_layer)

# =============================================================================
# STEP 3: FIND ALL RASTER FILES IN INPUT FOLDER
# =============================================================================
print("\\n[3/5] Scanning for raster files...")

# Get all raster files from input folder
raster_files = []
for filename in os.listdir(INPUT_FOLDER):
    if any(filename.endswith(ext) for ext in RASTER_EXTENSIONS):
        raster_files.append(os.path.join(INPUT_FOLDER, filename))

if not raster_files:
    print(f"✗ ERROR: No raster files found in {INPUT_FOLDER}")
    print(f"  Supported formats: {', '.join(RASTER_EXTENSIONS)}")
    exit(1)

print(f"✓ Found {len(raster_files)} raster file(s)")
for i, f in enumerate(raster_files, 1):
    print(f"  {i}. {os.path.basename(f)}")

# =============================================================================
# STEP 4: PROCESS EACH RASTER IMAGE
# =============================================================================
print("\\n[4/5] Processing raster images...")

processed_count = 0
error_count = 0

for idx, raster_path in enumerate(raster_files, 1):
    print(f"\\n--- Processing {idx}/{len(raster_files)}: {os.path.basename(raster_path)} ---")

    try:
        # Load the raster layer
        raster_layer = QgsRasterLayer(raster_path, os.path.basename(raster_path))

        if not raster_layer.isValid():
            print(f"✗ Skipping: Invalid raster layer")
            error_count += 1
            continue

        print(f"  Bands: {raster_layer.bandCount()}")
        print(f"  CRS: {raster_layer.crs().authid()}")

        # Determine satellite type based on filename or band count
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
            # Default to Landsat if unclear
            red_band = LANDSAT_RED_BAND
            nir_band = LANDSAT_NIR_BAND
            satellite_type = 'Unknown (using Landsat bands)'

        print(f"  Detected: {satellite_type}")
        print(f"  Using: Red Band {red_band}, NIR Band {nir_band}")

        # --- CALCULATE NDVI ---
        print("  Calculating NDVI...")

        # Create raster calculator entries for NIR and Red bands
        nir_entry = QgsRasterCalculatorEntry()
        nir_entry.ref = 'nir@1'
        nir_entry.raster = raster_layer
        nir_entry.bandNumber = nir_band

        red_entry = QgsRasterCalculatorEntry()
        red_entry.ref = 'red@1'
        red_entry.raster = raster_layer
        red_entry.bandNumber = red_band

        # NDVI formula: (NIR - Red) / (NIR + Red)
        ndvi_formula = '(nir@1 - red@1) / (nir@1 + red@1)'

        # Output path for NDVI
        base_name = os.path.splitext(os.path.basename(raster_path))[0]
        ndvi_output = os.path.join(OUTPUT_FOLDER, f"{base_name}_NDVI.tif")

        # Calculate NDVI
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
            print(f"  ✗ NDVI calculation failed (error code: {result})")
            error_count += 1
            continue

        # --- CLIP TO BOUNDARY ---
        print("  Clipping to boundary shapefile...")

        # Load the NDVI result
        ndvi_layer = QgsRasterLayer(ndvi_output, f"{base_name}_NDVI")

        if not ndvi_layer.isValid():
            print(f"  ✗ Failed to load NDVI result for clipping")
            error_count += 1
            continue

        # Output path for clipped NDVI
        clipped_output = os.path.join(OUTPUT_FOLDER, f"{base_name}_NDVI_clipped.tif")

        # Clip raster by mask layer using GDAL
        params = {
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
        }

        clip_result = processing.run("gdal:cliprasterbymasklayer", params)

        if clip_result and 'OUTPUT' in clip_result:
            print(f"  ✓ Clipped successfully")
            print(f"  ✓ Saved to: {os.path.basename(clipped_output)}")
            processed_count += 1

            # Optional: Remove unclipped NDVI to save space
            if os.path.exists(ndvi_output):
                os.remove(ndvi_output)
                print(f"  ✓ Removed intermediate file")
        else:
            print(f"  ✗ Clipping failed")
            error_count += 1

    except Exception as e:
        print(f"  ✗ Error processing file: {str(e)}")
        error_count += 1
        continue

# =============================================================================
# STEP 5: SUMMARY
# =============================================================================
print("\\n" + "="*70)
print("PROCESSING COMPLETE")
print("="*70)
print(f"Successfully processed: {processed_count} file(s)")
print(f"Errors: {error_count} file(s)")
print(f"Output folder: {OUTPUT_FOLDER}")
print("="*70)

# Optional: Load one result for visualization
if processed_count > 0:
    print("\\nLoading first result to canvas...")
    first_result = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith('_clipped.tif')][0]
    result_path = os.path.join(OUTPUT_FOLDER, first_result)
    result_layer = QgsRasterLayer(result_path, first_result)
    if result_layer.isValid():
        QgsProject.instance().addMapLayer(result_layer)
        print(f"✓ Loaded: {first_result}")

print("\\n🎉 Script execution finished!\\n")
`;
}

/**
 * Save generated script to file
 * @param {string} script - Generated script content
 * @param {string} filename - Output filename
 * @param {string} outputDir - Output directory
 * @returns {Promise<string>} - Path to saved file
 */
export async function saveScript(script, filename, outputDir = './generated_scripts') {
  const { mkdirSync, existsSync } = await import('fs');

  if (!existsSync(outputDir)) {
    mkdirSync(outputDir, { recursive: true });
  }

  const filePath = join(outputDir, filename);
  await writeFile(filePath, script, 'utf-8');

  return filePath;
}

/**
 * Display script generation summary
 * @param {string} scriptType - Type of script generated
 * @param {string} filePath - Path where script was saved
 */
export function displayScriptSummary(scriptType, filePath) {
  console.log(chalk.bold.green('\n✨ Script Generated Successfully!\n'));
  console.log(chalk.cyan('Script Type:'), scriptType);
  console.log(chalk.cyan('Saved to:'), filePath);
  console.log(chalk.yellow('\n📝 Next Steps:'));
  console.log('  1. Open QGIS');
  console.log('  2. Go to Plugins → Python Console');
  console.log('  3. Click "Show Editor" button');
  console.log('  4. Load and run the script');
  console.log('  5. Update the file paths in the configuration section');
  console.log();
}

/**
 * Generate usage instructions for PyQGIS script
 * @returns {string} - Instructions text
 */
export function getPyQGISInstructions() {
  return `
${chalk.bold.cyan('PyQGIS Script Usage Instructions:')}

${chalk.yellow('Prerequisites:')}
  • QGIS 3.x installed on your system
  • Satellite imagery (Landsat 8/9 or Sentinel-2) downloaded
  • Shapefile of your region boundary (e.g., Ethiopia regions)

${chalk.yellow('Setup Steps:')}
  1. ${chalk.white('Organize your data:')}
     - Place all satellite images in one folder
     - Have your shapefile ready (.shp and associated files)

  2. ${chalk.white('Open QGIS:')}
     - Launch QGIS Desktop
     - Open Python Console (Plugins → Python Console)
     - Click "Show Editor" button

  3. ${chalk.white('Configure the script:')}
     - Update INPUT_FOLDER path
     - Update OUTPUT_FOLDER path
     - Update SHAPEFILE_PATH
     - Verify band numbers match your satellite type

  4. ${chalk.white('Run the script:')}
     - Click "Run Script" or press Ctrl+Enter
     - Monitor progress in the console
     - Results will be saved to your output folder

${chalk.yellow('What the script does:')}
  ✓ Scans input folder for all raster images (.tif files)
  ✓ Calculates NDVI (Normalized Difference Vegetation Index)
  ✓ Clips each NDVI image to your region boundary
  ✓ Saves results as GeoTIFF in output folder
  ✓ Provides detailed progress reporting

${chalk.yellow('Output Files:')}
  • [original_name]_NDVI_clipped.tif - Final clipped NDVI images
  • One file per input image

${chalk.yellow('Troubleshooting:')}
  • If script fails, check file paths are correct
  • Ensure shapefile CRS matches raster CRS
  • Verify band numbers for your satellite type
  • Check QGIS console for detailed error messages
`;
}

export default {
  generatePyQGISScript,
  saveScript,
  displayScriptSummary,
  getPyQGISInstructions,
};
