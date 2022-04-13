import os
import re

excluded_files = ['COMMIT_EDITMSG', 'README.md', 'LICENSE', 'locator.py']


def askForBaseDir():
    baseDir = input("Enter base directory: ")
    return baseDir


def askForSearchWord():
    searchWord = input("Enter search word: ")
    return searchWord


def findFilesContainingSearchWord(baseDir, searchWord):
    matches = []
    for root, dirnames, filenames in os.walk(baseDir, topdown=True, followlinks=False):
        for file in filenames:
            if os.path.isfile(file) and not isFileHidden(file) and not isFileExcluded(file):
                print(f'Searching file: {file}')
                contents = open(file, 'r').read()
                regex = re.compile("\W" + searchWord + "*")
                found = re.findall(regex, contents)
                matches = matches + found
    return matches


def isFileExcluded(file):
    return file in excluded_files


def isFileHidden(file):
    return file.startswith('.')


def getCurrentDir():
    return os.getcwd()


def writeToFile(matches):
    file = open('results.txt', 'w')
    for match in matches:
        file.write(match + '\n')
    file.close()


if __name__ == '__main__':
    baseDir = askForBaseDir()
    if baseDir == "" or baseDir == "." or baseDir == "./":
        baseDir = getCurrentDir()
    searchWord = askForSearchWord()
    print(baseDir)
    print(searchWord)
    files = findFilesContainingSearchWord(baseDir, searchWord)
    writeToFile(files)
    print(f'Found {len(files)} files that match the search word "{searchWord}"')
