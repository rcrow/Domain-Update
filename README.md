# Domain-Update
Written by Ryan Crow, USGS

We manage attribution of fields in a series of SDE databases designed for geologic mapping with domains. Domains are set for mapunit, data source ID, etc. Some domains need to be updated regularly in multiple databases. Our approach is to maintain a series of Arc tables and excel file that have the code and description values for those domains. These master files are updated when needed and then these scripts are used to update the domains in the relevant databases. Before updating the domains a copy of the existing domain is made. The script also emails all the users so they know that a change has been made. 
