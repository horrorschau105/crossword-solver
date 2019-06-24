# crossword-solver

Hi, this is a crossword solver I've written for my BSc thesis. 

## What is needed to run
- a file with vector for each word in language (i.e. those available on https://fasttext.cc)
- a crossword in specific format (see tests/)
- a solution to the crossword (for ranker required only. see tests/ for format)
- a file with word frequencies is optional, but the solver works better with it (you can find i.e. here: https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/PG/2006/04/1-10000
- python 2.7
- numpy
## Usage

To solve a crossword, simply run
```
python main.py <vectors file> <crossword file> <frequencies file>
```

To compare different sentence_vector method, simply add it to _ranker.py_ and run
```
python main.py <vectors file> <crossword file> <frequencies file>
```

### About the solver

The main idea is to use A* for searching a solution in a huge tree of partially filled crosswords, with root as an empty grid. We need to generate lists of fitting words for each clue. To do it, we count a weightened average of vectors of words in the clue, with weight function as a logarithm of a frequence of the word. A heuristic function ranking a crossword will prefer words more accurate to the hints, that's way solution will be rather correct. See *thesis.pdf* for more detailed abstract and pseudocodes of used algorithms.

