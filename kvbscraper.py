#!/usr/bin/env python
# encoding: utf-8

"""
Scraper for KVB public transport data (cologne)
"""

import scrapemark
import urllib
import re


class KVBScraper(object):
    """
    Interface to some direct information from
    the kvb-koeln.de or vrs-info.de website
    """

    def get_station_realtime_data(self, station_id):
        """
        Reads info from QR code pages like
        http://www.kvb-koeln.de/qr/185
        and returns structured, normalized data.
        Strings are unicode. Returns tuple:
        (station_name, vehicles)
        """
        urlschema = 'http://www.kvb-koeln.de/qr/%d'
        url = urlschema % station_id
        request = urllib.urlopen(url)
        html = request.read()
        # pre-process
        #html = html.decode('latin-1')
        html = html.decode('iso-8859-1')
        #html = html.replace('ü', '&uuml;')
        # get output
        table = scrapemark.scrape("""
            <div class="qr_top_head_rot_small">{{ name }}<span></span></div>
            <table class="qr_table">
            {*
                <tr>
                    <td>&nbsp;{{ [vehicles].line }}&nbsp;</td>
                    <td>{{ [vehicles].destination }}</td>
                    <td>{{ [vehicles].time }}</td>
                </tr>
            *}
            </table>
            """, html=html)
        # process output
        if len(table['vehicles']) > 0:
            for vehicle in table['vehicles']:
                # process line value
                match_line_int = re.match(r'[0-9]', vehicle['line'])
                if match_line_int is not None:
                    vehicle['line'] = int(vehicle['line'])
                elif vehicle['line'] == '':
                    vehicle['line'] = None
                else:
                    raise ValueError('Bad line value ' + vehicle['line'])
                # process time value
                # get rid of &nbsp; remainders
                vehicle['time'] = vehicle['time'].replace(u'\xa0', u' ')
                time_parts = vehicle['time'].split()
                if len(time_parts) == 2:
                    if time_parts[1] == 'Min':
                        vehicle['time'] = int(time_parts[0]) * 60
                    else:
                        raise ValueError('Bad time value: ' + time_parts[1])
                elif len(time_parts) == 1:
                    if time_parts[0] == 'Sofort':
                        vehicle['time'] = 0
                    else:
                        raise ValueError('Bad time value: ' + time_parts[0])
                else:
                    raise ValueError('Bad number of time elements')
                # proess destination
                if vehicle['destination'].lower() == 'nicht einsteigen':
                    vehicle['destination'] = None
                elif vehicle['destination'].lower() == 'bitte nicht einsteigen':
                    vehicle['destination'] = None
                elif vehicle['destination'].lower() == 'leer':
                    vehicle['destination'] = None
                elif vehicle['destination'].lower() == 'fahrt endet hier':
                    vehicle['destination'] = table['name']
                elif vehicle['destination'].lower() == 'zug endet hier':
                    vehicle['destination'] = table['name']
            return (table['name'], table['vehicles'])
        elif table['name'] != '':
            # Station exists, but has no vehicle data
            return (table['name'], None)
        else:
            # Station doesn't exist
            return (None, None)


