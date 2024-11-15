# DOT to C# Class Translator

This small Python script translates a DOT file to C# classes. The script makes A LOT of assumptions about the layout of the DOT file, based on the HOWEST-provided files.
It can be used to save time typing, but every line of code should still be doublechecked.
## Usage

1. **Drag and Drop**: You can simply drag your `.dot` file onto the provided batch (`.bat`) file to automatically generate C# classes.
2. **Run from Command Line**: Alternatively, you can run the Python script directly, passing your `.dot` file as an argument.

   ```bash
   python3 convert.py your_file.dot
After running the script, you will be asked for the name of your class library project, this will be used to populate the namespace.  
When the script is done your generated C# classes can be found in the output folder.

Example:  
Here’s an example command to run the script manually from the command line:

```bash
python3 convert.py example.dot
```
Or simply drag example.dot onto convert.bat.

## Notable features
- Detect get and set methods for a property and decide access type for the property or field based on them, 
excludes these property methods from the methods if they can be implemented as getter or setters.  

- Initialize fields and properties in given order according to UML
  
- Do nullOrWhitespace check on every string argument in the constructor

- Do null check on every other nullable in the constructor 

## Notable issues
- parameters for methods that are not the constructor are not given names or autofilled

- Inheritance is not added in the code

- The code will have errors if there are typos or inconsistencies in the dot file. You are responsible for the end result.

## Important Note
This script was quickly put together and makes a lot of assumptions about the input file. Please check each generated file thoroughly for potential issues or bugs. I am not responsible for any issues in the generated classes.
The classes will have no relationships, so you should still add implementation and inheritance of your classes.
Enjoy your C# classes!
