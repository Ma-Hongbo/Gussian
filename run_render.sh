source /lustre/fs12/portfolios/nvr/users/ymingli/miniconda3/etc/profile.d/conda.sh
conda activate gaussian_splatting
python /lustre/fs12/portfolios/nvr/projects/nvr_av_end2endav/users/ymingli/projects/mhb/citygaussian/Grendel-GS/render.py -s /lustre/fs12/portfolios/nvr/projects/nvr_av_end2endav/users/ymingli/datasets/supermarket/sample_5_process --model_path /lustre/fs12/portfolios/nvr/projects/nvr_av_end2endav/users/ymingli/datasets/supermarket/sample_5_result --bsz 128
