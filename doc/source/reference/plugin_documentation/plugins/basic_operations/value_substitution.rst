Value Substitution
########################################################

Description
--------------------------

The function looks for a specific value in the provided second dataset (e.g. a mask image) and substitutes it with a given value. 

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
        
        seek_value:
            visibility: basic
            dtype: float
            description: The value to be located in the second dataset.
            default: "0.0"
        
        new_value:
            visibility: basic
            dtype: float
            description: The value to be replaced with in the first dataset.
            default: "1.0"
        
        pattern:
            visibility: advanced
            dtype: str
            options: "['SINOGRAM', 'PROJECTION', 'VOLUME_XZ', 'VOLUME_YZ']"
            description: Pattern to apply this to.
            default: VOLUME_XZ
        
Key
^^^^^^^^^^

.. literalinclude:: /../source/files_and_images/plugin_guides/short_parameter_key.yaml
    :language: yaml
