import pickle
import time
import pandas as pd
import numpy as np
import requests
from datetime import date, timedelta, datetime
import os

class KrakenWrapper(object):
    endpoints = {
        "trade_assets": "https://api.kraken.com/0/public/AssetPairs",
        "ohlc_bars": "https://api.kraken.com/0/public/OHLC?pair={0}&since={1}&interval={2}",
        "files_path": "./hist_data/kraken_data/"
    }

    def __init__(self, key="", secret="", default_lookback = 233, default_lb_interval = 240):
        self.key = key
        self.secret = secret
        self.look_back = default_lookback
        self.lb_interval = default_lb_interval
        return

    def get_assets(self, base_pair):
        tradeable_assets = requests.get(self.endpoints["trade_assets"])
        asset_list = []
        #df = pd.DataFrame(tradeable_assets.json())
        for i in tradeable_assets.json()["result"]:
            if i[-(len(base_pair)):] == base_pair:
                asset_list.append(i)
        return asset_list

    def pull_kraken_hist_usd(self):
        sym_list = self.get_assets("USD")
        lookback_ts = datetime.today() - timedelta(self.look_back)
        for i in sym_list:
            hist_req = requests.get(self.endpoints["ohlc_bars"].format(i, lookback_ts, self.lb_interval))
            results = hist_req.json()["result"][i]
            with open("./hist_data/kraken_data/"+ i + ".txt", "a") as f:
                f.write("time,open,high,low,close,vwap,vol\n")
                for l in range(len(results)):
                    next_line = results[l]
                    for x in range(len(next_line)):
                        if(x != len(next_line)-1):
                            f.write(str(next_line[x]) + ",")
                        else:
                            f.write(str(next_line[x]))
                    f.write("\n")
            print(i, " written")

    def pull_single_sym_hist(self):
        sym_list = self.get_assets("USD")
        lookback_ts = datetime.today() - timedelta(self.look_back)
        sym = sym_list[0]
        hist_req = requests.get(self.endpoints["ohlc_bars"].format(sym, lookback_ts, self.lb_interval))
        results = hist_req.json()["result"][sym]
        for i in range(len(results)):
            print(results[i])

    def load_hist_files(self):
        histFiles = os.listdir(os.path.join(os.path.dirname(__file__), '../hist_data/kraken_data'))
        df_dict = {}
        for sym in histFiles:
            frame = pd.DataFrame().from_csv(self.endpoints["files_path"]+sym)
            frame['avg_vol_3'] = pd.Series(np.where(frame.vol.rolling(3).mean() / frame.vol, 1, 0),frame.index)
            frame['avg_close_3'] = pd.Series(np.where(frame.close.rolling(3).mean() / frame.close, 1, 0),frame.index)
            frame['avg_close_13'] = pd.Series(np.where(frame.close.rolling(21).mean() / frame.close.rolling(3).mean(), 1, 0),frame.index)
            frame['avg_close_34'] = pd.Series(np.where(frame.close.rolling(55).mean() / frame.close.rolling(21).mean(), 1, 0),frame.index)
            frame['std_close'] = frame['open']/frame['close']
            frame['std_high'] = frame['low']/frame['close']
            df_dict[sym] = frame
        return df_dict


    def combine_polo_usd_frames(self, restrict_val = 0):
        df_dict = self.load_hist_files()
        coin_and_hist_index = 0
        file_lens = []
        for y in df_dict:
            df = self.get_polo_usd_frame(df_dict[y])
            df_len = len(df)
            #print(df.head())
            file_lens.append(df_len)
        mode_len = mode(file_lens)
        print(mode_len)
        self.hist_full_size = mode_len
        vollist = []
        prefixes = []
        for x in df_dict:
            df = df_dict[x]
            col_prefix = self.get_file_symbol(fileNames[x])
            #as_array = np.array(df)
            if(len(df) == mode_len):
                #print(as_array)
                prefixes.append(col_prefix)
                self.currentHists[col_prefix] = df
                vollist.append(df['volume'][0])
        if restrict_val != 0:
            vollist = np.argsort(vollist)[-restrict_val:][::-1]
        vollist = np.argsort(vollist)[::-1]
        #print(vollist)
        for ix in vollist:
            print(prefixes[ix])
            df['volume'] = (df['volume'] - df['volume'].mean())/(df['volume'].max() - df['volume'].min())
            df = self.currentHists[prefixes[ix]][['volume', 'std_high', 'std_close', 'avg_vol_3', 'avg_close_3', 'avg_close_13', 'avg_close_34']].copy()
            #norm_df = (df - df.mean()) / (df.max() - df.min())
            as_array=np.array(df)
            self.hist_shaped[coin_and_hist_index] = as_array
            self.coin_dict[coin_and_hist_index] = prefixes[ix]
            coin_and_hist_index += 1
        self.hist_shaped = pd.Series(self.hist_shaped)

