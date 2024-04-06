# Fungelet, a very convenient befunge IDE
## Screenshot
![image](https://cdn.discordapp.com/attachments/881463505755197460/1226180037880057946/Screenshot_2024-04-06_at_10.41.35_PM.png?ex=6623d426&is=66115f26&hm=0c2512edd053d35fcc4fe805d566061613716c8e71f3d3d6cda9beb313db7276&)

## Installation
```bash
git clone https://github.com/lomnom/Fungelet/
cd Fungelet
git clone https://github.com/lomnom/Terminal/
mv Terminal/Term*.py .
rm -rf Terminal
pip3 install pyyaml
python3 Run.py -h
```
- Works on Mac and linux natively
- Tested in WSL (use a good terminal tho)

## Usage
Tutorial & demonstration [here](https://www.reddit.com/1bxdu7b/)

Features of this include:
- Cut, paste, chunk delete and rotate
- Quick instruction reference
- Seeing the pointers and plane evolve live, right in front of your eyes
- An input system built for productivity
- Visualising non-ascii characters as coloured boxes
- Negative regions are as accessible as positive ones
- Concurrency is easy and natural
- And many more quality of life features, on top of an almost entirely compliant implementation of befunge.

#### Note: It is strongly recommended to follow along with the hands-on guide by running `python3 Run.py -h`!
befunge examples [here](http://www.nsl.com/k/befunge93/index.html)

## (Dev) Documentation 
As it is unlikely that there will ever be a substantial number of developers wanting to contribute to or extend this application, I have chosen not to write code documentation. Please feel free to contact me at `zhaoxiong.ang@gmail.com` for any queries and explanations related to this application's code.