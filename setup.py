import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
     name='pikama',  
     version='0.1',
     scripts=['pikama'] ,
     author="Luis Toledo",
     author_email="luisernesto.toledo@gmail.com",
     description="Video analysis app and OSC server designed for Raspberry Pi camera",
     long_description=long_description,
   long_description_content_type="text/markdown",
     url="https://github.com/luistoledo/pikama",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
     setup_requires=['imutils', 'python-osc', 'numpy', 'opencv-python', 'picamera']
 )