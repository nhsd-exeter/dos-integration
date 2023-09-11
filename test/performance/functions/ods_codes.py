from csv import reader
from random import choice


class OdsCodes:
    """Class to get valid and invalid pharmacy ods codes."""

    invalid_ods_codes: list[list[str]] | None = None
    valid_ods_codes: list[list[str]] | None = None

    def get_ods_codes_from_file(self, ods_code_file: str) -> list[list[str]]:
        """Get the ods codes from a file.

        Args:
            ods_code_file (str): The name of the file to get the ods codes from

        Returns:
            list[list[str]]: The list of ods codes
        """
        with open(f"resources/{ods_code_file}") as file:
            csv_reader = reader(file)
            return list(csv_reader)

    def generic_get_ods_code(
        self,
        ods_code_file_name: str,
        odscode_list: list[list[str]] | None,
    ) -> tuple[str, list[list[str]]]:
        """Get a random ods code from list or file if list is empty.

        Args:
            ods_code_file_name (str): The name of the file to get the ods codes from if the list is empty
            odscode_list (Optional[list[list[str]]]): The list of ods codes to get the odscode from

        Returns:
            Tuple[str, list[list[str]]]: The odscode and the list of ods codes
        """
        if odscode_list is None or len(odscode_list) == 0:
            odscode_list = self.get_ods_codes_from_file(ods_code_file_name)
        odscode_list_of_one = choice(odscode_list)
        odscode_list.remove(odscode_list_of_one)
        return odscode_list_of_one[0], odscode_list

    def get_valid_ods_code(self) -> str:
        """Get a valid pharmacy ods code.

        Returns:
            str: The valid ods code
        """
        odscode, self.valid_ods_codes = self.generic_get_ods_code("valid_ods_codes.csv", self.valid_ods_codes)
        return odscode

    def get_invalid_ods_code(self) -> str:
        """Get an invalid pharmacy ods code.

        Returns:
            str:  The invalid ods code
        """
        odscode, self.invalid_ods_codes = self.generic_get_ods_code("invalid_ods_codes.csv", self.invalid_ods_codes)
        return odscode


ODS_CODES = OdsCodes()
