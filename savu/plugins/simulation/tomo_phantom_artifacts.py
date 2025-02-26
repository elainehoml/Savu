# Copyright 2014 Diamond Light Source Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
.. module:: tomo_phantom_artifacts
   :platform: Unix
   :synopsis: Adding artifacts to real or generated synthetic projection data using TomoPhantom

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

import savu.plugins.utils as pu
from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

from tomophantom.supp.artifacts import _Artifacts_
import numpy as np

@register_plugin
class TomoPhantomArtifacts(Plugin, CpuPlugin):
    def __init__(self):
        super(TomoPhantomArtifacts, self).__init__('TomoPhantomArtifacts')

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        out_dataset[0].create_dataset(in_dataset[0])
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup(self.parameters['pattern'], self.get_max_frames())
        out_pData[0].plugin_data_setup(self.parameters['pattern'], self.get_max_frames())

    def process_frames(self, data):
        proj_data = data[0]

        if self.parameters['pattern'] == 'PROJECTION':
            proj_data = np.expand_dims(proj_data, axis=1)

        # apply a variety of artifacts to the generated data:
        _noise_ = {}
        if self.parameters['artifacts_noise_type'] is not None:
            _noise_ = {'noise_type': self.parameters['artifacts_noise_type'],
                       'noise_amplitude': self.parameters['artifacts_noise_amplitude'],
                       'noise_seed': 0,
                       'verbose': False}

        # misalignment dictionary
        _datashifts_ = {}
        if self.parameters['datashifts_maxamplitude_pixel'] is not None:
            _datashifts_ = {'datashifts_maxamplitude_pixel': self.parameters['datashifts_maxamplitude_pixel']}
        if self.parameters['datashifts_maxamplitude_subpixel'] is not None:
            _datashifts_ = {'datashifts_maxamplitude_subpixel': self.parameters['datashifts_maxamplitude_subpixel']}

        # adding zingers
        _zingers_ = {}
        if self.parameters['artifacts_zingers_percentage'] is not None:
            _zingers_ = {'zingers_percentage': self.parameters['artifacts_zingers_percentage'],
                         'zingers_modulus': self.parameters['artifacts_zingers_modulus']}
        _stripes_ = {}

        # adding stripes
        if self.parameters['pattern'] == 'SINOGRAM':
            if self.parameters['artifacts_stripes_percentage'] is not None:
                _stripes_ = {'stripes_percentage': self.parameters['artifacts_stripes_percentage'],
                             'stripes_maxthickness': self.parameters['artifacts_stripes_maxthickness'],
                             'stripes_intensity': self.parameters['artifacts_stripes_intensity'],
                             'stripes_type': self.parameters['artifacts_stripes_type'],
                             'stripes_variability': self.parameters['artifacts_stripes_variability']}

        # partial volume effect dictionary
        _pve_ = {}
        if self.parameters['artifacts_pve'] is not None:
            _pve_ = {'pve_strength': self.parameters['artifacts_pve']}

        # fresnel propagator
        _fresnel_propagator_ = {}
        if self.parameters['artifacts_fresnel_distance'] is not None:
            _fresnel_propagator_ = {'fresnel_dist_observation': self.parameters['artifacts_fresnel_distance'],
                                    'fresnel_scale_factor': self.parameters['artifacts_fresnel_scale_factor'],
                                    'fresnel_wavelenght': self.parameters['artifacts_fresnel_wavelenght']}

        if (self.parameters['datashifts_maxamplitude_pixel']) or (self.parameters['datashifts_maxamplitude_subpixel']) is not None:
            [data_artifacts, shifts] = _Artifacts_(proj_data.copy(), **_noise_, **_zingers_, **_stripes_, **_datashifts_, **_pve_, **_fresnel_propagator_)
        else:
            data_artifacts = _Artifacts_(proj_data.copy(), **_noise_, **_zingers_, **_stripes_, **_datashifts_, **_pve_, **_fresnel_propagator_)

        if self.parameters['pattern'] == 'PROJECTION':
            data_artifacts = data_artifacts[:, 0, :]

        return data_artifacts

    def get_max_frames(self):
        return 'single'

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 1
