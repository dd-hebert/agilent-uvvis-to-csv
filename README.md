# uv2csv
A simple script for converting Agilent 845x Chemstation UV-Vis binary files (**.KD** or **.SD** formats) to .csv format.

Do you have **.KD** or **.SD** UV-Vis binary files but no access to the Agilent 845x UV-Vis Chemstation software? Are your **.KD** files massive and contain thousands of spectra? This script will automatically read and convert your **.KD** or **.SD** files to .csv format (and it's significantly faster than the Agilent Chemstation software!). Exports thousands of spectra in seconds!

Currently supports **.KD** and **.SD** binary file types.

## Using This Script
To use this script, simply run it from the command line:

```sh
python uv2csv.py
```
Then provide a file path when prompted.

## How It Works
In the **.KD** and **.SD** binary files, UV-Vis absorbance data is stored in a data table which has a unique hexadecimal header.

The way this script works is by searching the **.KD** or **.SD** binary file for the unique hexadecimal header which precedes the absorbance data (see [disclaimer](#disclaimer)). The absorbance data that follows this header are encoded as little-endian double precision floats, which the script unpacks into a pandas DataFrame.

## Export Location for .CSV Files
The script automatically exports .csv files containing UV-Vis spectra upon parsing a specified **.KD** or **.SD** binary file. You can locate the exported .csv files in the same directory as the original **.KD** or **.SD** binary file.
- **Binary Files with Multiple Spectra:** The .csv files are exported into a folder within the same directory as the binary file.
- **Binary Files with a Single Spectrum:** A single .csv file is exported to the same directory as the binary file.

**Note:** If you are parsing a **.SD** file which contains sample names, the sample names will also be included in the file names of the exported .csv files. Please be aware that sample names are not currently supported for **.KD** files.

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
This script has only been tested on UV-Vis binary files from a few different versions of the Agilent UV-Vis Chemstation software. Therefore, UV-Vis binary files from other versions of UV-Vis Chemstation, different spectrometer setups, or custom methods may not work.

**Known Supported Chemstation Versions:**
- B.05.02 [16]
- A.08.03 [71]

If you encounter an issue, please submit an issue so I can improve this script!
