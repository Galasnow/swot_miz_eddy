from pathlib import Path
from typing import List

# root of repo (parent of scripts/)
REPO_ROOT = Path(__file__).resolve().parents[1]

import earthaccess
from earthaccess import DataGranule
import shapely

from swot_miz_eddy.common.geo_utils import build_polygon
from swot_miz_eddy.common.swot_filename import SWOTFilename, find_similar_swot_filename

### Config
tmin = "2023-08-01 00:00:00"
tmax = "2024-07-31 23:59:59"

product_type = "Expert"
# product_type = "Unsmoothed"
roi_shp_path = REPO_ROOT / "data" / "mask" / "research_area_enclosing" / "research_area_enclosing.shp"

if product_type == "Expert":
    download_dir = Path(r'F:\eddy\expert')
elif product_type == "Unsmoothed":
    download_dir = Path(r'F:\eddy\unsmoothed')
else:
    raise RuntimeError

filter_output_existence = True
output_npz_dir = r'D:\eddy\new_variables\npz'
output_tif_dir = r'D:\eddy\new_variables\tif'
filter_nc_file_existence = True
###

if not download_dir.is_dir():
    download_dir.mkdir()
search_area = build_polygon(str(roi_shp_path))
polygon = shapely.geometry.polygon.orient(shapely.Polygon(search_area), sign=1).exterior.coords


def extract_filename_from_data_granule(data_granule: DataGranule) -> str:
    data_links = data_granule.data_links()
    if len(data_links) == 1:
        data_links_item = data_links[0]
        filename = data_links_item.split('/')[-1]
    else:
        raise RuntimeError(f'unrecognized data_links: {data_links}')
    return filename


def filter_existing_result_list(earthdata_access_result_list: List[DataGranule], existing_filenames_list):
    filtered_list = []
    for item in earthdata_access_result_list:
        data_links = item.data_links()
        if len(data_links) == 1:
            data_links_item = data_links[0]
            item_name = data_links_item.split('/')[-1]
        else:
            raise RuntimeError(f'unrecognized data_links: {data_links}')
        if item_name not in existing_filenames_list:
            filtered_list.append(item)
    return filtered_list


def filter_low_counter_result_list(earthdata_access_result_list: List[DataGranule]):
    filename_list = [extract_filename_from_data_granule(item) for item in earthdata_access_result_list]
    filtered_list = []
    for i, item in enumerate(earthdata_access_result_list):
        item_name = filename_list[i]
        item_obj = SWOTFilename(item_name)
        similar_filename_list = find_similar_swot_filename(item_obj, filename_list[i - 10: i + 10])
        if len(similar_filename_list) == 0:
            filtered_list.append(item)
        elif len(similar_filename_list) >= 2:
            counter_list = [SWOTFilename(filename).product_process_counter for filename in similar_filename_list]
            max_index = counter_list.index(max(counter_list))
            max_filename = similar_filename_list[max_index]
            filtered_list.append(earthdata_access_result_list[filename_list.index(max_filename)])
        else:
            raise RuntimeError

    return filtered_list


def filter_output_existence_result_list(earthdata_access_result_list: List[DataGranule],
                                        output_npz_dir,
                                        output_tif_dir,
                                        groups=('left', 'right')):
    filtered_list = []
    for item in earthdata_access_result_list:
        for group_name in groups:
            nc_basename = extract_filename_from_data_granule(item)
            output_npz_path = Path(f"{output_npz_dir}/{nc_basename.replace('.nc', '')}_{group_name}.npz")
            output_tif_path = Path(f"{output_tif_dir}/{nc_basename.replace('.nc', '')}_{group_name}.tif")

            if not output_npz_path.exists() or not output_tif_path.exists():
                filtered_list.append(item)
                break

    filtered_list = list(dict.fromkeys(filtered_list))
    return filtered_list


if __name__ == "__main__":
    earthaccess.login(persist=True)

    karin_results = earthaccess.search_data(
    short_name="SWOT_L2_LR_SSH_D",
    temporal=(tmin, tmax),
    polygon=polygon,
    granule_name=f"SWOT_L2_LR_SSH_{product_type}_???_???_*_*_P?D?_??"
    )
    print(f'{len(karin_results) = }')

    filtered_results_1 = filter_low_counter_result_list(karin_results)
    del karin_results
    print(f'{len(filtered_results_1) = } files after filter small counter')

    if filter_output_existence and product_type == "Unsmoothed":
        # output filenames are named by Unsmoothed product
        filtered_results_2 = filter_output_existence_result_list(filtered_results_1, output_npz_dir, output_tif_dir)
        print(f'{len(filtered_results_2) = } files after filter output existence')
        del filtered_results_1
    else:
        filtered_results_2 = filtered_results_1

    if filter_nc_file_existence:
        existing_filenames_list = [filename for filename in download_dir.iterdir() 
                                if filename.is_file() and filename.suffix == '.nc']
        filtered_results = filter_existing_result_list(filtered_results_2, existing_filenames_list)
        print(f'{len(filtered_results) = } files after filter existing local files')
        del filtered_results_2
    else:
        filtered_results = filtered_results_2

    if len(filtered_results) == 0:
        print(f'no file in the filtered list, skip')
        pass
    else:
        if product_type == "Expert":
            threads_used = 8
        elif product_type == "Unsmoothed":
            threads_used = 2
        else:
            raise RuntimeError('Unknown product type')
        filelist = earthaccess.download(filtered_results, local_path=download_dir, threads=threads_used, show_progress=True)
