from pathlib import Path
from _data_io.dat_finder import DatFinder
from _data_io.dat_loader import load_ion_data
from _data_io.dat_saver import create_save_path_for_calc_ScanFile
from apps.c2t_calculation.domain.config import AnalysisConfig
from apps.c2t_calculation.domain.pipeline import run_pipeline
from apps.scan_averaging.domain.averaging import average_scans
from base_core.math.enums import AngleUnit
from base_core.math.models import Angle, Point, Range
from base_core.quantities.enums import Prefix
from base_core.quantities.models import Length


folder_path = Path(r"/home/soeren/Downloads/20260112_jet_raw and scanfiles/20260112_Jet_raw/JetScan4+5")
file_paths = DatFinder(folder_path).find_datafiles()

config_1 = AnalysisConfig(
    delay_center= Length(55, Prefix.MILLI),
    center=Point(189, 205),
    angle= Angle(12, AngleUnit.DEG),
    analysis_zone= Range[int](60, 120),
    transform_parameter= 0.75)

ion_data = load_ion_data(file_paths, config_1.delay_center)
save_path = create_save_path_for_calc_ScanFile(folder_path, str(ion_data[0].run_id))
calculated_Scan_1 = run_pipeline(ion_data,config_1, save_path)




folder_path = Path(r"/home/soeren/Downloads/20260112_jet_raw and scanfiles/20260112_Jet_raw/JetScan4+5")
file_paths = DatFinder(folder_path).find_datafiles()

config_2 = AnalysisConfig(
    delay_center= Length(55, Prefix.MILLI),
    center=Point(189, 205),
    angle= Angle(12, AngleUnit.DEG),
    analysis_zone= Range[int](60, 120),
    transform_parameter= 0.75)

ion_data = load_ion_data(file_paths, config_2.delay_center)
save_path = create_save_path_for_calc_ScanFile(folder_path, str(ion_data[0].run_id))
calculated_Scan_2 = run_pipeline(ion_data,config_2, save_path)





averagedScanData = average_scans([calculated_Scan_1, calculated_Scan_2])