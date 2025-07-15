import glob
import os
import shutil
import time


class ImportSimulator:
    """
    A class to organize PRISMS-PF files for Materials Commons importing.
    This is a Python implementation of the functionality in importsim.sh.
    """

    def __init__(self):
        """Initialize the ImportSimulator."""
        self.src_dir = None
        self.dst_dir = None
        self.copy_output = True
        self.start_time = None

    def organize_files(self, src_dir, dst_dir=None, copy_output=True):
        """
        Organize files from the source directory into a structured destination directory.

        Args:
            src_dir (str): Source directory containing files to organize
            dst_dir (str, optional): Destination directory for organized files.
                If not provided, uses the basename of src_dir in the current directory.
            copy_output (bool, optional): Whether to copy (True) or move (False) output files.
                Defaults to True.

        Returns:
            dict: A dictionary containing information about the operation:
                - 'src_dir': The absolute path of the source directory
                - 'dst_dir': The absolute path of the destination directory
                - 'elapsed_time': Time taken to complete the operation in seconds
                - 'success': Boolean indicating if the operation was successful
                - 'message': A message describing the result of the operation
        """
        self.start_time = time.time()
        self.src_dir = os.path.abspath(os.path.expanduser(src_dir))
        self.copy_output = copy_output

        # If dst_dir is not provided, use the basename of src_dir
        if dst_dir is None:
            last_folder = os.path.basename(self.src_dir)
            self.dst_dir = os.path.abspath(os.path.join(".", last_folder))
        else:
            self.dst_dir = os.path.abspath(os.path.expanduser(dst_dir))

        # Check if the source directory exists
        if not os.path.isdir(self.src_dir):
            return self._create_result(False, f"Source directory '{self.src_dir}' does not exist.")

        # Create destination directory structure
        try:
            self._create_directory_structure()
        except Exception as e:
            return self._create_result(False, f"Failed to create directory structure: {str(e)}")

        # Organize files
        try:
            self._organize_files()
        except Exception as e:
            return self._create_result(False, f"Failed to organize files: {str(e)}")

        elapsed_time = time.time() - self.start_time
        return self._create_result(True, f"File organization completed in {elapsed_time:.2f} seconds.")

    def _create_directory_structure(self):
        """Create the destination directory structure."""
        # Create the main destination directory if it doesn't exist
        os.makedirs(self.dst_dir, exist_ok=True)

        # Create subdirectories
        self.code_dir = os.path.join(self.dst_dir, "code")
        self.data_dir = os.path.join(self.dst_dir, "data")
        self.output_dir = os.path.join(self.data_dir, "vtk")
        self.image_dir = os.path.join(self.data_dir, "images")
        self.movie_dir = os.path.join(self.data_dir, "movies")
        self.postprocess_dir = os.path.join(self.data_dir, "postprocess")

        # Create all subdirectories
        for directory in [self.code_dir, self.data_dir, self.output_dir, 
                         self.image_dir, self.movie_dir, self.postprocess_dir]:
            os.makedirs(directory, exist_ok=True)

    def _organize_files(self):
        """Organize files from the source directory into the destination directory structure."""
        # Copy code files
        code_extensions = ["*.cc", "*.c", "*.cpp", "*.cxx", "*.h", "*.hpp", 
                          "*.prm", "*.py", "*.sh", "*.json", "*.yaml", "*.yml"]
        self._copy_files_by_pattern(code_extensions, self.code_dir, copy=True)

        # Copy or move output files
        output_extensions = ["*.vtk", "*.vtu", "*.pvtu"]
        self._copy_files_by_pattern(output_extensions, self.output_dir, copy=self.copy_output)

        # Copy markdown files to the root destination directory
        self._copy_files_by_pattern(["*.md"], self.dst_dir, copy=True)

        # Handle special case files
        self._handle_special_files()

    def _copy_files_by_pattern(self, patterns, destination, copy=True):
        """
        Copy or move files matching the given patterns to the destination directory.

        Args:
            patterns (list): List of glob patterns to match files
            destination (str): Destination directory
            copy (bool): Whether to copy (True) or move (False) the files
        """
        found_files = False
        for pattern in patterns:
            matching_files = glob.glob(os.path.join(self.src_dir, pattern))
            if matching_files:
                found_files = True
                for file_path in matching_files:
                    if copy:
                        shutil.copy2(file_path, destination)
                    else:
                        shutil.move(file_path, destination)

        return found_files

    def _handle_special_files(self):
        """Handle special case files like CMakeLists.txt and integratedFields.txt."""
        # Check for CMakeLists.txt
        cmake_file = os.path.join(self.src_dir, "CMakeLists.txt")
        if os.path.isfile(cmake_file):
            shutil.copy2(cmake_file, self.code_dir)

        # Check for integratedFields.txt
        integrated_fields_file = os.path.join(self.src_dir, "integratedFields.txt")
        if os.path.isfile(integrated_fields_file):
            shutil.copy2(integrated_fields_file, self.postprocess_dir)

    def _create_result(self, success, message):
        """
        Create a result dictionary with information about the operation.

        Args:
            success (bool): Whether the operation was successful
            message (str): A message describing the result

        Returns:
            dict: A dictionary with information about the operation
        """
        elapsed_time = time.time() - self.start_time if self.start_time else 0
        return {
            'src_dir': self.src_dir,
            'dst_dir': self.dst_dir,
            'elapsed_time': elapsed_time,
            'success': success,
            'message': message
        }


# API functions
def organize_files(src_dir, dst_dir=None, copy_output=True):
    """
    Organize files from the source directory into a structured destination directory.

    Args:
        src_dir (str): Source directory containing files to organize
        dst_dir (str, optional): Destination directory for organized files.
            If not provided, uses the basename of src_dir in the current directory.
        copy_output (bool, optional): Whether to copy (True) or move (False) output files.
            Defaults to True.

    Returns:
        dict: A dictionary containing information about the operation:
            - 'src_dir': The absolute path of the source directory
            - 'dst_dir': The absolute path of the destination directory
            - 'elapsed_time': Time taken to complete the operation in seconds
            - 'success': Boolean indicating if the operation was successful
            - 'message': A message describing the result of the operation
    """
    importer = ImportSimulator()
    return importer.organize_files(src_dir, dst_dir, copy_output)