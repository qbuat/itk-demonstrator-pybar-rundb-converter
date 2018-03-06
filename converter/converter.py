import json
import ConfigParser

__all__ = [
    'pybar_yarr_mapping',
    'converter'
]

pybar_yarr_mapping = [
    ('Chip_ID', 'chipId'),
    ('CMDcnt', 'CalPulseWidth'),
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

    def dump_to_json(self, path):
        pass

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
        for key in complex_conversion:
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
