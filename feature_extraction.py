"""feature extraction
generalize process of feature extraction by abstracting the individual steps
"""

from typing import Dict, List, Optional, Tuple, Union, Set
from pathlib import Path
from xml.etree import ElementTree as ET

# third party imports
import pandas as pd
from fastai.tabular import *

FileOrFolderPath = FilePath = FolderPath = Union[str, Path]
Permissions = List[str]

# TODO: replace hardcoded paths to folder crawling functionality
ALL_PERMISSIONS_CSV = Path('/home/milton/Code/Work/apk-total/Data/permissions_csv/all-permissions-from-fdroid-repos.csv')
ANDROID_MANIFEST_PATH = Path('/home/milton/Code/Work/apk-total/Data/')  # base path
ANDROID_MANIFEST_XML_PATH = ANDROID_MANIFEST_PATH/'permissions_xml'  # source
ANDROID_MANIFEST_CSV_PATH = ANDROID_MANIFEST_PATH/'permissions_csv'  # target
IKARUS_DS = ANDROID_MANIFEST_CSV_PATH/'ikarus'

LABELS_TO_CONVERT = ['clean', 'adware']
ID:str = 'ID'


class FeatureExtractor:
    def __init__(self, folder_path: FolderPath):
        self.folder_path = folder_path  # folder containing AndroidManifest.xml files

    def extract_features(self, max_file_nr=None):
        #for i, file in enumerate(self.folder_path.iterdir()):
        for i, file in enumerate(self.folder_path.rglob("*.xml")):  # TODO: change for other features
            if max_file_nr is not None and i >= max_file_nr:  # max_file_nr is for testing
                break
            try:
                PermissionExtractor(file).append_to_csv()
                # TODO: add other FeatureExtractors e.g. IGrepExtractor, LibraryExtractor, ...
            except ET.ParseError:
                continue  # TODO: add logging for not well formed xml files
            except ValueError:  # will be raised if a folder has been passed to individual FeatureExtractors
                continue


class PermissionExtractor:
    def __init__(self, file_path: FileOrFolderPath):
        file = Path(file_path).absolute()

        # file validation
        if not file.is_file() and file.suffix == '.xml':
            raise ValueError(f'{file} is not a valid .xml file')

        self.file_name: FilePath = file.name
        self.file_path: FolderPath = file.parent
        self.requested_permissions: Optional[Set[str]] = None
        self.label: Optional[str] = None  # TODO: label with 0/1 or str?
        self.target_name: FilePath = self.get_target_path(file)

    @staticmethod
    def get_all_permissions() -> pd.Series:
        """create a Pandas Series with the names of all possible Android permissions
        use for the column names for Pandas DataFrames"""

        # without squeeze read_csv() would return a DataFrame instead of a Series
        return pd.read_csv(ALL_PERMISSIONS_CSV, squeeze=True, header=None)

    def get_requested_permissions(self):
        """extract the permissions from the given AndroidManifest.xml file
        return a dict with the filename as key, and list of permissions as value
        """
        # create xml tree and search for permission tags
        file = self.file_path/self.file_name
        tree = ET.parse(file)
        permissions = tree.findall('uses-permission')  # type: List[ET.Element]

        # loop over xml tree and gather permissions in a list
        permissions_requested = []
        for perm in permissions:  # type: ET.Element
            for p in perm.items():  # type: Tuple[str, str]
                permissions_requested.append(p[1])  # actual permission

        # TODO: add logging if found permission was not in known (all) permissions?
        self.requested_permissions = set(permissions_requested)

    def csv2vec(self) -> List[int]:
        """file_name should refer to a csv file, permissions is a dict
        with filename as key and list of extracted permissions as values
        return an List[int]
        where int is either 0 if permission was not requested, else 1"""

        # extract the permissions requested by AndroidManifest.xml
        if self.requested_permissions is None:
            self.get_requested_permissions()

        # get the permissions for the current file
        all_perms_series = self.get_all_permissions()  # type: pd.Series

        # create the input vector for the ML model
        vector: List[int] = []
        for p in all_perms_series:
            if p in self.requested_permissions:
                vector.append(1)
            else:
                vector.append(0)
        return vector

    def get_target_path(self) -> FilePath:
        """input: path to xml file
        return absolute path to csv file (many to one mapping)"""
        out_path = str(self.file_path).replace('permissions_xml', 'permissions_csv')
        return Path(out_path)/'permissions.csv'

    def init_csv(self, target_csv: Union[str, Path] = None) -> None:
        """return the path to a csv with only the Android permissions as column names, no rows yet"""
        # create parent directories if necessary
        if not self.target_name.parent.is_dir():
            os.makedirs(self.target_name.parent)
        all_perms = self.get_all_permissions()  # type: pd.Series

        # write column names only if the file doesn't already exist
        with open(self.target_name, 'w') as target:
            csv_writer = csv.writer(target)
            csv_writer.writerow([ID] + [p for p in all_perms])

    def append_to_csv(self):
        # if target csv file does not exist, create it and initialize columns
        if not self.target_name.is_file():
            self.init_csv(self.target_name)

        # append the feature vector
        with open(self.target_name, 'a') as target:
            csv_writer = csv.writer(target)
            csv_writer.writerow([self.get_id()] + self.csv2vec())

    def get_id(self):
        """example: failtest_10111652.AndroidManifest.xml
        would return failtest_10111652
        """
        return str(self.file_name).split('.')[0]



class IpExtractor:
    def __init__(self, file_path: FileOrFolderPath):
        file = Path(file_path).absolute()

        # file validation
        if not file.is_file():  # TODO: add more file validation if necessary
            continue

        self.file_name: FilePath = file.name
        self.file_path: FolderPath = file.parent
        self.found_urls: Optional[Set[str]] = None
        self.label: Optional[str] = None  # TODO: label with 0/1 or str?
        self.target_name: FilePath = self.get_target_path(file)

    def get_target_path(self, path: FileOrFolderPath = None ) -> FilePath:
        return path  # stub TODO: fill out stub

    def get_all_urls(self):
        pass  # TODO: implement

    def get_current_urls(self):
        pass  # TODO: implement

    def file2vec(self) -> List[int]:
        pass  # TODO: implement

    def init_csv(self, target_csv: Union[str, Path] = None) -> None:
        pass  # TODO: implement

    def append_to_csv(self):
        pass  # TODO: implement





if __name__ == '__main__':
    import time
    t0 = time.time()
    clean_folder = Path('/home/milton/Code/Work/apk-total/Data/permissions_xml/ikarus/clean/')
    adware_folder = Path('/home/milton/Code/Work/apk-total/Data/permissions_xml/ikarus/adware/')
    FeatureExtractor(clean_folder).extract_features()  # (max_file_nr=1000)  # for testing
    FeatureExtractor(adware_folder).extract_features()  # (max_file_nr=1000)  # for testing
    t1 = time.time()
    print(f'done... it took {t1 - t0} seconds')
