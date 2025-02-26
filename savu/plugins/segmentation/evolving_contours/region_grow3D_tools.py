from savu.plugins.plugin_tools import PluginTools

class RegionGrow3dTools(PluginTools):
    """Fast 3D segmentation by evolving the user-given mask, the initialised
mask should be set in the central part of the object to be segmented.
    """

    def define_parameters(self):
        """
        threshold:
            visibility: basic
            dtype: float
            description: parameter to control mask propagation.
            default: 1.0

        method:
            visibility: intermediate
            dtype: str
            description: a method to collect statistics from the
              given mask (mean, median, value).
            default: mean

        iterations:
            visibility: basic
            dtype: int
            description: number of iterations.
            default: 500

        connectivity:
            visibility: intermediate
            dtype: int
            description: the connectivity of the local neighbourhood,
              choose 4, 6, 8 or 26.
            default: 6
            options: [4, 6, 8, 26]

        out_datasets:
            visibility: datasets
            dtype: [list[],list[str]]
            description: The default names
            default: ['MASK_RG_EVOLVED']

        """
