source /lustre/fs12/portfolios/nvr/users/ymingli/miniconda3/etc/profile.d/conda.sh
conda activate pycolmap
python /lustre/fsw/portfolios/nvr/users/ymingli/projects/mhb/citygaussian/colmap/python/examples/panorama_sfm.py --input_image_path /lustre/fsw/portfolios/nvr/users/ymingli/datasets/supermarket/Supermarket/sample_5 --output_path /lustre/fsw/portfolios/nvr/users/ymingli/datasets/supermarket/Supermarket/sample_5_process --matcher vocabtree
