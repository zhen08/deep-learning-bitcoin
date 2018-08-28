import os
import shutil
import sys
from time import time
from uuid import uuid4
from multiprocessing import Process

import numpy as np
import pandas as pd

from data_manager import file_processor
from returns_quantization import add_returns_in_place
from utils import *

np.set_printoptions(threshold=np.nan)
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

slice_size_4hours = 48
slice_size_12hours = 144
slice_size_2days = 576
slice_size_1week = 2016

def generate_up_down(data_folder, bitcoin_file):
    def get_price_direction(btc_df, btc_slice, i):
        # last_price = btc_slice[-2:-1]['price_close'].values[0] #this is actually the second last price
        last_price = btc_slice[-1:]['price_close'].values[0] #one option to get the correct last price
        # last_price = btc_df[i + slice_size - 1:i + slice_size]['price_close'].values[0] #another option to get the correct last price
        next_slice_prices = btc_df[i:i + slice_size_12hours]
        #print(next_slice_prices)
        maxPrice = next_slice_prices['price_close'].values.max()
        #print("Max Price {0}",maxPrice)
        minPrice = next_slice_prices['price_close'].values.min()
        #print("Min Price {0}",minPrice)
        
        if maxPrice > last_price:
            increase_percent = 100*((maxPrice-last_price)/last_price)
        else:
            increase_percent = 0

        if minPrice < last_price:
            decrease_percent = 100*((last_price-minPrice)/last_price)
        else:
            decrease_percent = 0

#        next_price = btc_df[i + slice_size:i + slice_size + 1]['price_close'].values[0]
        if (increase_percent >= 2.5) & (increase_percent > decrease_percent):
            class_name = "LONG"
        elif  (decrease_percent > increase_percent) & (decrease_percent >= 2.5):   
            class_name = "SHORT"
        else:
            class_name = 'HOLD'
        return class_name

    return generate_cnn_dataset(data_folder, bitcoin_file, get_price_direction)


def generate_cnn_dataset(data_folder, bitcoin_file, get_class_name):
    btc_df = file_processor(bitcoin_file)
#    btc_df, levels = add_returns_in_place(btc_df)

#    print('-' * 80)
#    print('Those values should be roughly equal to 1/len(levels):')
#    for ii in range(len(levels)):
#        print(ii, np.mean((btc_df['close_price_returns_labels'] == ii).values))
#    print(levels)
#    print('-' * 80)

    test_every_steps = 10
    n = len(btc_df) - slice_size_1week

    #shutil.rmtree(data_folder, ignore_errors=True)
    for epoch in range(int(1e5)):
        st = time()

        i = np.random.choice(n) + slice_size_1week

        btc_slice_4hours = btc_df[i-slice_size_4hours:i]
        btc_slice_12hours = btc_df[i-slice_size_12hours:i]
        btc_slice_2days = btc_df[i-slice_size_2days:i]
        btc_slice_1week = btc_df[i-slice_size_1week:i]

        if btc_slice_1week.isnull().values.any():
            raise Exception('NaN values detected. Please remove them.')

        class_name = get_class_name(btc_df, btc_slice_4hours, i)
        save_dir = os.path.join(data_folder, 'train', class_name)
        if epoch % test_every_steps == 0:
            save_dir = os.path.join(data_folder, 'test', class_name)
        mkdir_p(save_dir)
        fid = uuid4()
        filename = save_dir + '/' + str(fid) + '.png'
        #filenamen = save_dir + '/' + str(fid) + 'n.png'
        save_to_file(btc_slice_4hours, btc_slice_12hours, btc_slice_2days, btc_slice_1week, filename=filename)
        #save_to_file(btc_df[i:i + slice_size+slice_size], filename=filenamen)
        print('epoch = {0}, time = {1:.3f}, filename = {2}'.format(str(epoch).zfill(8), time() - st, filename))


def main(arg):
    data_folder = "data"
    bitcoin_file = "data/coinbaseUSD.csv"

    generate_up_down(data_folder, bitcoin_file)
    print("Finished")

if __name__ == '__main__':
    args = sys.argv
    if len(args) == 1:
        main(1)
    else:
        number_of_processes = args[1]
        print('Start {} processes.'.format(number_of_processes))
        procs = []
        for index, number in enumerate(range(int(number_of_processes))):
            proc = Process(target=main, args=(number,))
            procs.append(proc)
            proc.start()
 
        for proc in procs:
            proc.join()
 
 