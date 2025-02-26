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
.. module:: forward_projector_cpu
   :platform: Unix
   :synopsis: A forward data projector using ToMoBAR software

.. moduleauthor:: Daniil Kazantsev <scientificsoftware@diamond.ac.uk>
"""

from savu.plugins.plugin import Plugin
from savu.plugins.driver.cpu_plugin import CpuPlugin
from savu.plugins.utils import register_plugin

from tomobar.methodsDIR import RecToolsDIR
import numpy as np

@register_plugin
class ForwardProjectorCpu(Plugin, CpuPlugin):
    def __init__(self):
        super(ForwardProjectorCpu, self).__init__('ForwardProjectorCpu')

    def pre_process(self):
        # getting metadata
        in_meta_data = self.get_in_meta_data()[0]
        self.cor = in_meta_data.get('centre_of_rotation')
        self.cor = self.cor[0]

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()
        in_pData, out_pData = self.get_plugin_datasets()
        in_pData[0].plugin_data_setup('VOLUME_XZ', 'single')

        in_meta_data = self.get_in_meta_data()[0]
        # extracting parameters from metadata
        angles_meta_deg = in_meta_data.get('rotation_angle')
        self.angles_rad = np.deg2rad(angles_meta_deg)
        self.detectors_horiz = in_meta_data.get('detector_x_length')

        # get experimental metadata of projection_shifts
        if 'projection_shifts' in list(self.exp.meta_data.dict.keys()):
            self.projection_shifts = self.exp.meta_data.dict['projection_shifts']

        # deal with user-defined parameters
        if (self.parameters['angles_deg'] is not None):
            angles_list = self.parameters['angles_deg']
            self.angles_rad = np.deg2rad(np.linspace(angles_list[0], angles_list[1], angles_list[2], dtype=np.float))
        if (self.parameters['centre_of_rotation'] is not None):
            self.cor = self.parameters['centre_of_rotation']
        if (self.parameters['det_horiz'] is not None):
            self.detectors_horiz = self.parameters['det_horiz']

        self.det_horiz_half = 0.5 * self.detectors_horiz
        self.angles_total = len(self.angles_rad)

        out_shape_sino = self.new_shape(in_dataset[0].get_shape(), in_dataset[0])
        labels = ['rotation_angle.degrees', 'detector_y.pixel', 'detector_x.pixel']
        pattern = {'name': 'SINOGRAM', 'slice_dims': (1,),
                   'core_dims': (2, 0)}
        out_dataset[0].create_dataset(axis_labels=labels, shape=out_shape_sino)
        out_dataset[0].add_pattern(pattern['name'],
                                   slice_dims=pattern['slice_dims'],
                                   core_dims=pattern['core_dims'])
        pattern2 = {'name': 'PROJECTION', 'slice_dims': (0,),
                    'core_dims': (1, 2)}
        out_dataset[0].add_pattern(pattern2['name'],
                                   slice_dims=pattern2['slice_dims'],
                                   core_dims=pattern2['core_dims'])
        out_pData[0].plugin_data_setup(pattern['name'], self.get_max_frames())
        out_dataset[0].meta_data.set('rotation_angle', angles_meta_deg)

    def process_frames(self, data):
        image = data[0].astype(np.float32)
        image = np.where(np.isfinite(image), image, 0)
        image_size = np.shape(image)[0]
        vert_size = None  # 2D case
        # dealing with 3D data case
        if image.ndim == 3:
            vert_size = np.shape(image)[1]
            self.angles_rad = -self.angles_rad
            cor = (-self.cor + self.det_horiz_half - 0.5) - self.projection_shifts
        else:
            cor = (-self.cor + self.det_horiz_half - 0.5)
        RectoolsDIR = RecToolsDIR(DetectorsDimH=self.detectors_horiz,  # DetectorsDimH # detector dimension (horizontal)
                                  DetectorsDimV=vert_size,  # DetectorsDimV # detector dimension (vertical)
                                  CenterRotOffset=cor,  # Center of Rotation
                                  AnglesVec=self.angles_rad,  # array of angles in radians
                                  ObjSize=image_size,  # a scalar to define reconstructed object dimensions
                                  device_projector='cpu')
        if vert_size is not None:
            sinogram_new = RectoolsDIR.FORWPROJ(np.swapaxes(image, 0, 1))
            sinogram_new = np.swapaxes(sinogram_new, 0, 1)
        else:
            sinogram_new = RectoolsDIR.FORWPROJ(image)
        return sinogram_new

    def new_shape(self, full_shape, data):
        # calculate a new output data shape based on the input data shape
        new_shape_sino_orig = list(full_shape)
        new_shape_sino = (self.angles_total, new_shape_sino_orig[1], self.detectors_horiz)
        return tuple(new_shape_sino)

    def get_max_frames(self):
        return 'multiple'

    def nInput_datasets(self):
        return 1

    def nOutput_datasets(self):
        return 1