from app.crud.loc_info_statistics import (
    get_stat_data,
    get_stat_data_by_city,
    get_stat_data_by_distirct
)

def select_stat_data(filters_dict):
    result = get_stat_data(filters_dict)
    return result

def select_stat_data_by_city(filters_dict):
    result = get_stat_data_by_city(filters_dict)
    return result

def select_stat_data_by_district(filters_dict):
    result = get_stat_data_by_distirct(filters_dict)
    return result