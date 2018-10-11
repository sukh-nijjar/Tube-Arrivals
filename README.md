# Tube-Arrivals
Tube Arrivals is a responsive minimalist application that does one concise thing : displays train arrivals for a tube station on the famous London Underground.

## Pre-requisites
* An installation of Python
## Setting up and running application
After you’ve downloaded the source code it’s worth [creating a virtual environment](https://uoa-eresearch.github.io/eresearch-cookbook/recipe/2014/11/26/python-virtual-env/) to keep a separation between python libraries you may have installed locally and the ones used by this application.  
Once virtual environment is activated from the command line run:  
* pip install flask 
   
To start the application:  
* python main.py

# Technical Details
Python web application using:
* Flask
* Bootstrap 4
* Transport for London Unified API
* Google Fonts

# Design Choices
Given there are only 2 views each with specific client-side needs javascript has been directly included in the 2 html pages.
