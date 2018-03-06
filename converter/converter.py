import os
import json
import ConfigParser
import numpy as np
from .registry import *

__all__ = [
    'pybar_yarr_mapping',
    'converter'
]

pybar_yarr_mapping = [
    ('Chip_ID', 'chipId'),
    ('CMDcnt', 'TOBEDETERMINED'),
    ('Chip_SN', 'EFUSE'),
    ('Clk2OutCnfg', 'Clk2Out'),
    ('DIGHITIN_SEL', 'DigHitIn_Sel'),
    ('DINJ_OVERRIDE', 'DJO'),
    ('DisableColumnCnfg', 'TOBEDETERMINED'),
    ('EN_160M', 'EN_160'),
    ('EN_320M', 'EN_320'),
    ('EN_PLL', 'PLL_Enable'),
    ('ErrorMask', 'TOBEDETERMINED'),
    ('FdacVbn', 'FDACVbn'),
    ('GADCStart', 'GADC_En'),
    ('GateHitOr', 'HitOr'),
    ('HITLD_IN', 'HitLD'),
    ('Latch_En', 'Latch_Enable'),
    ('LvdsDrvEn', 'LVDSDrvEn'),
    ('MonleakRange', 'IleakRange'),
    ('Pixel_Strobes', 'Pixel_latch_strobe'),
    ('PlsrDacBias', 'PlsrDACbias'),
    ('PlsrIdacRamp', 'PlsrIDACRamp'),
    ('PrmpVbnLcc', 'PrmpVbnLCC'),
    ('SELB' , 'TOBEDETERMINED'),
    ('SR_Clr', 'SRClr'),
    ('SR_Read', 'SRRead'),
    ('SmallHitErase', 'SME'),
    ('StopModeCnfg', 'StopModeConfig'),
    ('TdacVbp', 'TDACVbp'),
    ('TempSensDiodeBiasSel', 'TmpSensDiodeSel'),
    ('Vthin_AltCoarse', 'Vthin_Coarse'),
    ('Vthin_AltFine', 'Vthin_Fine'),
    ('C_Inj_Low', 'sCap'),
    ('C_Inj_Med', 'lCap'),
    ('C_Inj_High', 'TOBEDETERMINED'),
    ('Vcal_Coeff_0', 'vcalOffset'),
]

complex_conversion = [
    m[0] for m in pybar_yarr_mapping if m[1] == 'TOBEDETERMINED'
]

class converter(object):
    """
    pybar / json converter for the ATLAS ITk 
    demonstrator
    """

    def __init__(self):
        """
        """
        self._keys = []
      #  self._json_filename
        self._pybar_keys = []
        self._json_keys  = []
        self._json_dict = {}
        self._pybar_dict = {}
        self._dict_pybar_to_json_complex = {}

    def read_from_json(self, path):
        with open(path, 'r') as f:
            datastore = json.load(f)
            for k in datastore.keys():
                if isinstance(datastore[k], (list, dict)):
                    print k, type(datastore[k])
                else:
                    print k,type(datastore[k]), datastore[k]
                    self._json_keys.append(str(k))
                    self._json_dict[str(k)] = datastore[k]
                for kk in datastore[k].keys():
                    if isinstance(datastore[k][kk], (list, dict)):
                        print '\t', kk, type(datastore[k][kk])
                    else:
                        print '\t', kk, type(datastore[k][kk]), datastore[k][kk]
                        self._json_keys.append(str(kk))
                        self._json_dict[str(kk)] = datastore[k][kk]

                    if isinstance(datastore[k][kk], dict):
                        for kkk in datastore[k][kk].keys():
                            if isinstance(datastore[k][kk][kkk], list):
                                print '\t\t', kkk, type(datastore[k][kk][kkk])
                            else:
                                print '\t\t', kkk, type(datastore[k][kk][kkk]), datastore[k][kk][kkk]
                                self._json_keys.append(str(kkk))
                                self._json_dict[str(kkk)] = datastore[k][kk][kkk]
            return datastore



    def dump_to_json(self, output='tmp.json'):
        
        template_filename = os.path.join(os.path.dirname(__file__), '../dat/fei4.json')
        with open(template_filename, 'r') as ftemplate:
            template_json = json.load(ftemplate)

            # hardcode new json structure
            new_json = {}
            new_json['FE-I4B'] = {
                'name': 'blurp',
                'PixelConfig': [],
                'txChannel': int(0),
                'rxChannel': int(0),
                'GlobalConfig': {},
                'Parameter': {}}


            for block in ('GlobalConfig', 'Parameter'):
                for k, val in template_json['FE-I4B'][block].iteritems():
                    arg_type = type(val)
                    # argument exist in both yarr and pybar
                    if k in common_arguments():
                        new_json['FE-I4B'][block][k] = arg_type(self._pybar_dict[k])
                    # argument needs to be computed from pybar arguments
                    if k in json_complex_conversion():
                        new_json['FE-I4B'][block][k] = self._dict_pybar_to_json_complex[k]
                    # argument exist in both yarr and pybar with different name
                    for p, y in pybar_yarr_matched_args():
                        if k == y:
                            new_json['FE-I4B'][block][k] = arg_type(self._pybar_dict[p])


            new_json = json.dumps(new_json, sort_keys=True, indent=4, separators=(',', ': '))
            out_json = open(output, 'wb')
            out_json.write(new_json)


    def read_from_pybar(
        self, config, fdac, tdac, masks):
        with open(config, 'r') as config_file:
            for l in config_file.readlines():
                stripped_line = l.strip().split(' ')
                if stripped_line[0] in ('', '#'):
                    continue
                print stripped_line
                self._pybar_keys.append(stripped_line[0])
                self._pybar_dict[stripped_line[0]] = stripped_line[1]
        pass


    def pybar_to_json_complex_conversion(self):
        
        pybar_val = self._pybar_dict['CMDcnt']
        self._dict_pybar_to_json_complex['CalPulseWidth'] = 0
        self._dict_pybar_to_json_complex['CalPulseDelay'] = 0

        pybar_val = self._pybar_dict['DisableColumnCnfg']
        self._dict_pybar_to_json_complex['DisableColCnfg0'] = 0
        self._dict_pybar_to_json_complex['DisableColCnfg1'] = 0
        self._dict_pybar_to_json_complex['DisableColCnfg2'] = 0

        pybar_val = self._pybar_dict['ErrorMask']
        self._dict_pybar_to_json_complex['ErrorMask_0'] = 0
        self._dict_pybar_to_json_complex['ErrorMask_1'] = 0

        pybar_val = self._pybar_dict['SELB']
        self._dict_pybar_to_json_complex['SELB0'] = 0
        self._dict_pybar_to_json_complex['SELB1'] = 0
        self._dict_pybar_to_json_complex['SELB2'] = 0
        

    def json_to_pybar_complex_conversion(self):
        for key in complex_conversion:
            if key == 'CMDcnt':
                a = np.binary_repr(self._json_dict['CalPulseWidth'], width=16)
                b = np.binary_repr(self._json_dict['CalPulseDelay'], width=16)
                c = a[7:0:-1] + b[13:8:-1]
                self._json_keys.append(key)
                self._json_dict[key] = int(c, 2)
            if key == 'DisableColumnCnfg':
                self._json_keys.append(key)
                self._json_dict[key] = self._json_dict['DisableColCnfg0'] + self._json_dict['DisableColCnfg1'] + self._json_dict['DisableColCnfg2']
            if key == 'ErrorMask':
                self._json_keys.append(key)
                self._json_dict[key] = self._json_dict['ErrorMask_0'] + self._json_dict['ErrorMask_1']
            if key == 'SELB':
                self._json_keys.append(key)
                self._json_dict[key] =  self._json_dict['SELB0'] + self._json_dict['SELB1'] + self._json_dict['SELB2']
            if key == 'C_Inj_High':
                self._json_keys.append(key)
                self._json_dict[key] = self._json_dict['sCap'] + self._json_dict['lCap']

    def dump_to_pybar(self):
        pass

    @property
    def pybar_keys(self):
        return self._pybar_keys

    @property
    def json_keys(self):
        return self._json_keys
