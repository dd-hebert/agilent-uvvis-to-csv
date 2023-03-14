# uv2csv
A simple script for converting Agilent 845x Chemstation UV-Vis binary files (**.KD** or **.SD** formats) to .csv format.

Do you have **.KD** or **.SD** UV-Vis binary files but no access to the Agilent 845x UV-Vis Chemstation software? Are your **.KD** files massive and contain thousands of spectra? This script will automatically read and convert your **.KD** or **.SD** files to .csv format (and it's significantly faster than exporting .csv files directly from the Agilent Chemstation software!). Exports thousands of spectra in seconds!

Currently supports **.KD** and **.SD** binary file types.

## Using This Script
To use this script, simply run it from the command line:

```sh
python uv2csv.py
```
Then provide a file path when prompted.

## How It Works
This script works by searching **.KD** or **.SD** binary file for a string of hexedecimal values ``\x28\x00\x41\x00\x55\x00\x29\x00`` which precedes the absorbance data (see [disclaimer](#disclaimer)). The absorbance data following this string of hexedecimal values are little-endian double precision floats which get unpacked into a pandas DataFrame.

## Where .CSV Files Are Exported
The specified **.KD** or **.SD** binary file is read and UV-Vis spectra are automatically exported as .csv files. 
- **.KD files:** .csv files get exported to a folder named ``self.name`` in ``self.path``. 
- **.SD files:** a single .csv file named ``self.name`` is exported to ``self.path``.

Here ``self.name`` is the name of the binary file (without the file extension) and ``self.path`` is the file path where the binary file is located.

## Changing The Wavelength Range
By default, the script assumes your spectrometer captures data from **190 nm to 1100 nm**. If the range of wavelengths your spectrometer records is different than this, you can set the wavelength range by adding a single keyword argument ``wavelength_range`` to the ``BinaryFile`` object constructor at the bottom of the script:

```python
if __name__ == '__main__':
    PATH = os.path.normpath(input('Enter a file path: '))
    BINARY_FILE = BinaryFile(PATH, wavelength_range=(min, max))
    BINARY_FILE.export_csv()

```

## Requirements
You must have the [pandas](https://pandas.pydata.org/) python package installed to use this script.

## Disclaimer
This script has only been tested on UV-Vis binary files outputted from a single machine (the spectrometer in my lab) running Agilent UV-Vis Chemstation ver. B.05.02 [16] using the default standard and kinetics methods.  Therefore, UV-Vis binary files from other versions of UV-Vis Chemstation or different spectrometer setups using custom methods may result in UV-Vis binary files which cannot be read by this script.

If you encounter such an issue, please let me know and submit an issue so I can improve this script!
