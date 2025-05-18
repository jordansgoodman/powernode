# About

One drawback with many low-code analytics tools is that they use eager evaluation when applying transformations. 

For example - node 1 is data from a CSV. node 2 data is then loaded from a database. They are both committed into memory, THEN joined together. 

My goal with this project is to introduce lazy evaluation via polars, powered by fastAPI as a backend, and TypeScript for the GUI in a local server on your browser.