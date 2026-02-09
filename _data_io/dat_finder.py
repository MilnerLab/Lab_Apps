from pathlib import Path
import os

if os.name == "nt":  # Windows
    MOST_RECENT_FOLDER = Path(r"Z:\Droplets")
else:                # Linux
    MOST_RECENT_FOLDER = Path("/mnt/valeryshare/Droplets/")

SCAN_FILE_PATTERN = '*ScanFile.dat'
BATCH_PATTERN = '*ScanFile.txt'
ION_FILE_PATTERN = '*mm.dat'

def convert_to_system_path(paths: list[Path]) -> list[Path]:
    """
    Treat incoming paths as relative to MOST_RECENT_FOLDER and return
    paths that work on the current OS.

    Fixes cases like '20260206\\Scan7' on Linux by splitting backslashes
    into proper path parts.
    """
    out: list[Path] = []

    for p in paths:
        s = str(p)

        # If it's already absolute, keep it as-is (extra safety)
        if Path(s).is_absolute():
            out.append(Path(s))
            continue

        # Normalize separators for relative paths:
        # Turn both "\" and "/" into the current OS semantics via parts
        parts = [part for part in s.replace("\\", "/").split("/") if part]
        rel = Path(*parts)

        out.append(MOST_RECENT_FOLDER / rel)

    return out

class DatFinder:
    def __init__(self, folder_paths: Path | list[Path] | None = None, is_full_path: bool = False):
        if folder_paths is None:
            folder_paths = [MOST_RECENT_FOLDER]
        elif isinstance(folder_paths, Path):
            folder_paths = [folder_paths]
        else:
            folder_paths = list(folder_paths)  # falls tuple, generator, etc.

        if not is_full_path and folder_paths is not None:
            self.folder_paths: list[Path] = convert_to_system_path(folder_paths)
        else:   
            self.folder_paths: list[Path] = folder_paths
        
    def find_scanfiles(self,merge_batches = False) -> list[Path]:
        scans_paths: list[list[Path]] = []
        
        for f in self.folder_paths:
            
            file_list: list[Path] = sorted(f.glob(SCAN_FILE_PATTERN))

            if not file_list:
                continue

            if f == MOST_RECENT_FOLDER:
                txt_files = sorted(f.glob(BATCH_PATTERN))

                if txt_files:
                    newest_batch_stem = txt_files[-1].stem
                    if merge_batches == True:
                        file_list = [f for f in file_list]
                    else:
                        file_list = [f for f in file_list if f.stem >= newest_batch_stem]

                if not file_list:
                    continue

                scans_paths.append(file_list)
            else:
                scans_paths.append(file_list)
            
        return scans_paths

    def find_most_recent_scanfile(self) -> Path:
        file_list = list(MOST_RECENT_FOLDER.glob(SCAN_FILE_PATTERN)) 
        file_list = sorted(file_list)

        return file_list[-1]

    def find_datafiles(self)-> list[list[Path]]:
        scans_paths: list[list[Path]] = []
        
        for f in self.folder_paths:
            all_files = list(f.glob(ION_FILE_PATTERN))
            all_files.sort()
            
            scans_paths.append(all_files)
        
        return scans_paths

    