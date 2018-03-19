from converter import converter
import json
from tabulate import tabulate

from argparse import ArgumentParser


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('out', default='json', choices=['json', 'pybar'])
    args = parser.parse_args()

    if args.out == 'json':
        c1 = converter(yarr_to_pybar=True)
        c1.read_from_pybar(
            './dat/module_0/configs/1_module_0_init_scan.cfg',
            './dat/module_0/fdacs/fdac_1_module_0_init_scan.dat',
            './dat/module_0/tdacs/tdac_1_module_0_init_scan.dat',
            [
                './dat/module_0/masks/c_high_1_module_0_init_scan.dat',
                './dat/module_0/masks/c_low_1_module_0_init_scan.dat',
                './dat/module_0/masks/enable_1_module_0_init_scan.dat',
                './dat/module_0/masks/imon_1_module_0_init_scan.dat',])
        
        c1.pybar_to_json_complex_conversion()
        c1.dump_to_json()

    else:
        c2 = converter(yarr_to_pybar=False)
        c2.read_from_json('dat/fei4.json')
        c2.dump_to_pybar()
