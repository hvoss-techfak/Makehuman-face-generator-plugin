# Makehuman-face-generator-plugin
This plugin utilises the python face recognition library, to automatically create faces from reference images.
The project is based upon the face_recognition library (https://github.com/ageitgey/face_recognition), as well as makehuman.

## Installation

### Requirements

* Python 3.5+
* pip


### Installation Options:

#### Installing on Mac or Linux

A virtual enviroment (venv,anaconda) is recommended but not necessary)
* See here for Install Instructions: [venv](https://gist.github.com/frfahim/73c0fad6350332cef7a653bcd762f08d), [anaconda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html)
* [Install dlib](https://gist.github.com/ageitgey/629d75c1baac34dfa5ca2a1928a7aeaf) (GPU support is highly recommended)

Install the requirements using pip
```bash
	pip install -r requirements.txt
```

Clone the source code version of makehuman from [here](https://github.com/makehumancommunity/makehuman)
* Move into the cloned repository.
* Add the 0_modeling_facerec.py from this repository to the makehuman/plugins folder.
* Run the makehuman project (in your virtual enviroment) using:
```bash
	python makehuman/makehuman.py
```
	
#### Installing on Windows:
	
* A virtual enviroment (anaconda) is recommended but not necessary)
* See here for Install Instructions: [anaconda](https://docs.anaconda.com/anaconda/install/windows/)

##### Install dlib (GPU support is highly recommended)
Installing Dlib on windows is a bit more complicated than on linux or mac.
* [Here is an install instruction](https://www.learnopencv.com/install-dlib-on-windows/)
* [Another instruction from the face recognition page](https://github.com/ageitgey/face_recognition/issues/175#issue-257710508)

Install the requirements using pip
```bash
	pip install -r requirements.txt
```

Clone the source code version of makehuman from [here](https://github.com/makehumancommunity/makehuman)
* Move into the cloned repository.
* Add the 0_modeling_facerec.py from this repository to the makehuman/plugins folder.
* Run the makehuman project (in your virtual enviroment) using:
```bash
	python makehuman/makehuman.py
```
	
### Usage:
Currently the preview is rendered in a seperate windows which can be hidden behind the main window.
* After starting makehuman a new menu should have appeared: ![](https://github.com/hvoss-techfak/Makehuman-face-generator-plugin/blob/master/img/Img1.JPG?raw=true)

The "Face Reference Directory" opens a folder dialog window, which should be pointed to the reference images.
* Attention: The Images are loaded from all subfolders.

Multiple different optimizer methods can be chosen, but it is recommended to only use one.

* The random method is currently giving the best results.

After all options are chosen, press "Do Face Reconstruction" and wait.
* The frozen window is normal, the loading of the images can take up to 10 minutes, depending on the amount of images.
Depending on your hardware the optimization can take a long time, the preview window should update every 30-60 seconds.
	
	