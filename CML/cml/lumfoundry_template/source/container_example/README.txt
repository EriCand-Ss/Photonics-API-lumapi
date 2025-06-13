This document describes the specifics of setting up a container element which combines 2 or more elements of a library into one element.
Copyright (c) 2003-2020, Ansys, Inc. All rights reserved.  

Unauthorized use, distribution, or duplication is prohibited.  
This product is subject to U.S. laws governing export and re-export.  

For full Legal Notice, see documentation.

1. Foundry .XML file setup
	1.1. The foundry .XML file should include the container element as well as its children (sub-elements) as stand-alone elements listed under the element list.
	1.2. It is required that the children should be listed above the container element in the element list so that they are built before the container is built.
	1.3. The children should also be listed in a "sub-element" list under the container element.
	1.4. In order to avoid including the children as stand-alone elements in the generated library, a <remove_sub_elements> tag can be added under the container element 
	1.5. A selection code which selects an specific child of the container needs to be added under each child in the sub-element list.
	1.6. For an example of how the above-mentioned requirements are implemented in the foundry .XML file, please see lumfoundry.xml (elements "container_example", "container_element_child1", "container_element_child2").      

2. Container element source data and .LSF file setup  
	2.1. The .LSF file for the container element should include the children names, a list of parent and children elements parameters and selection code for selecting each child based on the user's input. For an example, please refer to the source data files for elements "container_example", "container_element_child1", and "container_element_child2" in lumfoundry template.        
	2.2. A child's parameters will be inherited from its parent container  
	2.3. Once the library is built, the QA scripts for each child element will be created under its own source data folder. The container element itself will not have any QA script created.





