Tomopy Recon
########################################################

Description
--------------------------

A wrapper to the tomopy reconstruction library. 

Parameters
--------------------------

.. code-block:: yaml

        in_datasets:
            visibility: datasets
            dtype: "[list[],list[str]]"
            description: 
                summary: A list of the dataset(s) to process.
                verbose: A list of strings, where each string gives the name of a dataset that was either specified by a loader plugin or created as output to a previous plugin.  The length of the list is the number of input datasets requested by the plugin.  If there is only one dataset and the list is left empty it will default to that dataset.
            default: "[]"
        
        out_datasets:
            visibility: datasets
            dtype: "[list[],list[str]]"
            description: 
                summary: A list of the dataset(s) to create.
                verbose: A list of strings, where each string is a name to be assigned to a dataset output by the plugin. If there is only one input dataset and one output dataset and the list is left empty, the output will take the name of the input dataset. The length of the list is the number of output datasets created by the plugin.
            default: "[]"
        
        centre_of_rotation:
            visibility: basic
            dtype: "[float, str, dict{int:float}]"
            description: Centre of rotation to use for the reconstruction.
            default: "0.0"
            example: It could be a fixed value, a dictionary of (sinogram number, value) pairs for a polynomial fit of degree 1, or a dataset name.
        
        init_vol:
            visibility: hidden
            dtype: "[None,int]"
            description: Not an option.
            default: None
            example: "Type the name of the initialised dataset e.g. ['tomo']"
        
        log:
            visibility: intermediate
            dtype: bool
            description: 
                summary: Option to take the log of the data before reconstruction.
                verbose: Should be set to false if you use PaganinFilter
            default: "True"
            example: Set to True to take the log of the data before reconstruction.
        
        preview:
            visibility: intermediate
            dtype: preview
            description: A slice list of required frames.
            default: "[]"
        
        force_zero:
            visibility: intermediate
            dtype: "[list[float,float],list[None,None]]"
            description: Set any values in the reconstructed image outside of this range to zero.
            default: "['None', 'None']"
            example: "[0, 1]"
        
        ratio:
            visibility: intermediate
            dtype: "[float, list[float, float]]"
            description: Ratio of the masks diameter in pixels to the smallest edge size along given axis. If a list of two floats is given, the second value is used to fill up the area outside the mask.
            default: "0.95"
        
        log_func:
            visibility: advanced
            dtype: str
            description: Override the default log function with a numpy statement
            default: np.nan_to_num(-np.log(sino))
        
        vol_shape:
            visibility: intermediate
            dtype: "[str, int]"
            description: 
                summary: Override the size of the reconstruction volume with an integer value.
                verbose: When fixed, you get the dimension of the horizontal detector or you can specify any reconstruction size you like with an integer.
            default: fixed
        
        algorithm:
            visibility: basic
            dtype: str
            description: The reconstruction algorithm
            default: gridrec
            options: "['art', 'bart', 'fbp', 'gridrec', 'mlem', 'osem', 'ospml_hybrid', 'ospml_quat', 'pml_hybrid', 'pml_quad', 'sirt']"
        
        filter_name:
            visibility: intermediate
            dtype: "[None, str]"
            description: Name of the filter for analytic reconstruction
            default: ramlak
            options: "['None', 'shepp', 'cosine', 'hann', 'hamming', 'ramlak', 'parzen', 'butterworth']"
            dependency: 
                algorithm: 
                    fbp
                    gridrec
        
        reg_par:
            visibility: intermediate
            dtype: float
            description: Regularization parameter for smoothing
            default: "0.0"
            dependency: 
                algorithm: 
                    ospml_hybrid
                    ospml_quad
                    pml_hybrid
                    pml_quad
        
        n_iterations:
            visibility: basic
            dtype: int
            description: Number of iterations.
            default: "1"
            dependency: 
                algorithm: 
                    art
                    bart
                    mlem
                    osem
                    ospml_hybrid
                    ospml_quad
                    pml_hybrid
                    pml_quad
                    sirt
        
        outer_pad:
            visibility: intermediate
            dtype: "[bool, float]"
            description: Pad the sinogram width to fill the reconstructed volume for asthetic purposes. Choose from True (defaults to sqrt(2)), False or float <= 2.1.
            warning: This will increase the size of the data and the time to compute the reconstruction. Only available for selected algorithms and will be ignored otherwise.
            default: "False"
            dependency: 
                algorithm: 
                    fbp
                    gridrec
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml

Citations
--------------------------

TomoPy: a framework for the analysis of synchrotron tomographic data by Gürsoy, Doga et al.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Bibtex
""""""""""""""""""""""""""""""""""""""""""

.. code-block:: none

    @article{gursoy2014tomopy,
    title={TomoPy: a framework for the analysis of synchrotron tomographic data},
    author={Gürsoy, Doga and De Carlo, Francesco and Xiao, Xianghui and Jacobsen, Chris},
    journal={Journal of synchrotron radiation},
    volume={21},
    number={5},
    pages={1188--1193},
    year={2014},
    publisher={International Union of Crystallography}
    }
    

Endnote
""""""""""""""""""""""""""""""""""""""""""

.. code-block:: none

    %0 Journal Article
    %T TomoPy: a framework for the analysis of synchrotron tomographic data
    %A Gürsoy, Doga
    %A De Carlo, Francesco
    %A Xiao, Xianghui
    %A Jacobsen, Chris
    %J Journal of synchrotron radiation
    %V 21
    %N 5
    %P 1188-1193
    %@ 1600-5775
    %D 2014
    %I International Union of Crystallography
    

