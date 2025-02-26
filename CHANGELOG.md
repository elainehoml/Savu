All notable changes to this project are documented in this file. 
*******************************************************************
# Savu Version 4.2, *planned release December 2021*

## _Core_
* Statistics (TODO) 
* Iterative plugins (TODO) 

## _Existing Plugins_

### Centering

### Simulation
  * A sub-pixel misalignment simulation for projections from TomoPhantom
  * Various Tomoloader fixes. Closing of the linked nxs file with MPI fixed. 

### Reconstruction
  * AstraReconGPU, 3D GPU methods are added (CGLS3D_CUDA, SIRT3D_CUDA)
  * ForwardProjector works with 3D geometry
  * 3D geometries can accept metadata for x-y shifts and correct the misalignment
  * GPU memory usage check for *tomobar_recon_3D* plugin to avoid CUDA error
  * *tomobar_recon_3D* access to regularisation using Wavelets, try set regularisation method e.g. to 'PD_TV_WAVELETS'
  
### Filters
  * GPU memory usage check for *ccpi_denoising_gpu_3D* plugin to avoid CUDA error

## _New plugins_
### Alignment
  * *projection_2d_alignment* - works with 2 sets of 3D projection data by comparing projection images and estimating vertical-horizontal shifts in data. The vector shifts then stored in experimental data to be used later in 3D vector geometry.
### Filters
  * *wavelet_denoising_gpu* - a GPU plugin for denoising using Wavelets. Highly optimised for GPU performance. 

## _Updated and new packages as dependencies_
  * A new [pypwt](https://github.com/pierrepaleo/pypwt "pypwt") GPU wavelet package added through Jenkins build and savu-dep channel 
  * ToMoBAR and TomoPhantom packages have been updated

## _Configurator_ 

## _Documentation_

## _BUGS_
  *  res_norm bug when using AstaReconGPU with CGLS_CUDA

## Other
  * The test dataset 24737.nxs has been changed to tomo-standard.nxs
  * The synthetic test data has been added 
  * Environment variable *type* is replaced with *GPUarch_nodes*



*******************************************************************
# Savu Version 4.1 (released September 2021) 