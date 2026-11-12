import copy
import datetime
import re
from typing import Dict, List, Sequence


class SWOTFilename:
    def __init__(self, filename: str, suffix='.nc'):
        filename_info = get_swot_filename_info(filename)
        self.filename = filename
        self.product_process_version = filename_info['product_process_version']
        self.product_version_major = filename_info['product_version_major']
        self.product_version_minor = filename_info['product_version_minor']
        self.product_process_counter = filename_info['product_process_counter']
        self.data_level = filename_info['data_level']
        self.product_type = filename_info['product_type']
        self.cycle_id = filename_info['cycle_id']
        self.pass_id = filename_info['pass_id']

        start_date = filename_info['start_date']
        start_hour_minute_second = filename_info['start_hour_minute_second']
        start_time = start_date + '-' + start_hour_minute_second
        self.acquire_time_start = datetime.datetime.strptime(start_time, '%Y%m%d-%H%M%S')

        end_date = filename_info['end_date']
        end_hour_minute_second = filename_info['end_hour_minute_second']
        end_time = end_date + '-' + end_hour_minute_second
        self.acquire_time_end = datetime.datetime.strptime(end_time, '%Y%m%d-%H%M%S')

    def __lt__(self, other):
        return self.acquire_time_start < other.acquire_time_start

    def __gt__(self, other):
        return self.acquire_time_start > other.acquire_time_start

    def __eq__(self, other):
        return self.acquire_time_start == other.acquire_time_start


def get_swot_filename_info(swot_filename) -> Dict:
    swot_filename_pattern = r'SWOT_L([23])_LR_SSH_(\w{5,10})_(\d{3})_(\d{3})_(202\d{5})T(\d{6})_(202\d{5})T(\d{6})'
    swot_filename_select = re.search(swot_filename_pattern, swot_filename)
    if swot_filename_select:
        data_level = int(swot_filename_select.group(1))
        product_type = str(swot_filename_select.group(2))
        cycle_id = str(swot_filename_select.group(3))
        pass_id = str(swot_filename_select.group(4))
        start_date = str(swot_filename_select.group(5))
        start_hour_minute_second = str(swot_filename_select.group(6))
        end_date = str(swot_filename_select.group(7))
        end_hour_minute_second = str(swot_filename_select.group(8))
    else:
        raise RuntimeError('unrecognized filename')
    product_process_version = None
    product_version_major = None
    product_version_minor = None
    product_process_counter = None
    if data_level == 2:
        swot_filename_pattern_l2 = r'SWOT_L([23])_LR_SSH_(\w{5,10})_(\d{3})_(\d{3})_(202\d{5})T(\d{6})_(202\d{5})T(\d{6})_P([GI])([ABCD])(\d{1})_(\d{2})'
        swot_filename_l2_select = re.search(swot_filename_pattern_l2, swot_filename)
        if swot_filename_l2_select:
            product_process_version = str(swot_filename_l2_select.group(9))
            # if product_process_version == 'I':
            #     logging.warning(f'{swot_filename} process version is "I", consider use "G" version data instead, for example: "PGD0"')
            product_version_major = str(swot_filename_l2_select.group(10))
            # if product_version_major in ['A', 'B', 'C']:
            #     logging.warning(
            #         f'{swot_filename} is old version: "{product_version_major}", consider use version D product instead')
            product_version_minor = int(swot_filename_l2_select.group(11))
            product_process_counter = int(swot_filename_l2_select.group(12))
    return {'product_process_version': product_process_version, 'product_version_major': product_version_major,
            'product_version_minor': product_version_minor, 'product_process_counter': product_process_counter,
            'data_level': data_level, 'product_type': product_type, 'cycle_id': cycle_id, 'pass_id': pass_id,
            'start_date': start_date, 'start_hour_minute_second': start_hour_minute_second,
            'end_date': end_date, 'end_hour_minute_second': end_hour_minute_second}


def find_similar_swot_filename(need_search_swot_filename: SWOTFilename,
                               need_search_list: Sequence[SWOTFilename] | Sequence[str]) -> List:
    similar_filename_list = []
    for target_swot_filename in need_search_list:
        if isinstance(target_swot_filename, str):
            target_swot_filename_obj = SWOTFilename(target_swot_filename)
        elif isinstance(target_swot_filename, SWOTFilename):
            target_swot_filename_obj = copy.deepcopy(target_swot_filename)
            target_swot_filename = target_swot_filename_obj.filename
        else:
            raise TypeError
        if (target_swot_filename_obj.product_process_version == need_search_swot_filename.product_process_version
                and target_swot_filename_obj.product_version_major == need_search_swot_filename.product_version_major
                and target_swot_filename_obj.product_version_minor == need_search_swot_filename.product_version_minor
                and target_swot_filename_obj.cycle_id == need_search_swot_filename.cycle_id
                and target_swot_filename_obj.pass_id == need_search_swot_filename.pass_id
                # start time and end time may be not the same
                # and target_swot_filename_obj.acquire_time_start == need_search_swot_filename.acquire_time_start
                # and target_swot_filename_obj.acquire_time_end == need_search_swot_filename.acquire_time_end
                and target_swot_filename_obj.product_process_counter != need_search_swot_filename.product_process_counter
        ):
            similar_filename_list.append(target_swot_filename)

    if len(similar_filename_list) != 0:
        similar_filename_list.append(need_search_swot_filename.filename)

    return similar_filename_list


if __name__ == '__main__':
    input_nc_filepath = r"SWOT_L2_LR_SSH_Unsmoothed_042_176_20251128T222515_20251128T231642_PID0_01.nc"
    swot_filename_object = SWOTFilename(input_nc_filepath)
    print(f'{swot_filename_object.acquire_time_start = }')
