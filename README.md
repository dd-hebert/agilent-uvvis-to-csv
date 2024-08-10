# uv2csv
A simple script for converting Agilent 845x Chemstation UV-vis binary files (**.KD** or **.SD** formats) to .csv format.

Do you have **.KD** or **.SD** UV-vis files but no access to the Agilent 845x UV-vis Chemstation software? Do you have large **.KD** files that contain thousands of spectra? This script will automatically convert your **.KD** or **.SD** files to .csv format (and it's significantly faster than the Agilent Chemstation software!). Exports thousands of spectra in seconds!

Currently supports **.KD** and **.SD** UV-vis binary file types.

## Using This Script
To use this script, simply run it from the command line:

```sh
python uv2csv.py
```
Then provide a file path when prompted.

## Requirements
You must have the [pandas](https://pandas.pydata.org/) python package installed to use this script.

## How It Works
This script works by searching a **.KD** or **.SD** file for a unique byte string which precedes the absorbance data (see [disclaimer](#disclaimer)). The absorbance data that follows this byte string are encoded as little-endian double precision floats, which the script unpacks into a pandas DataFrame.

## Export Location for .CSV Files
You can locate the exported .csv files in the same directory as the original **.KD** or **.SD** binary file.
- **Files with Multiple Spectra:** .csv files are exported into a folder within the same directory as the binary file.
- **Files with a Single Spectrum:** A single .csv file is exported to the same directory as the binary file.

**Note:** If the **.SD** file you are parsing contains sample names, the sample names will be included in the file names of the exported .csv files. Please be aware that sample names are not currently supported for **.KD** files.

## Changing The Wavelength Range
By default, the script assumes your spectrometer captures data from **190 nm to 1100 nm**. If the range of wavelengths your spectrometer records is different than this, you can set the wavelength range by adding a single keyword argument ``wavelength_range`` to the ``UVvisFile`` object constructor at the bottom of the script:

```python
if __name__ == '__main__':
    if path := input_path():
        UVvisFile(path, export_csv=True, wavelength_range=(min, max))
```
Running the script with an incorrect wavelength range might lead to unexpected results and messed-up looking spectra. It seems that both the Agilent 8453 and 8454 spectrometer models only capture data from 190 nm to 1100 nm, so the default setting should work fine for most cases. However, if needed, this setting can be adjusted as shown above. In the future, I may add a feature that automatically detects the correct wavelength range.

## Automation
Running the script directly with ``python uv2csv.py`` allows you to export one **.KD** or **.SD** file at a time. This is fine if you only have a few files or are comfortable using the command line. However, if you need to export many files, doing them one by one might not be the most efficient way. Below is a simple example script that can help you automate the export of multiple **.KD** or **.SD** files all at once:

```python
from pathlib import Path
from uv2csv import UVvisFile

dir = Path(r'C:\Documents\UV_Spectra\Data')
files = [
    'file1.SD',
    'file2.KD',
    'other_file.SD',
    'yet_another_file.KD',
    'some_uvvis_data.SD'
]

if __name__ == '__main__':
    for file in files:
        UVvisFile(dir.joinpath(file), export_csv=True)
```

## Built for Simplicity
The goal of ``uv2csv`` is to make the process as straightforward as possible. You don't need to learn complicated commands or navigate through a bunch of features and options. This script is designed for ease of use, especially for those who might not be familiar with Python or programming. I've kept the code minimal and simple, so it should (hopefully) be easy to understand and customize for your specific needs.

If you're looking for more advanced features, feel free to open an issue or reach out to me, and I'll consider adding them. I'm also developing a more feature-rich UV-vis data processing library for .KD and .SD files, which I plan to release in the near future.

## Disclaimer
This script has only been tested on files from a small number of different versions of the Agilent UV-vis Chemstation software. Therefore, binary files from other versions of UV-vis Chemstation, different spectrometer setups, or custom methods may not work.

**Known Supported Chemstation Versions:**
- B.05.02 [16]
- A.08.03 [71]

If you encounter an bug or problem, please submit an issue so I can improve this script!
