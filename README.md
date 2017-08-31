# create-camera-tool
Create maya camera with data from real world camera

This is a production tool developed by Shirui Zhang.

This tool runs in maya 2016.

Create Camera Tool provides artist with a friendly UI with categorized real world camera data. User can easily look up a certain camera by "Manufacturer", "Model", "Setting" and also choose a compatible "Lens" with the selected camera body. It is very helpful for Lookdev artist who needs start their work by creating a maya camera which matches the one used in the live action shot.

Data:
The data used in this tool is stored in two yaml files. One contains camera body information, another contains lens data.
*The yaml file which comes with the code has been modified in purpose and is only for tool demonstration.

UI:
The UI consists of Three parts.
First, four list widgets which interactively display the data in a yaml file based on user selection. There is a search field for "Setting" list. The "Generic" item in "Lens" list allows user to input a custom focal length.

Second, a display widget at the bottom which display all information associated with the current selections. Beside the "Camera FOV", there is a lock icon. By clicking the lock icon, the current FOV value with be held and it will show a "Recalculated focal length". This feature comes from production request. It allows user to switch camera but maintains the same FOV with the previous one.

Last, "Apply", "Create" buttons which update existing camera or create a new camera based on the selection.
