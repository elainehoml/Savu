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
.. module:: astra_recon_gpu
   :platform: Unix
   :synopsis: Wrapper around the Astra toolbox for gpu reconstruction using vector geometry
.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
import astra
import numpy as np

from savu.plugins.reconstructions.astra_recons.base_astra_vector_recon \
    import BaseAstraVectorRecon
from savu.plugins.driver.gpu_plugin import GpuPlugin
from savu.plugins.utils import register_plugin


@register_plugin
class AstraReconGpu(BaseAstraVectorRecon, GpuPlugin):

    def __init__(self):
        super(AstraReconGpu, self).__init__("AstraReconGpu")
        self.GPU_index = None
        self.res = False
        self.start = 0

    def set_options(self, cfg):
        if 'option' not in cfg.keys():
            cfg['option'] = {}
        cfg['option']['GPUindex'] = self.parameters['GPU_index']
        return cfg

    def nOutput_datasets(self):
        alg = self.parameters['algorithm']
        if self.parameters['res_norm'] is True and 'FBP' not in alg:
            self.res = True
            self.parameters['out_datasets'].append('res_norm')
            return 2
        return 1

    def astra_setup(self):
        options_list = ["FBP_CUDA", "SIRT_CUDA", "SART_CUDA", "CGLS_CUDA",
                        "FP_CUDA", "BP_CUDA", "SIRT3D_CUDA", "CGLS3D_CUDA"]
        if not options_list.count(self.parameters['algorithm']):
            raise Exception("Unknown Astra GPU algorithm.")

    def astra_2D_vector_recon(self, data):
        sino = data[0]
        cor, angles, vol_shape, init = self.get_frame_params()
        if self.res:
            res = np.zeros(self.len_res)
        # create volume geom
        vol_geom = astra.create_vol_geom(vol_shape)
        # create projection geom
        det_width = sino.shape[self.dim_detX]
        half_det_width = 0.5*det_width
        cor_astra_scalar = half_det_width - cor
        # set parallel beam vector geometry
        vectors = self.vec_geom_init2D(np.deg2rad(angles), 1.0, cor_astra_scalar-0.5)
        try:
            #vector geometry (astra > 1.9v)
            proj_geom = astra.create_proj_geom('parallel_vec', det_width, vectors)
        except:
            print('Warning: using scalar geometry since the Astra version <1.9 does not support the vector one for 2D')
            proj_geom = astra.create_proj_geom('parallel', 1.0, det_width, angles)
        sino = np.transpose(sino, (self.dim_rot, self.dim_detX))

        # Create a data object to hold the sinogram data
        sino_id = astra.data2d.create('-sino', proj_geom, sino)

        # create reconstruction id
        if init is not None:
            rec_id = astra.data2d.create('-vol', vol_geom, init)
        else:
            rec_id = astra.data2d.create('-vol', vol_geom)

#        if self.mask_id:
#            self.mask_id = astra.data2d.create('-vol', vol_geom, self.mask)
        # setup configuration options
        cfg = self.set_config(rec_id, sino_id, proj_geom, vol_geom)
        # create algorithm id
        alg_id = astra.algorithm.create(cfg)
        # run algorithm
        if self.res:
            for j in range(self.iters):
                # Run a single iteration
                astra.algorithm.run(alg_id, 1)
                res[j] = astra.algorithm.get_res_norm(alg_id)
        else:
            astra.algorithm.run(alg_id, self.iters)
        # get reconstruction matrix

        if self.manual_mask is not False:
            recon = self.manual_mask*astra.data2d.get(rec_id)
        else:
            recon = astra.data2d.get(rec_id)

        # delete geometry
        self.delete(alg_id, sino_id, rec_id, False)
        return [recon, res] if self.res else recon

    def astra_3D_vector_recon(self, data):
        proj_data3d = data[0] # get 3d block of projection data
        cor, angles, vol_shape, init = self.get_frame_params()
        projection_shifts2d = self.get_frame_shifts()   
        #print(projection_shifts2d)
        half_det_width = 0.5*proj_data3d.shape[self.sino_dim_detX]
        cor_astra_scalar = half_det_width - np.mean(cor)  # works with scalar CoR only atm

        recon = np.zeros(vol_shape)
        recon = np.expand_dims(recon, axis=self.slice_dir)
        if self.res:
            res = np.zeros((self.vol_shape[self.slice_dir], self.iters))

        # create volume geometry
        vol_geom = \
            astra.create_vol_geom(vol_shape[0], vol_shape[2], vol_shape[1])

        # define astra vector geometry for 3d case
        vectors3d = self.vec_geom_init3D(np.deg2rad(angles+90.0), 1.0, 1.0, cor_astra_scalar-0.5, projection_shifts2d)
        proj_geom = astra.create_proj_geom('parallel3d_vec',
                                           proj_data3d.shape[self.sino_dim_detY],
                                           proj_data3d.shape[self.sino_dim_detX],
                                           vectors3d)
        # create projection data id
        proj_id = astra.data3d.create("-sino", proj_geom, np.swapaxes(proj_data3d, 0, 1))

        # create reconstruction id
        if init is not None:
            rec_id = astra.data3d.create('-vol', vol_geom, init)
        else:
            rec_id = astra.data3d.create('-vol', vol_geom)

        # setup configuration options
        cfg = self.set_config(rec_id, proj_id, proj_geom, vol_geom)

        # create algorithm id
        alg_id = astra.algorithm.create(cfg)

        # run algorithm
        """
        if self.res:
            for j in range(self.iters):
                # Run a single iteration
                astra.algorithm.run(alg_id, 1)
                res[j] = astra.algorithm.get_res_norm(alg_id)
        else:
            astra.algorithm.run(alg_id, self.iters)
        """
        astra.algorithm.run(alg_id, self.iters)

        # get reconstruction matrix
        #if self.manual_mask:
        #    recon = self.mask*astra.data3d.get(rec_id)
        #else:
        #    recon = astra.data3d.get(rec_id)

        recon = np.transpose(astra.data3d.get(rec_id), (2, 0, 1))

        # delete geometry
        self.delete(alg_id, proj_id, rec_id, False)

        self.start += 1
        if self.res:
            return [recon, res]
        else:
            return recon

    def rotation_matrix2D(self, theta):
        #define 2D rotation matrix
        return np.array([[np.cos(theta), -np.sin(theta)],
                         [np.sin(theta), np.cos(theta)]])

    def rotation_matrix3D(self, theta):
        #define 3D rotation matrix
        return np.array([[np.cos(theta), -np.sin(theta), 0.0],
                         [np.sin(theta), np.cos(theta), 0.0],
                         [0.0 , 0.0 , 1.0]])

    def vec_geom_init2D(self, angles_rad, DetectorSpacingX, CenterRotOffset):
        #define 2D vector geometry
        s0 = [0.0, -1.0] # source
        d0 = [CenterRotOffset, 0.0] # detector
        u0 = [DetectorSpacingX, 0.0] # detector coordinates

        vectors = np.zeros([angles_rad.size, 6])
        for i in range(0, angles_rad.size):
            theta = angles_rad[i]
            vec_temp = np.dot(self.rotation_matrix2D(theta), s0)
            vectors[i, 0:2] = vec_temp[:] # ray position
            vec_temp = np.dot(self.rotation_matrix2D(theta), d0)
            vectors[i, 2:4] = vec_temp[:] # center of detector position
            vec_temp = np.dot(self.rotation_matrix2D(theta), u0)
            vectors[i, 4:6] = vec_temp[:] # detector pixel (0,0) to (0,1).
        return vectors

    def vec_geom_init3D(self, angles_rad, DetectorSpacingX, DetectorSpacingY, CenterRotOffset, projection_shifts2d):
        #define 3D vector geometry
        s0 = [0.0, -1.0, 0.0] # source        
        u0 = [DetectorSpacingX, 0.0, 0.0] # detector coordinates
        v0 = [0.0, 0.0, DetectorSpacingY] # detector coordinates

        vectors = np.zeros([angles_rad.size, 12])
        for i in range(0, angles_rad.size):
            d0 = [CenterRotOffset - projection_shifts2d[i, 0], 0.0, CenterRotOffset - projection_shifts2d[i, 1]]  #detector
            theta = angles_rad[i]
            vec_temp = np.dot(self.rotation_matrix3D(theta), s0)
            vectors[i, 0:3] = vec_temp[:] # ray position
            vec_temp = np.dot(self.rotation_matrix3D(theta), d0)
            vectors[i, 3:6] = vec_temp[:] # center of detector position
            vec_temp = np.dot(self.rotation_matrix3D(theta), u0)
            vectors[i, 6:9] = vec_temp[:] # detector pixel (0,0) to (0,1).
            vec_temp = np.dot(self.rotation_matrix3D(theta), v0)
            vectors[i, 9:12] = vec_temp[:] # Vector from detector pixel (0,0) to (1,0)
        return vectors

