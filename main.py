#! python3

### Main function to run the entire chain of downloading and extracting data


import logging, os, download_tidy_up as dtu, sys, db_data_lake as dl, db_data_refinery as dr, pandas as pd

## Set up paths
data_folder = os.path.join(os.getcwd(), 'downloaded_data')
snotel_folder = os.path.join(data_folder, 'snotel')
sf_folder = os.path.join(data_folder, 'streamflow')
tidal_folder = os.path.join(data_folder, 'tide_gauge')
wsu_folder = os.path.join(data_folder, 'wsu')
wsu_subfolder = os.path.join(wsu_folder, 'tidied_data_weather')
sl_file = os.path.join(wsu_folder, 'tidied_data_wsu_weather_station_list.csv')
sl_ps_file = os.path.join(wsu_folder, 'puget_sound_stations.csv')
si_file = os.path.join(wsu_folder, 'tidied_data_wsu_weather_station_info.csv')
# Toggle between windows or mac
# gecko_fullpath = os.path.join(os.getcwd(),'geckodriver_bins','mac','geckodriver')
gecko_fullpath = os.path.join(os.getcwd(), 'geckodriver_bins', 'win', 'geckodriver.exe')
dl_folder = os.path.join(os.getcwd(), 'sqlite', 'dl')
wrk_folder = os.path.join(os.getcwd(), 'sqlite')
dr_folder = os.path.join(os.getcwd(), 'sqlite', 'dr')
nClim_output_folder = os.path.join(data_folder,'nclimdiv')
nClim_raw_output_folder = os.path.join(nClim_output_folder,'raw_data')

## Set up logging file
logging.basicConfig(level=logging.INFO
                    , filename='main_logging.txt'
                    , format=' %(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.info('Start main.py')

## Set up standard out file
sdpath = os.path.join('main_stdout.txt')
sys.stdout = open(sdpath, 'w')
sys.stderr = open(sdpath, 'a')

## Set up a second handler for output to stdout
root = logging.getLogger()
root.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

# logging.info('Before exception')
# raise Exception ('Deliberate exception')
'''
## Download and minimally tidy up data
logging.info('Getting CO2 Data')
dtu.get_CO2_conc(output_folder=data_folder)
logging.info('Getting NOAA US climate data')
dtu.get_nClimDiv(output_folder=nClim_output_folder,raw_output_folder=nClim_raw_output_folder)
logging.info('Getting Snotel Data')
dtu.get_snotel_data(snotel_folder)
logging.info('Getting tidal gauge data')
dtu.get_tidal_data(tidal_folder)
logging.info('Getting streamflow data')
dtu.get_usgs_streamflow(sf_folder)
logging.info('Getting global temperature data')
dtu.get_global_temp_data(output_folder=data_folder)
## World Bank Data is two years out of date, disable update and update file manually using worldometer.info
#logging.info('Getting population data from World Bank')
#dtu.get_wb_data(output_folder=data_folder, indicator_id='SP.POP.TOTL', indicator='Population, total', country='WLD')
logging.info('Getting grain data from USDA')
dtu.get_grain_data(output_folder=data_folder
                  ,baseurl='https://apps.fas.usda.gov/psdonline/downloads/'
                  ,filename = 'psd_grains_pulses_csv.zip')

# Update station list
dtu.get_wsu_station_list(output_folder=wsu_folder)
'''


# Download WSU weather data
logging.info('Getting WSU weather data')
dtu.get_wsu_weather_data(output_folder=wsu_subfolder,station_list_file=sl_file,
                       station_info_file = si_file, gecko_fullpath=gecko_fullpath)

'''
#logging.info('Create data lakes')
#dl.create_data_lakes(sl_file=sl_file,dl_folder=dl_folder,overwrite=False)

logging.info('Loading csv files into data lake')
dl.load_dl_wsu_weather(sl_file=sl_ps_file, csv_base_folder=wsu_subfolder, dl_folder = dl_folder, overwrite = False)

#logging.info('Create data refineries')
#dr.create_data_refineries(sl_file=sl_file, dr_folder = dr_folder, overwrite=False)

logging.info('Calling wsu_progress')
dtu.wsu_progress(station_list_file=sl_file,output_folder=wsu_folder, scan_folder=wsu_subfolder
                , dl_folder=dl_folder, dr_folder=dr_folder)


logging.info('Entering loop for loading data lake into data refinery')
stat_list = pd.read_csv(sl_ps_file)
logging.info(str(stat_list.loc[:, 'station_id']))
for this_stat in stat_list.loc[:, 'station_id']:
    logging.debug('very start of loop')
    this_stat = str(this_stat)
    logging.debug('start loop of ' + this_stat)
    logging.debug('loading ' + this_stat)
    try:
        dr.load_wsu_weather_dl_to_dr(this_stat=this_stat, dl_folder=dl_folder, working_folder = wrk_folder, dr_folder = dr_folder)
    except Exception as e:
        logging.warning('load_wsu_weather_dl_to_dr: Error thrown')
        logging.warning('The exception caught:')
        logging.warning(str(e))
        logging.info(str(e.args))
        logging.warning('Moving on to next station')
        continue




logging.info('Calling wsu_min_max')
dtu.wsu_min_max(data_folder=wsu_folder, station_list_file=sl_ps_file)


'''

logging.info('Calling wsu_progress')
dtu.wsu_progress(station_list_file=sl_file,output_folder=wsu_folder, scan_folder=wsu_subfolder, dl_folder=dl_folder
                 , dr_folder=dr_folder)

logging.info('End main.py')