from converter import converter
import json
from tabulate import tabulate
import os
from argparse import ArgumentParser


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('out', default='json', choices=['json', 'pybar'])
    parser.add_argument('--json-input-file', default='tmp.json')
    parser.add_argument('--pybar-input-dir', default='/Users/quentin/Dropbox/JP2_1_ExampleConfig/')
    parser.add_argument('--name', default='434_JP2')
    parser.add_argument('--feb', type=int, default=1)
    parser.add_argument('--scan', default='threshold', choices=['init', 'threshold'])

    args = parser.parse_args()

    pybar_folder = args.pybar_input_dir
    module_name = args.name
    feb = args.feb
    scan_type = args.scan

    if args.out == 'json':
        c1 = converter(yarr_to_pybar=True)
        c1.read_from_pybar(
            os.path.join(pybar_folder, 'configs', '{name}_{feb}_{scan}_scan.cfg'.format(name=module_name, feb=feb, scan=scan_type)),
            os.path.join(pybar_folder, 'fdacs', 'fdac_{name}_{feb}_{scan}_scan.dat'.format(name=module_name, feb=feb, scan=scan_type)),
            os.path.join(pybar_folder, 'tdacs', 'tdac_{name}_{feb}_{scan}_scan.dat'.format(name=module_name, feb=feb, scan=scan_type)),
            [
                os.path.join(pybar_folder, 'masks', 'c_high_{name}_{feb}_{scan}_scan.dat'.format(name=module_name, feb=feb, scan=scan_type)),
                os.path.join(pybar_folder, 'masks', 'c_low_{name}_{feb}_{scan}_scan.dat'.format(name=module_name, feb=feb, scan=scan_type)),
                os.path.join(pybar_folder, 'masks', 'enable_{name}_{feb}_{scan}_scan.dat'.format(name=module_name, feb=feb, scan=scan_type)),
                os.path.join(pybar_folder, 'masks', 'imon_{name}_{feb}_{scan}_scan.dat'.format(name=module_name, feb=feb, scan=scan_type)),])
        
        c1.pybar_to_json_complex_conversion()
        c1.dump_to_json()

    else:
        c2 = converter(yarr_to_pybar=False, run_number=feb, fe_name=module_name, scan_type=scan_type)
        # tmp.json
        c2.read_from_json('tmp.json')
        c2.dump_to_pybar()
