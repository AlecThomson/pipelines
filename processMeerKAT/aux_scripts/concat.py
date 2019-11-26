#Copyright (C) 2019 Inter-University Institute for Data Intensive Astronomy
#See processMeerKAT.py for license details.

import os
import glob

import config_parser
from config_parser import validate_args as va
from cal_scripts import bookkeeping

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)-15s %(levelname)s: %(message)s", level=logging.INFO)

def sortbySPW(visname):
    return float(visname.split('~')[0])

def do_concat(visname, fields):

    basename = os.path.split(visname)[-1].replace('.ms','')
    msmd.open(visname)
    for target in fields.targetfield.split(','):
        fname = msmd.namesforfields(int(target))[0]

        #Concat images (into continuum cube)
        images = glob.glob('*/images/*{0}*image'.format(fname))
        if len(images) == 0:
            logger.warn("Didn't find any images with '*/images/*{0}*image'".format(fname))
        else:
            images.sort(key=sortbySPW)
            out = '{0}.{1}.cube'.format(basename,fname)
            if os.path.exists(out):
                logger.info('Output file "{0}" already exists. Skipping imageconcat.'.format(out))
            else:
                ia.imageconcat(infiles=images, outfile=out, axis=-1, relax=True)

        #Concat MSs
        MSs = glob.glob('*/*{0}*.ms'.format(fname))
        if len(MSs) == 0:
            logger.warn("Didn't find any MSs with '*/*{0}*.ms'".format(fname))
        else:
            MSs.sort(key=sortbySPW)
            out = '{0}.{1}.ms'.format(basename,fname)
            if os.path.exists(out):
                logger.info('Output file "{0}" already exists. Skipping concat.'.format(out))
            else:
                concat(vis=MSs, concatvis=out)

    msmd.done()

if __name__ == '__main__':
    # Get the name of the config file
    args = config_parser.parse_args()

    # Parse config file
    taskvals, config = config_parser.parse_config(args['config'])

    visname = va(taskvals, 'data', 'vis', str)
    spw = va(taskvals, 'crosscal', 'spw', str, default='')
    fields = bookkeeping.get_field_ids(taskvals['fields'])

    do_concat(visname, fields)