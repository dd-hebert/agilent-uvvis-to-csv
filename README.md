# uv2csv
A simple script for converting Agilent 845x Chemstation UV-Vis binary files (**.KD** or **.SD** formats) to .csv format.

Do you have **.KD** or **.SD** UV-Vis files but no access to the Agilent 845x UV-Vis Chemstation software? Do you have large **.KD** files that contain thousands of spectra? This script will automatically convert your **.KD** or **.SD** files to .csv format (and it's significantly faster than the Agilent Chemstation software!). Exports thousands of spectra in seconds!

Currently supports **.KD** and **.SD** UV-Vis binary file types.

## Using This Script
To use this script, simply run it from the command line:

```sh
python uv2csv.py
```
Then provide a file path when prompted.

## How It Works
This script works by searching a **.KD** or **.SD** file for a unique byte string which precedes the absorbance data (see [disclaimer](#disclaimer)). The absorbance data that follows this byte string are encoded as little-endian double precision floats, which the script unpacks into a pandas DataFrame.

## Export Location for .CSV Files
You can locate the exported .csv files in the same directory as the original **.KD** or **.SD** binary file.
- **.KD/.SD Files with Multiple Spectra:** .csv files are exported into a folder within the same directory as the binary file.
- **.KD/.SD Files with a Single Spectrum:** A single .csv file is exported to the same directory as the binary file.

**Note:** If you are parsing a **.SD** file which contains sample names, the sample names will be included in the file names of the exported .csv files. Please be aware that sample names are not currently supported for **.KD** files.

## Changing The Wavelength Range
By default, the script assumes your spectrometer captures data from **190 nm to 1100 nm**. If the range of wavelengths your spectrometer records is different than this, you can set the wavelength range by adding a single keyword argument ``wavelength_range`` to the ``BinaryFile`` object constructor at the bottom of the script:

```python
if __name__ == '__main__':
    PATH = os.path.normpath(input('Enter a file path or "q" to quit: '))
    BINARY_FILE = BinaryFile(PATH, export_csv=True, wavelength_range=(min, max))

```

## Requirements
You must have the [pandas](https://pandas.pydata.org/) python package installed to use this script.

## Disclaimer
This script has only been tested on files from a small number of different versions of the Agilent UV-Vis Chemstation software. Therefore, binary files from other versions of UV-Vis Chemstation, different spectrometer setups, or custom methods may not work.

**Known Supported Chemstation Versions:**
- B.05.02 [16]
- A.08.03 [71]

If you encounter an bug or problem, please submit an issue so I can improve this script!
