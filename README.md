# DOT to C# Class Translator

This small Python script translates a DOT file to C# classes. The script makes A LOT of assumptions about the layout of the DOT file, based on the HOWEST-provided files.

## Usage

1. **Drag and Drop**: You can simply drag your `.dot` file onto the provided batch (`.bat`) file to automatically generate C# classes.
2. **Run from Command Line**: Alternatively, you can run the Python script directly, passing your `.dot` file as an argument.

   ```bash
   python3 convert.py your_file.dot
After running the script, your generated C# classes can be found in the output folder.

Important Note
This script was quickly put together and makes a lot of assumptions about the input file. Please check each generated file thoroughly for potential issues or bugs. I am not responsible for any issues in the generated classes.
The classes will have no relationships, so you should still add implementation and inheritance of your classes.

Example

Here’s an example command to run the script manually from the command line:

```bash
python3 convert.py example.dot
```
Or simply drag example.dot onto convert.bat.
Enjoy your C# classes!
