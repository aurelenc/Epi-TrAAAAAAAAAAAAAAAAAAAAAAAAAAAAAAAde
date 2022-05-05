#!/usr/bin/python3
# -*- coding: iso-8859-1 -*
""" Python starter bot for the Crypto Trader games, from ex-Riddles.io """
__version__ = "1.0"

from os import remove
import sys
import numpy as np

class Bot:
    def __init__(self):
        self.botState = BotState()
        self.low = 0
        self.high = 0
        self.last = 0
        self.tendency = 0
        self.transaction = 0
        self.vals = []

    def run(self):
        while True:
            reading = input()
            if len(reading) == 0:
                continue
            self.parse(reading)

    def parse(self, info: str):
        tmp = info.split(" ")
        if tmp[0] == "settings":
            self.botState.update_settings(tmp[1], tmp[2])
        if tmp[0] == "update":
            if tmp[1] == "game":
                self.botState.update_game(tmp[2], tmp[3])
        if tmp[0] == "action":
            # This won't work every time, but it works sometimes!
            dollars = self.botState.stacks["USDT"]
            bitcoin = self.botState.stacks["BTC"]
            current_closing_price = self.botState.charts["USDT_BTC"].closes[-1]
            affordable = dollars / current_closing_price
            # sellable = bitcoin / current_closing_price
            print(f'My stacks are {dollars}. The current closing price is {current_closing_price}. So I can afford {affordable}', file=sys.stderr)
            print(f'My stacks are {bitcoin}. The current closing price is {current_closing_price}. So I can sell {bitcoin}', file=sys.stderr)
            # if dollars < 100:
            #     print("no_moves", flush=True)
            # if (self.high > current_closing_price + self.last) and affordable > 0.01:
            #     print(f'buy USDT_BTC {affordable}', flush=True)
            # elif (self.low < current_closing_price - self.last) and bitcoin > 0.01:
            #     print(f'sell USDT_BTC {sellable}', flush=True)
            # else:
            #     print("no_moves", flush=True)
            # # if np.mean(self.vals) > current_closing_price and (0.5 * sellable) > 0.01:
            #     print(f'sell USDT_BTC {0.5 * sellable}', flush=True)
            # elif np.mean(self.vals) < current_closing_price and (0.5 * affordable) > 0.01:
            #     print(f'buy USDT_BTC {0.5 * affordable}', flush=True)
            # else:
            #     print("no_moves", flush=True)
            # self.vals.append(current_closing_price)
            # if len(self.vals) > 7:
            #    self.vals.remove(self.vals[0])
            if (self.last > current_closing_price):
                # print(f'sell USDT_BTC {bitcoin * 0.9}', flush=True, file=sys.stderr)
                if (self.tendency == 2 and bitcoin > 0.001 and current_closing_price > self.transaction):
                # if (bitcoin > 0.001 and current_closing_price > self.transaction):
                    print(f'sell USDT_BTC {bitcoin}', flush=True)
                else:
                    print("no_moves", flush=True)
                self.tendency = 1
            elif (self.last < current_closing_price):
                # print(f'buy USDT_BTC {affordable * 0.9}', flush=True, file=sys.stderr)
                if (self.tendency == 1 and affordable > 0.001):
                # if (affordable * 0.2 > 0.001):
                    print(f'buy USDT_BTC {affordable}', flush=True)
                    self.transaction = current_closing_price
                else:
                    print("no_moves", flush=True)
                self.tendency = 2
            else:
                print("no_moves", flush=True)
            self.last = current_closing_price
            self.low = current_closing_price - self.last
            self.high = current_closing_price + self.last
            # elif dollars % 2 == 0 and 0.5 * sellable > 0.01:


class Candle:
    def __init__(self, format, intel):
        tmp = intel.split(",")
        for (i, key) in enumerate(format):
            value = tmp[i]
            if key == "pair":
                self.pair = value
            if key == "date":
                self.date = int(value)
            if key == "high":
                self.high = float(value)
            if key == "low":
                self.low = float(value)
            if key == "open":
                self.open = float(value)
            if key == "close":
                self.close = float(value)
            if key == "volume":
                self.volume = float(value)

    def __repr__(self):
        return str(self.pair) + str(self.date) + str(self.close) + str(self.volume)


class Chart:
    def __init__(self):
        self.dates = []
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.volumes = []
        self.indicators = {}

    def add_candle(self, candle: Candle):
        self.dates.append(candle.date)
        self.opens.append(candle.open)
        self.highs.append(candle.high)
        self.lows.append(candle.low)
        self.closes.append(candle.close)
        self.volumes.append(candle.volume)


class BotState:
    def __init__(self):
        self.timeBank = 0
        self.maxTimeBank = 0
        self.timePerMove = 1
        self.candleInterval = 1
        self.candleFormat = []
        self.candlesTotal = 0
        self.candlesGiven = 0
        self.initialStack = 0
        self.transactionFee = 0.1
        self.date = 0
        self.stacks = dict()
        self.charts = dict()

    def update_chart(self, pair: str, new_candle_str: str):
        if not (pair in self.charts):
            self.charts[pair] = Chart()
        new_candle_obj = Candle(self.candleFormat, new_candle_str)
        self.charts[pair].add_candle(new_candle_obj)

    def update_stack(self, key: str, value: float):
        self.stacks[key] = value

    def update_settings(self, key: str, value: str):
        if key == "timebank":
            self.maxTimeBank = int(value)
            self.timeBank = int(value)
        if key == "time_per_move":
            self.timePerMove = int(value)
        if key == "candle_interval":
            self.candleInterval = int(value)
        if key == "candle_format":
            self.candleFormat = value.split(",")
        if key == "candles_total":
            self.candlesTotal = int(value)
        if key == "candles_given":
            self.candlesGiven = int(value)
        if key == "initial_stack":
            self.initialStack = int(value)
        if key == "transaction_fee_percent":
            self.transactionFee = float(value)

    def update_game(self, key: str, value: str):
        if key == "next_candles":
            new_candles = value.split(";")
            self.date = int(new_candles[0].split(",")[1])
            for candle_str in new_candles:
                candle_infos = candle_str.strip().split(",")
                self.update_chart(candle_infos[0], candle_str)
        if key == "stacks":
            new_stacks = value.split(",")
            for stack_str in new_stacks:
                stack_infos = stack_str.strip().split(":")
                self.update_stack(stack_infos[0], float(stack_infos[1]))


if __name__ == "__main__":
    mybot = Bot()
    mybot.run()
