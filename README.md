# ZybooksAutoComplete

## Running
You will need to use python2 to run the auto-completer.

The following librarie(s) are required and can be installed through pip:
  - requests
  
  After installing the required dependencie(s), you can simply run the completer as follows:
  `python run.py`
  
  You will then be prompted to enter your Zybooks email and password.
  
  ## Configuration
  All configuration necessary to use the completer can be found in `settings.py`.
  
  I will list each of the configurable values in this file:
  
    - COURSE: This can be your class code, your full class name, or the Zybook code (in the url when accessing the class) 
    
        - Examples can be found in `settings.py` at the top of the file
        
    - CHAPTER_NUMBER: The chapter in zybooks to complete sections in
    
    - SECTION_NUMBERS: Comma separated list of sections you wish the completer to complete
    
        - Can also use '\*' to complete all sections in the chapter
        
    - TIME_INTERVAL: The base time in seconds to wait before attempting another zybooks problem. (To look authentic)
    
        - The actual time can be up to PERCENTAGE_VARIANCE above or below this time.
        
    - PERCENTAGE_VARIANCE: As previously mentioned, the percent variance to deviate from the base time (TIME_INTERAL)
    
        - You can use 0, if you want a constant time, but it will appear more obvious
