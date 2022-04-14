# /usr/bin/env python
import datetime
import os
import traceback
import re
import fileinput

actionAudits = []
common_excluded_paths = ['venv', '.idea', 'node_modules', 'bower_components', 'dist', 'build', '__pycache__', 'git',
                         '.git', 'Python']
common_excluded_files = ['audits.txt', 'substitute.py', 'substitutor.py', 'substitutor.pyc', 'substitutor.pyw',
                         'substitutor.pyo', 'substitutor.exe', 'Redactor.py', '.git', 'repos_list.json',
                         'repoList.json', 'repoList.txt', 'repos.txt', '.settings.xml', '.gitignore', '.gitattributes',
                         'settings.xml']

startTime = int(round(datetime.datetime.now().timestamp()) * 1000)
auditFileName = f'Substitor_Audit_{startTime}.txt'


# Main functions
def searchAndReplaceInFiles(keyword, substitute, baseDirectory, directoryExclusions):
    filesToBeEdited = findAllFilesContainingKeyword(keyword, baseDirectory, directoryExclusions)
    with fileinput.FileInput(files=filesToBeEdited, inplace=True) as file:
        print(f'Processing files: {file.filename}')
        for line in file:
            line = line.replace(keyword, substitute)
            print(line, end='')
        file = file.nextfile()
    audit(f'{len(filesToBeEdited)} files were edited.')
    audit(filesToBeEdited)
    filesToBeEdited.clear()
    writeAuditsToFile()


def findAllFilesContainingKeyword(keyword, baseDirectory, directoryExclusions):
    """
    Finds all files containing the key word.
    """
    filesToChange = []
    keywordRegex = re.compile(re.escape(keyword))
    for root, dirs, files in os.walk(baseDirectory, topdown=True, followlinks=False):
        for directory in directoryExclusions:
            if directory in dirs:
                audit(f'Skipping excluded directory: {directory}')
                dirs.remove(directory)
        for file in files:
            if getFileName(file) in common_excluded_files:
                audit(f'Skipping excluded file: {file}')
                continue
            else:
                filePath = os.path.join(root, file)
                audit(f'Checking file: {filePath}')
                # try to read file, skip if not readable
                try:
                    with fileinput.FileInput(filePath, inplace=False) as f:
                        for line in f:
                            anyMatch = re.search(keywordRegex, line)
                            if anyMatch:
                                filesToChange.append(filePath)
                                break
                    f.close()
                except Exception as readError:
                    audit(f'Skipping file, unreadable: {filePath}')
                    audit(f'Exception: {formatErrorWithTrace(readError)}')
                    continue
                writeAuditsToFile()
    return filesToChange


# Audit functions
def audit(action):
    """
    Audits the actions taken by this script.
    """
    pretty = f'{action}\n'
    print(pretty)
    actionAudits.append(pretty)


def writeAuditsToFile():
    """
    Writes the audits to a file.
    """

    with open(auditFileName, 'a') as f:
        f.writelines(actionAudits)
    actionAudits.clear()
    f.close()


# Utility functions
def isSymLink(path):
    """
    Checks if the path is a symbolic link.
    """
    return os.path.islink(path)


def checkIfPathContainsExcludedWords(path, excludedWords):
    """
    Checks if the path contains any of the excluded words.
    """
    for excludedWord in excludedWords:
        if excludedWord in path:
            return True
    return False


def currentDirectory():
    """
    Returns the current directory.
    """
    return os.getcwd()


def getFileName(path):
    """
    Returns the file name.
    """
    return os.path.basename(path)


def formatErrorWithTrace(e):
    """
    Formats the error with the trace.
    """
    return f'{e}\n{traceback.format_exc()}'


# User Input functions

def askForBaseDirectory():
    """
    Asks the user for the base directory.
    """
    baseDirectory = input("Enter the base directory: \n")
    return baseDirectory


def askForDirectoryExclusions():
    """
    Asks the user for directories to exclude.
    """
    directoryExclusions = input("Enter the directory(ies) to exclude: \n")
    return directoryExclusions.split()


def askForKeyWords():
    """
    Asks the user for the keyword.
    """
    keyword = input("Enter the keyword to replace: \n")
    return keyword


def askForSubstitutes():
    """
    Asks the user for the substitute for the corresponding key word.
    """
    substitutions = input("Enter the substitute word: \n")
    return substitutions


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    try:
        baseDirectory = askForBaseDirectory()
        if baseDirectory == '.' or baseDirectory == './':
            baseDirectory = currentDirectory()
        excludeDirectories = askForDirectoryExclusions()
        excludeDirectories = excludeDirectories + common_excluded_paths
        audit(f'Excluded directories: {excludeDirectories}')
        keyword = askForKeyWords()
        substitute = askForSubstitutes()
        audit(f'Key words: {keyword}')
        audit(f'Substitutes: {substitute}')
        searchAndReplaceInFiles(keyword, substitute, baseDirectory, excludeDirectories)
        writeAuditsToFile()
    except Exception as e:
        audit(f'Error: {formatErrorWithTrace(e)}')
        writeAuditsToFile()
        raise e
