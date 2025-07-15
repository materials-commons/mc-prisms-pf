import os
import re
import pandas
from pathlib import Path


def _get_file_contents(path: Path):
    return path.read_text()


def _exists(path: Path):
    return path.exists()


class ParameterFileParser:
    def __init__(self):
        self.parameters = {}
        self.section_stack = []

    def parse(self, prm_file):
        current_section = self.parameters
        with open(prm_file, 'r') as f:
            for line in f:

                line = line.strip()

                if not line:
                    # skip empty files
                    continue

                if line.startswith("#"):
                    # skip comments
                    continue

                # Detect subsection
                subsection_match = re.match(r"subsection\s+(.+)", line)

                # Start of subsection
                if subsection_match:
                    subsection = subsection_match.group(1).strip()
                    if subsection not in self.parameters:
                        current_section[subsection] = {}
                    self.section_stack.append(current_section)
                    current_section = current_section[subsection]
                    continue

                # Detect the end of a subsection
                if line == "end":
                    if self.section_stack:
                        current_section = self.section_stack.pop()
                    continue

                # Match set pattern for `set <key> = <value> [type]` and extract out key and value
                key_value_match = re.match(r"set\s+(.+?)\s*=\s*(.+?)(?:\s*,\s*(\S+))?$", line)
                if key_value_match:
                    key = key_value_match.group(1).strip()
                    value = key_value_match.group(2).strip()
                    if key_value_match.group(3):
                        value_type = key_value_match.group(3).strip()
                    else:
                        value_type = None
                    current_section[key] = {"value": value, "type": value_type}
                else:
                    print(f"Warning: Unable to parse line: {line}")

    def to_params(self, calculation, source_directory):
        description_path = Path(source_directory) / "description.txt"
        description = _get_file_contents(description_path) if _exists(description_path) else ""

        observations_path = Path(source_directory) / "observations.txt"
        observations = _get_file_contents(observations_path) if _exists(observations_path) else ""

        description = Path(source_directory) / "description.txt"
        return {
            "c:Calculation": calculation,

        }
            calculation=calculation,
            description=description,
            observations=observations,
            **self.parameters
        )


def add_to_excel(params, calculation, excel_file_path):
    data_frame = pandas.DataFrame([params])
    if not os.path.exists(excel_file_path):
        data_frame.to_excel(excel_file_path, index=False)
        return

    existing_data_frame = pandas.read_excel(excel_file_path)
    if not set(existing_data_frame.columns).issubset(set(data_frame.columns)):
        raise Exception("Existing excel file does not have the same columns as the new data")

    with pandas.ExcelWriter(excel_file_path, mode='a', engine='openpyxl', if_sheet_exists="overlay") as writer:
        existing_data_frame.to_excel(writer, sheet_name=calculation, index=False, header=False,
                                     startrow=writer.sheets[calculation].max_row)

