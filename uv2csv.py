"""
A simple script to convert Agilent 845x Chemstation UV-Vis files to .csv format.

To use this script, simply run it from the command line then provide a file
path. Currently supported UV-Vis file types are .KD and .SD files.

Version 0.1.9
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

    def __init__(self, path, export_csv=False, wavelength_range=(190, 1100)):
        """
        Initialize a :class:`BinaryFile` object and read a UV-Vis binary file.

        Parameters
        ----------
        path : str
            The file path to a UV-Vis binary file (.KD or .SD format).
        export_csv : bool
            True or False. Set to True to automatically export .csv files upon creation
            of the :class:`BinaryFile` object. Default is False (.csv files not automatically
            exported.)
        wavelength_range : tuple
            Set the range of wavelengths (in nm) recorded by the detector (min, max).
            Default value is (190, 1100).

        Returns
        -------
        None.
        """
        self.path = path
        self._check_path()
        if self.path:
            self.wavelength_range = wavelength_range
            self._check_wavelength_range()
            self.absorbance_table_length = self._absorbance_table_length()
            self.name, self.file_type = os.path.splitext(os.path.basename(self.path))
            self.spectra, self.samplenames = self.read_binary()
            if export_csv is True:
                self.export_csv()

    def _check_path(self):
        while True:
            if self.path.lower() == 'q':
                self.path = ''
                break

            ext = os.path.splitext(self.path)[1].upper()
            if ext in self.supported_file_types and os.path.isfile(self.path):
                break

            print('Invalid file path (must be a .KD or .SD file).')
            self.path = os.path.normpath(input('Enter a file path or "q" to quit: '))

    def _check_wavelength_range(self):
        if self.wavelength_range[0] > self.wavelength_range[1]:
            raise ValueError('Wavelength range error: minimum wavelength greater than maximum.')

    def _absorbance_table_length(self):
        # Data is 8 hex characters per wavelength long.
        absorbance_table_length = (self.wavelength_range[1] - self.wavelength_range[0]) * 8 + 8
        return absorbance_table_length

    def read_binary(self):
        """
        Read a .KD or .SD file and extract spectra and sample names.

        Returns
        -------
        spectra : list of :class:`pandas.DataFrame` objects
            A list of :class:`pandas.DataFrame` objects containing the UV-Vis
            spectra.
        samplenames : list
            A list of strings with sample names.
        """
        print(f'Reading {self.file_type} file...')

        with open(self.path, 'rb') as binary_file:
            file_bytes = binary_file.read()

        spectra = self._read_spectra(file_bytes)

        if self.file_type == '.SD':
            samplenames = self._read_samplenames(file_bytes, len(spectra))
            return spectra, samplenames
        return spectra, [''] * len(spectra)

    def _read_spectra(self, file_bytes):
        """
        Read the spectra from a .KD or .SD file.

        Parameters
        ----------
        file_bytes : bytes
            The raw bytes of the binary file.

        Raises
        ------
        Exception
            Raises an exception if no spectra are found.

        Returns
        -------
        spectra : list of :class:`pandas.DataFrame` objects
            A list of :class:`pandas.DataFrame` objects containing the UV-Vis
            spectra.
        """
        spectra = []
        position = 0
        wavelength = list(range(self.wavelength_range[0], self.wavelength_range[1] + 1))
        absorbance_data_header, spacing = self._find_absorbance_data_header(file_bytes)

        while True:
            header_location = file_bytes.find(absorbance_data_header, position)
            if header_location == -1:
                break

            data_start = header_location + spacing
            data_end = data_start + self.absorbance_table_length
            absorbance_data = file_bytes[data_start:data_end]
            absorbance_values = [value for value, in struct.iter_unpack('<d', absorbance_data)]
            spectra.append(pd.DataFrame({'Wavelength (nm)': wavelength,
                                         'Absorbance (AU)': absorbance_values}))
            position = data_end

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
        spacing : int
            The spacing between the header and the beginning of the actual data.
        """
        # Each header contains its hex string and the spacing that follows it.
        headers = {
            '( A U ) ': (b'\x28\x00\x41\x00\x55\x00\x29\x00', 17),
            '(AU) ': (b'\x28\x41\x55\x29\x00', 5)}
        for key, (header, spacing) in headers.items():
            if file_bytes.find(header, 0) != -1:
                return header, spacing
        raise Exception('Error parsing file. No absorbance data headers could be found.')

    def _read_samplenames(self, file_bytes, num_samples):
        """
        Read the sample names from a .SD file.

        Parameters
        ----------
        file_bytes : bytes
            The raw bytes of the binary file.
        num_samples : int
            The number of samples or spectra in the .SD file.

        Returns
        -------
        samplenames : list
            A list of strings with the sample names.
        """
        samplename_header, spacing, end_char = self._find_samplename_header(file_bytes)
        if samplename_header is None:
            return [''] * num_samples

        samplenames = []
        position = 0

        while True:
            find_header = file_bytes.find(samplename_header, position)
            if find_header == -1:
                break

            find_end_char = file_bytes.find(end_char, find_header + spacing)
            if find_end_char == -1:
                break

            samplename_start = find_header + spacing
            samplename_end = find_end_char
            raw_samplename = file_bytes[samplename_start:samplename_end]
            samplename = raw_samplename.replace(b'\x00', b'').decode('ascii', 'replace')
            samplenames.append(samplename)
            position = find_end_char + self.absorbance_table_length

        if len(samplenames) < num_samples:
            remainder = num_samples - len(samplenames)
            blank_names = [''] * remainder
            samplenames.extend(blank_names)

        return samplenames

    def _find_samplename_header(self, file_bytes):
        """
        Search the binary file for the appropriate sample name header.

        Parameters
        ----------
        file_bytes : bytes
            The raw bytes of the binary file.

        Returns
        -------
        header : string
            The sample name header as a hex string.
        spacing : int
            The spacing between the header and the beginning of the actual data.
        end_char : bytes
            The end-of-data termination character.
        """
        # Each header contains its hex string, spacing, and termination character.
        headers = {
            'S a m p l e N a m e ': (b'\x53\x00\x61\x00\x6D\x00\x70\x00\x6C\x00\x65\x00\x4E\x00\x61\x00\x6D\x00\x65\x00', 28, b'\x09'),
            '(`DataType': (b'\x28\x60\x44\x61\x74\x61\x54\x79\x70\x65', 33, b'\x02')}
        for key, (header, spacing, end_char) in headers.items():
            if file_bytes.find(header, 0) != -1:
                return header, spacing, end_char
        return None, None, None

    def export_csv(self):
        """
        Export spectra as .csv files.

        For files containing multiple spectra, .csv files are exported to a
        folder named ``self.name`` in ``self.path``. For files with a single
        spectrum, a .csv file named ``self.name`` is exported to ``self.path``.

        For .SD files, if a spectrum has a sample name associated with it, the
        sample name will be added to the filename as well.

        Returns
        -------
        None.
        """
        print('Exporting .csv files...')

        def get_unique_directory(path):
            """If a folder named self.name exists, add a number after."""
            n = 1
            output_dir = path
            while os.path.exists(output_dir) is True:
                output_dir = os.path.splitext(self.path)[0] + f' ({n})'
                n += 1
            return output_dir

        def get_unique_filename(base_filename):
            """If a file named base_filename exists, add a number after."""
            n = 1
            unique_filename = base_filename
            while os.path.exists(f'{unique_filename}.csv'):
                unique_filename = base_filename + f' ({n})'
                n += 1
            return unique_filename

        if len(self.spectra) > 1:
            output_dir = get_unique_directory(os.path.splitext(self.path)[0])
            os.mkdir(output_dir)
            digits = len(str(len(self.spectra)))

            for i, (spectrum, samplename) in enumerate(zip(self.spectra, self.samplenames)):
                base_filename = f'{str(i + 1).zfill(digits)}'
                if samplename:
                    base_filename += f' - {samplename}'

                spectrum.to_csv(os.path.join(output_dir, f'{base_filename}.csv'), index=False)
            print(f'Finished export: {output_dir}')

        else:
            base_filename = os.path.splitext(self.path)[0]
            if self.samplenames[0]:
                base_filename += f' - {self.samplenames[0]}'

            filename = get_unique_filename(base_filename)
            self.spectra[0].to_csv(f'{filename}.csv', index=False)
            print(f'Finished export: {filename}.csv')


if __name__ == '__main__':
    PATH = os.path.normpath(input('Enter a file path or "q" to quit: '))
    BINARY_FILE = BinaryFile(PATH, export_csv=True)
