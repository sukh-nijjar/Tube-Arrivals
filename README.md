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

# Requirements

## User Story
**As a** passenger  
**I want** to know when the next trains are arriving at my local station  
**So that** I can work out when I need to leave my location in order to get the train I need and become aware of any issues

## Acceptance Criteria
**GIVEN**  
A passenger wants to know train arrivals for a local station  
**WHEN**  
They search for arrival information  
**THEN**  
They must specify the station name they are interested  

**GIVEN**  
A station is submitted for viewing it's arrivals information  
**WHEN**  
Arrivals information is retrieved  
**THEN**  
The following information is displayed:
- Platform number
- Train sequence (e.g. 1,2,3)
- Destination station
- When due (in minutes)
- Expected arrival time
- Current location of train

**GIVEN**  
There is no arrivals information available for a station  
**WHEN**  
Arrivals information is retrieved  
**THEN**  
A  message is displayed informing no arrivals information is available and line status is displayed  

# Design  
## User Interface  
### Responsive  
* The application must render properly across various device types  
### Look and Feel
* The site will have a background image which invokes familar feeling for tube users  
* The arrivals presentation will be inspired by the digital display boards found at tube stations  
* Font to replicate dot matrix display is Codystar  
* Font to display the station name and line status is the elegant Julius Sans One  
* lines will be represented by their familar TfL  colours (e.g. the central line is red, circle line is yellow)  
* line status will be represented by the familar Red-Amber-Green scheme  (Red = severe  delays, Amber = minor  delays, Green = good service)  

