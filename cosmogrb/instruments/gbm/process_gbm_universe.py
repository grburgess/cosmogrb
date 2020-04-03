from cosmogrb.instruments.gbm.gbm_trigger import GBMTrigger


def process_gbm_universe(*grb_save_files, client=None, threshold=4.5, serial=False):

    if not serial:

        assert client is not None, "One must provide a client to process in parallel"
    
    args = []
    for grb_file in grb_save_files:

        args.append([grb_file, threshold])
    
    futures = client.map(_submit, args)
    

def _submit(args):

    grb_file, threshold = args
    
    gbm_trigger = GBMTrigger(grb_save_file_name=grb_file, threshold=threshold)
    gbm_trigger.save()

    
