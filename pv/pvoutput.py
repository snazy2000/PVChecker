# Copyright (c) 2010-2011 Edmund Tse
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from http.client import HTTPConnection
from urllib.parse import urlencode

import pv

DefaultHost = 'pvoutput.org'

class Connection():
	def __init__(self, api_key, system_id, host = DefaultHost):
		self.host = host
		self.api_key = api_key
		self.system_id = system_id

	def add_output(self, date, generated, exported=None, peak_power=None, peak_time=None, condition=None,
			min_temp=None, max_temp=None, comments=None, import_peak=None, import_offpeak=None, import_shoulder=None):
		"""
		Uploads end of day output information
		"""
		path = '/service/r2/addoutput.jsp'
		params = {
				'd': date,
				'g': generated
				}
		if exported:
			params['e'] = exported
		if peak_power:
			params['pp'] = peak_power
		if peak_time:
			params['pt'] = peak_time
		if condition:
			params['cd'] = condition
		if min_temp:
			params['tm'] = min_temp
		if max_temp:
			params['tx'] = max_temp
		if comments:
			params['cm'] = comments
		if import_peak:
			params['ip'] = import_peak
		if import_offpeak:
			params['op'] = import_offpeak
		if import_shoulder:
			params['is'] = import_shoulder

		response = self.make_request('POST', path, params)

		if response.status == 400:
			raise ValueError(response.read().decode('utf-8', errors='replace'))
		if response.status != 200:
			raise RuntimeError(response.read().decode('utf-8', errors='replace'))

	def add_status(self, date, time, energy_exp, power_exp=None, energy_imp=None, power_imp=None, cumulative=False, temp=None):
		"""
		Uploads live output data
		"""
		path = '/service/r2/addstatus.jsp'
		params = {
				'd': date,
				't': time,
				'v1': energy_exp
				}
		if power_exp:
			params['v2'] = power_exp
		if energy_imp:
			params['v3'] = energy_imp
		if power_imp:
			params['v4'] = power_imp
		if cumulative:
			params['c1'] = 1
                
		params = urlencode(params)

		print(params)

		response = self.make_request('POST', path, params)

		if response.status == 400:
			raise ValueError(response.read().decode('utf-8', errors='replace'))
		if response.status != 200:
			raise RuntimeError(response.read().decode('utf-8', errors='replace'))

	def get_status(self, date=None, time=None):
		"""
		Retrieves status information
		"""
		path = '/service/r2/getstatus.jsp'
		params = {}
		if date:
			params['d'] = date
		if time:
			params['t'] = time
		params = urlencode(params)

		response = self.make_request("GET", path, params)

		if response.status == 400:
			raise ValueError(response.read().decode('utf-8', errors='replace'))
		if response.status != 200:
			raise RuntimeError(response.read().decode('utf-8', errors='replace'))

		return response.read().decode('utf-8', errors='replace')

	def delete_status(self, date, time):
		"""
		Removes an existing status
		"""
		path = '/service/r1/deletestatus.jsp'
		params = {
				'd': date,
				't': time
				}
		params = urlencode(params)

		response = self.make_request("POST", path, params)

		if response.status == 400:
			raise ValueError(response.read().decode('utf-8', errors='replace'))
		if response.status != 200:
			raise RuntimeError(response.read().decode('utf-8', errors='replace'))

		return response.read().decode('utf-8', errors='replace')

	def make_request(self, method, path, params=None):
		conn = HTTPConnection(self.host)
		if isinstance(params, dict):
			params = urlencode(params)
		headers = {
				'Content-type': 'application/x-www-form-urlencoded',
				'Accept': 'text/plain',
				'X-Pvoutput-Apikey': self.api_key,
				'X-Pvoutput-SystemId': str(self.system_id)
				}
		conn.request(method, path, params, headers)

		return conn.getresponse()
