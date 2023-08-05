"""
A simple script to convert Agilent 845x Chemstation UV-Vis files to .csv format.

To use this script, simply run it from the command line then provide a file
path. Currently supported UV-Vis file types are .KD and .SD files.

Version 0.1.5
Created by David Hebert

"""

import os
import struct
import pandas as pd


class BinaryFile:
    """
    A BinaryFile object.

    Supported file types are .KD and .SD. Upon creation of a BinaryFile object,
    the specified .KD or .SD binary file is read and unpacked into a
    :class:`pandas.DataFrame`.

    """

    supported_file_types = ['.KD', '.SD']

    def __init__(self, path, wavelength_range=(190, 1100)):
        """
        Initialize a :class:`BinaryFile` object and read a UV-Vis binary file.

        Parameters
        ----------
        path : str
            The file path to a UV-Vis binary file (.KD or .SD format).
        wavelength_range : tuple
            Set the range of wavelengths (in nm) recorded by the detector (min, max).
            Default value is (190, 1100).

        Returns
        -------
        None

        """
        self.path = path
        self._check_path()
        self.wavelength_range = wavelength_range
        self._check_wavelength_range()
        self.name, self.file_type = os.path.splitext(os.path.basename(self.path))
        self.spectra = self.read_binary()

    def _check_path(self):
        """Check path is a .KD or .SD file."""
        while (os.path.splitext(self.path)[1].upper() not in self.supported_file_types
                or os.path.isfile(self.path) is False):

            print('Invalid file path (must be a .KD or .SD file).')
            self.path = os.path.normpath(input('Enter a file path: '))

    def _check_wavelength_range(self):
        """Check ``wavelength_range`` is valid."""
        if self.wavelength_range[0] > self.wavelength_range[1]:
            raise Exception('Wavelength range error: minimum wavelength greater than maximum.')

    def read_binary(self):
        """
        Read a .KD or .SD file and extract the spectra into a list.

        Raises
        ------
        Exception
            Raises an exception if no spectra can be found.

        Returns
        -------
        spectra: list of :class:`pandas.DataFrame` objects
            A list of :class:`pandas.DataFrame` objects containing the UV-Vis
            spectra.

        """
        spectrum_locations = [0]
        spectra = []
        wavelength = list(range(self.wavelength_range[0], self.wavelength_range[1] + 1))

        # Data is 8 hex characters per wavelength long.
        absorbance_table_length = (self.wavelength_range[1] - self.wavelength_range[0]) * 8 + 8

        print(f'Reading {self.file_type} file...')

        with open(self.path, 'rb') as binary_file:
            file_bytes = binary_file.read()

        absorbance_data_header, spacing = self._find_absorbance_data_header(file_bytes)

        # Find the string of bytes that precedes absorbance data in binary file.
        finder = file_bytes.find(absorbance_data_header, spectrum_locations[-1])

        # Extract absorbance data.
        while spectrum_locations[-1] != -1 and finder != -1:
            spectrum_locations.append(finder)
            data_start = spectrum_locations[-1] + spacing
            data_end = data_start + absorbance_table_length
            absorbance_data = file_bytes[data_start:data_end]

            absorbance_values = [value for value, in struct.iter_unpack('<d', absorbance_data)]

            spectra.append(pd.DataFrame({'Wavelength (nm)': wavelength,
                                         'Absorbance (AU)': absorbance_values}))

            finder = file_bytes.find(absorbance_data_header, data_end)

        if spectra == []:
            raise Exception('Error parsing file. No spectra found.')

        return spectra

    def _find_absorbance_data_header(self, file_bytes):
        """
        Search the binary file for the appropriate absorbance data header.

        Parameters
        ----------
        file_bytes : bytes
            The raw bytes of the binary file.

        Raises
        ------
        Exception
            Raises an exception if no absorbance data headers can be found.

        Returns
        -------
        header : string
            The absorbance data header as a hex string.

        """
        # Each header contains its hex string and the spacing that follows it.
        headers = {
            '( A U ) ': (b'\x28\x00\x41\x00\x55\x00\x29\x00', 17),
            '(AU) ': (b'\x28\x41\x55\x29\x00', 5)
        }
        for key, (header, spacing) in headers.items():
            if file_bytes.find(header, 0) != -1:
                return header, spacing

        raise Exception('Error parsing file. No absorbance data headers could be found.')

    def export_csv(self):
        """
        Export spectra as .csv files.

        For files containing multiple spectra, .csv files are exported to a
        folder named ``self.name`` in ``self.path``. For files with a single
        spectrum, a .csv file named ``self.name`` is exported to ``self.path``.

        Returns
        -------
            None.

        """
        print('Exporting .csv files...')

        if len(self.spectra) > 1:
            output_dir = os.path.splitext(self.path)[0]
            n = 1
            # If a folder named self.name exists, add a number after.
            while os.path.exists(output_dir) is True:
                output_dir = os.path.splitext(self.path)[0] + f' ({n})'
                n += 1

            os.mkdir(output_dir)

            # Get number of digits to use for leading zeros.
            digits = len(str(len(self.spectra)))

            for i, spectrum in enumerate(self.spectra):
                spectrum.to_csv(os.path.join(output_dir, f'{str(i + 1).zfill(digits)}.csv'), index=False)
            print(f'Finished export: {output_dir}', end='\n')

        else:
            filename = os.path.splitext(self.path)[0] + '.csv'
            n = 1

            # If a file named filename exists, add a number after.
            while os.path.exists(filename) is True:
                filename = os.path.splitext(self.path)[0] + f' ({n}).csv'
                n += 1

            self.spectra[0].to_csv(filename, index=False)
            print(f'Finished export: {filename}', end='\n')


if __name__ == '__main__':
    PATH = os.path.normpath(input('Enter a file path: '))
    BINARY_FILE = BinaryFile(PATH)
    BINARY_FILE.export_csv()
