from cosmogrb.lightcurve import LightCurveAnalyzer




class GBMLightCurveAnalyzer(LightCurveAnalyzer):
    """Documentation for GBMLightCurveAnalyzer

    """
    def __init__(self, lightcurve):
        super(GBMLightCurveAnalyzer, self).__init__()
        self.lightcurve = lightcurve
        
        
