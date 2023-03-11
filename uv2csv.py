'''
A simple script to convert Agilent 845x Chemstation UV-Vis binary files
to .csv format. To use this script, simply run it from the command line
then provide a file path. Currently supported binary file types are .KD
and .SD files.

Version 1.0.0
Created by David Hebert

'''

import os
import struct
import pandas as pd

class BinaryFile:
    '''
    An Agilent UV-Vis Chemstation binary file object. Supported file types
    are .KD and .SD. Upon creation of a Binary_File object, the user is
    prompted for a file path. The specified .KD or .SD binary file is read
    and UV-Vis spectra are exported as .csv files.

    '''
    supported_file_types = ['.KD', '.kd', '.SD', '.sd']

    def __init__(self):
        self.path = os.path.normpath(input('Enter a file path: '))

        # Check path is a .KD or .SD file
        while (os.path.splitext(self.path)[1] not in self.supported_file_types
                or os.path.isfile(self.path) is False):

            print('Invalid file path (must be a .KD or .SD file).')
            self.path = os.path.normpath(input('Enter a file path: '))

        self.name, self.file_type = os.path.splitext(os.path.basename(self.path))

        print(f'Reading {self.file_type} file...')
        self.spectra = self.read_binary()
        print('Exporting .csv files...')
        self.export_csv()

    def read_binary(self, **kwargs):
        '''
        Reads a .KD or .SD file and extracts the spectra into a list of
        pd DataFrames (.KD file) or single pd DataFrame (.SD file).

        Keyword Arguments
        -----------------
        wavelength_range : tuple
            Set the range of wavelengths recorded by the detector.
            Default is 190 nm to 1100 nm.

        Returns
        -------
        spectra: (List of) pd DataFrame(s)
            Returns a list of pd DataFrame (.KD file) or single pd DataFrame
            (.SD file) containing the UV-Vis spectra.

        '''
        spectrum_locations = [0]
        spectra = []

        # Spectrometer records from 190-1100 nm by default
        wavelength_range = kwargs.get('wavelength_range', (190,1101))
        wavelength = list(range(wavelength_range[0], wavelength_range[1]))

        with open(self.path,'rb') as binary_file:
            file_bytes = binary_file.read() # Bytes from .KD or .SD binary file

        # Find the string of bytes that precedes absorbance data in binary file.
        finder = file_bytes.find(b'\xFF\xFF\x8F\x03\x00\x00\x00', spectrum_locations[-1])

        # Extract absorbance data.
        while spectrum_locations[-1] != -1:
            absorbance = []
            spectrum_locations.append(finder)

            for i in range(spectrum_locations[-1]+7, spectrum_locations[-1]+7288, 8):
                absorbance.append(struct.unpack('<d', (file_bytes[i:i+8]))[0]) # Little endian mode

            spectra.append(pd.DataFrame({'Wavelength (nm)':wavelength, 'Absorbance (AU)':absorbance}))
            finder = file_bytes.find(b'\xFF\xFF\x8F\x03\x00\x00\x00', spectrum_locations[-1]+7)

        spectra.pop(-1) # Remove weird final spectrum

        if self.file_type in ['.SD', '.sd']:
            return spectra[0]

        return spectra

    def export_csv(self):
        '''
        Exports the spectra in the .KD or .SD file as .csv files. For .KD files,
        .csv files are exported to a folder named {self.name} in {self.path}. For
        .SD files, a .csv file named {self.name} is exported to {self.path}.

        Returns
        -------
            None.

        '''
        if self.file_type in ['.KD', '.kd']:
            output_dir = os.path.splitext(self.path)[0]
            n = 1
            # If a folder named {self.name} exists, add a number after.
            while os.path.exists(output_dir) is True:
                output_dir = os.path.splitext(self.path)[0] + f' ({n})'
                n += 1

            os.mkdir(output_dir)

            # Get number of digits to use for leading zeros.
            digits = len(str(len(self.spectra)))

            for i,spectrum in enumerate(self.spectra):
                spectrum.to_csv(os.path.join(output_dir, f'{str(i+1).zfill(digits)}.csv'), index=False)
            print(f'Finished export: {output_dir}', end='\n')

        elif self.file_type in ['.SD', '.sd']:
            filename = os.path.splitext(self.path)[0] + '.csv'
            n = 1

            # If a file named {filename} exists, add a number after.
            while os.path.exists(filename) is True:
                filename = os.path.splitext(self.path)[0] + f' ({n}).csv'
                n += 1

            self.spectra.to_csv(filename, index=False)
            print(f'Finished export: {filename}', end='\n')

if __name__ == '__main__':
    BinaryFile()
