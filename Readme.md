# Fungelet, a very convenient befunge IDE
## Installation
```bash
git clone https://github.com/lomnom/Fungelet/
cd Fungelet
git clone https://github.com/lomnom/Terminal/
mv Terminal/Term*.py .
rm -rf Terminal
pip3 install pyyaml
python3 Run.py
```
- Works on Mac and linux natively
- Tested in WSL (use a good terminal tho)
## Usage
#### Note: It is strongly recommended to follow along with this hands-on guide by running `python3 Run.py -h`!
1. Movement
 - Use the arrow keys to move around and turn.
 - Use the enter key to jump where a cursor would. The enter key does nothing if there are multiple options.
 - Tip: take advantage of wrapping and warp over whitespace with enter.
2. Status Text: the text on the bottom left.
 - The first part will always have the format of `At (x,y) = value, moving (dx,dy)`
 - The second part will usually show documentation of the tile the cursor is on, but also shows other messages depending on context.
3. The sidebar on the right
 - Use shift left and shift right to change sidebar
 - Every sidebar has its own utility.
4. Tooltips: if you forget instructions.
 - Use ctrl t to summon tooltips.
 - Use arrow keys to move, and enter to place char.
 - Every colour is a different category.
 - Use ctrl t again to close.
5. Editing: The fifth sidebar
 - While in the fifth sidebar, you can type to place tiles.
 - Notice that the cursor deduces where to go like the enter key.
 - Disable this movement by pressing tab.
 - Use the backspace to delete the tile behind the cursor, and space to delete in front.
 - Press ctrl l to type a number and ctrl k to place. (Note that non-ascii values are displayed as coloured rectangles.)
6. Grabbing: The copy-paste & rotate
 - Press ctrl c at a corner then move to an opposite corner to highlight the area.
 - Here you have two choices:
   - Press ctrl d to delete the area or
   - Press ctrl c to grab the area.
     - From here, you can 
       - keep pressing ctrl c to rotate the area (StatusText will warn if rotation is not functional)
       - press ctrl p to place down a copy of the area without deselecting
       - press ctrl d to place down the area anddeselect.
 - Tip: the clipboard is not cleared when loading another file.
7. Execution: The third sidebar
 - Press ctrl l to type a number in the speed box.
 - Press ctrl x (works in any sidebar) to run.        
 - Press ctrl r (works in any sidebar) to step.
 - Tip: You can stil edit and do anything while running.
8. Pointers: The second sidebar.
 - Press S to spawn a pointer.
 - Notice the pointer is a struckthrough block.
 - The pointer is posessed right after you spawn it.
 - When posessed,
   - You can see the stack (scroll with w,s)
   - You can clear the stack with C
   - You can kill the pointer with K
   - The pointer and cursor coords and delta are synchronised.
 - You can unposess a pointer by pressing P, and also posess a pointer at the same position as the cursor by pressing P.
 - Note: pointers with a lower #id run first.
9. I/O: The fourth sidebar.
 - This is where stdin and stdout happens.
 - ctrl l to type in the input box.
 - C and c to clear input and output respectively.
 - w and s to scroll.
10. Files: The first sidebar.
 - This is where you load and save.
 - Use ctrl L to enter the filename.
 - Use S to save to file, and L to load from
     file.
 - Saving an empty plane is stopped, and loading
   to a non-empty plane needs confirmation.
 - Press C five times to clear.
11. Misc.
 - Non ascii values are rendered as coloured rectangles of ansi colour val%255+1
 - Input is non blocking by default. Change BlockingInput to true in config.yaml for blocking input.
 - Most global keys are reconfigurable in config.yaml.
 - Ctrl w to quit.
 - If there is only one file in pwd, it will be automatically entered into the textbox.
 - Please submit bug reports for bugs or feature suggestions.
 - Open a file from the cli with `python3 Run.py [file]`, run it bare with `python3 Run.py` and open this tutorial with `python3 Run.py -h`
befunge examples [here](http://www.nsl.com/k/befunge93/index.html)

## (Dev) Documentation 
As it is unlikely that there will ever be a substantial number of developers wanting to contribute to or extend this application, I have chosen not to write code documentation. Please feel free to contact me at `zhaoxiong.ang@gmail.com` for any queries and explanations related to this application's code.

## Screenshot
![image](https://cdn.discordapp.com/attachments/855698634032152576/1173253987869409401/image.png?ex=656348ec&is=6550d3ec&hm=91aa08e39b14cdbf199e162dfabfb9581987479e0a8a20bd0592b6346df71fbf&)
