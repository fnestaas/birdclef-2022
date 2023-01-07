# birdclef-2022
AI4Good project


#### Setup
- The path to the data and the repository is now read from environment variables which you have to create: 
- You will need $ pip install python-decouple (or requirements.txt, which does so automatically)
1. $ touch .env 
2. $ nano .env 
3. add the variables DATA_PATH, OUTPUT_DIR and SPEC_PATH on Euler they are:
* DATA_PATH=/cluster/work/igp_psr/ai4good/group-2b/birdclef-2022/data/
* OUTPUT_DIR=/cluster/work/igp_psr/ai4good/group-2b/birdclef-2022/output/
* SPEC_PATH=/cluster/work/igp_psr/ai4good/group-2b/birdclef-2022/data/spec/
* SPLIT_PATH=/cluster/work/igp_psr/ai4good/group-2b/birdclef-2022/splits/split_1/
* AUGMENT_PATH = /cluster/work/igp_psr/ai4good/group-2b/birdclef-2022/data/aug/
* SPLIT_PATH_KFOLD=/cluster/work/igp_psr/ai4good/group-2b/Lars_code/birdclef-2022/splits/3_fold_split/
* NOISE_PATH=/cluster/work/igp_psr/ai4good/group-2b/freefield/freefield1010_nobirds/wav

Of course, you can also download the data and set the paths above as you wish. 
In that case, make sure that ``DATA_PATH`` contains what you download from [the BirdClef 2022 Challenge](https://www.kaggle.com/competitions/birdclef-2022/data), and ``NOISE_PATH`` contains the freefield noise data TODO

#### Running the Code
To run the full pipeline, set up the .env file as described above and run `main.py`. This will however be *very slow*, and we recommend not recomputing the data, as we shall describe in the following.

The main scripts are `prepare_data.py`, `train.py`, `train_ablation_new.py`, and `train_ablation_original.py`.
`prepare_data.py` prepares all of the data and will take a lot of time to do so, because computing the audio augmentations is very costly. 
Instead, we recommend setting the paths as listed above and running the scripts containing "ablation", as these are the ones that generate the output relevant for the report.

`train.py` is a regular train script which can be used to train a regular model, or run a cross validation study with three splits.
It takes a number of arguments, a description of which can be found in `train.py`, and allows creating many different models using different pre- and post-processing steps, augmentations and (pretrained) model architectures.
On the other hand, the `train_ablation` scripts call `train.py` with different parameters, instantiating different pipelines in doing so.
`train_ablation_original.py` runs the ablation study for the original baseline, whereas `train_ablation_new.py` runs it for the changed baseline. 

#### Comments on the repository
There are many folders in this repository. 
They are organized as follows:
- ablation: contains all the code which is relevant for calling `train.py` with different configurations sequentially
- modules: contains the bulk of the code in the project. All of the modules in the pipeline can be found here (see `modules/readme.md`).
- splits: contains the train and validation splits for each fold in the cross validation, and also the train and validation split when not using cross validation.
- output: saved models during runs. 
- data: all of the datasets and metadata (also augmented data and precomputed spectrograms).

##### References

Some Links:

- https://www.researchgate.net/publication/362592701_Overview_of_BirdCLEF_2022_Endangered_bird_species_recognition_in_soundscape_recordings
- http://ceur-ws.org/Vol-3180/paper-170.pdf
- http://ceur-ws.org/Vol-2936/paper-134.pdf (2nd place 2021)


Dataset:
- https://www.kaggle.com/competitions/birdclef-2022/data

AUGMENTATION (Library audiomentations)
- https://github.com/iver56/audiomentations
