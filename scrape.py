#!/usr/bin/env python
# encoding: utf-8

"""
Scraper for KVB public transport data (cologne)
to store data into database
"""

import sys
import time
import MySQLdb
from kvbscraper import KVBScraper


class DataStore(object):
    """
    Writes some scraped data to a mysql database
    """
    def __init__(self, db, host='localhost', user='root', password=''):
        try:
            self.conn = MySQLdb.connect(host=host, user=user, passwd=password, db=db)
            self.cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
        except MySQLdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])
            sys.exit(1)

    def store_realtime_results(self, station_id, station_name, vehicles):
        """
        Stores stuff received from
        KVBScraper.get_station_realtime_data()
        """
        if vehicles is not None:
            # stations
            self.cursor.execute(
                """
                INSERT IGNORE INTO stations (id, name, has_realtime_data) VALUES (%s, %s, %s)
                """, (station_id, station_name, 1))
            for v in vehicles:
                if v['line'] is not None:
                    # lines
                    self.cursor.execute(
                        'INSERT IGNORE INTO `lines` (id) VALUES (' + str(v['line']) + ')')
                    # destinations
                    if v['destination'] is not None:
                        self.cursor.execute(
                            """
                            INSERT IGNORE INTO destinations (line, name) VALUES (%s, %s)
                            """, (v['line'], v['destination']))
                    # stations2lines
                    self.cursor.execute(
                        """
                        INSERT IGNORE INTO stations2lines (station, line) VALUES (%s, %s)
                        """, (station_id, v['line']))
        else:
            self.cursor.execute(
                """
                INSERT IGNORE INTO stations (id, name, has_realtime_data) VALUES (%s, %s, %s)
                """, (station_id, station_name, 0))


if __name__ == '__main__':
    scraper = KVBScraper()
    db = DataStore(db='kvb')
    #scraper.get_station_realtime_data(41)
    #sys.exit()
    station_ids = range(1, 920)
    #random_sample = random.sample(station_ids, 10)
    for station_id in station_ids:
        print "station_id:", station_id
        station_name, vehicles = scraper.get_station_realtime_data(station_id)
        db.store_realtime_results(station_id, station_name, vehicles)
        time.sleep(0.5)
