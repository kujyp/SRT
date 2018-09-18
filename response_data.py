import xml.etree.ElementTree as ET
import errors


class SRTResponseData():
    """SRT Response data class
    parse XML response from API request
    """

    NAMESPACE = '{http://www.nexacro.com/platform/dataset}'
    DATASETTAG = NAMESPACE + 'Dataset'
    DATATAG = NAMESPACE + 'Col'
    ROWTAG = NAMESPACE + 'Row'

    STATUS_OUTPUT_ID = 'dsOutput0'
    RESULT_OUTPUT_ID = 'dsCmcOutput0'
    DATA_OUTPUT_ID = 'dsOutput1'

    STATUS_SUCCESS = 'SUCC'
    STATUS_FAIL = 'FAIL'

    def __init__(self, response):
        self._xml = ET.fromstring(response)
        self._status = {}
        self._result = {}
        self._data = []

        # parse response data
        self._parse()

    def __str__(self):
        return self.dump()

    def dump(self):
        return ET.tostring(self._xml, encoding='unicode')

    def _parse(self):
        datasets = filter(lambda e: e.tag == self.DATASETTAG, list(self._xml))
        for dataset in datasets:
            tag_id = dataset.get('id')

            # status check
            if tag_id == self.STATUS_OUTPUT_ID:
                for row in dataset.iter(self.DATATAG):
                    self._status[row.get('id')] = row.text

            # result check
            elif tag_id == self.RESULT_OUTPUT_ID:
                for row in dataset.iter(self.DATATAG):
                    self._result[row.get('id')] = row.text

            # data check
            elif tag_id == self.DATA_OUTPUT_ID:
                for row in dataset.iter(self.ROWTAG):
                    self._data.append({})
                    for col in dataset.iter(self.DATATAG):
                        self._data[-1][col.get('id')] = col.text

    def success(self):
        result = self._status.get('strResult', None)
        if result is None:
            raise errors.SRTResponseError('Response status is not given')
        if result == self.STATUS_SUCCESS:
            return True
        elif result == self.STATUS_FAIL:
            return False
        else:
            raise errors.SRTResponseError('Undefined result status "{}"'.format(result))

    def message(self):
        if 'MSG' in self._result:
            return self._result['MSG']
        elif 'msgTxt' in self._status:
            return self._status['msgTxt']
        else:
            return ''

    # get parse result
    def get_data(self):
        return self._status.copy(), self._result.copy(), self._data.copy()