import datetime
import os
import traceback
import re

actionAudits = []
totalReplacementCount = 0
common_excluded_paths = ['venv', '.idea', 'node_modules', 'bower_components', 'dist', 'build', '__pycache__', 'git',
                         '.git', 'Python']
common_excluded_files = ['audits.txt', 'substitute.py', 'substitutor.py', 'substitutor.pyc', 'substitutor.pyw',
                         'substitutor.pyo', 'substitutor.exe', 'Redactor.py', '.git', 'repos_list.json',
                         'repoList.json', 'repoList.txt', 'repos.txt', '.settings.xml', '.gitignore', '.gitattributes',
                         'settings.xml']

startTime = int(round(datetime.datetime.now().timestamp()) * 1000)
auditFileName = f'Substitor_Audit_{startTime}.txt'


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


def askForBaseDirectory():
    """
    Asks the user for the base directory.
    """
    baseDirectory = input("Enter the base directory: \n")
    return baseDirectory


def askForKeyWords():
    """
    Asks the user for the keywords.
    """
    keyWords = input("Enter the keyword(s) to replace (3 or less): \n")
    return keyWords


def askForSubstitutes():
    """
    Asks the user for the substitute for the corresponding key words.
    """
    substitutions = input("Enter the substitute(s) (3 or less): \n")
    return substitutions


def getFileName(path):
    """
    Returns the file name.
    """
    return os.path.basename(path)


def searchAndReplaceInFiles(keyWordSubstitutions, baseDirectory, directoryExclusions):
    """
    Searches and replaces the key words with the substitutes in the files.
    """
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
                    fc = getFileContents(filePath)
                    resp = replaceText(fc, keyWordSubstitutions)
                    fc = resp[0]
                    changeCount = resp[1]
                    if changeCount > 0:
                        writeFileContent(filePath, fc)
                except Exception as e:
                    audit(f'Skipping file, unreadable: {filePath}')
                    audit(f'Exception: {formatErrorWithTrace(e)}')
                    continue
                writeAuditsToFile()


def writeFileContent(path, content):
    """
    Writes the file contents.
    """
    with open(path, 'w') as f:
        audit(f'... writing file content to {path}')
        f.write(content)


def getFileContents(path):
    """
    Returns the file contents.
    """
    with open(path, 'r') as f:
        audit(f'... reading {path}')
        return f.read()


def replaceText(text, keyWordSubstitutions):
    """
    Replaces the key words with the substitutes in the text.
    """
    count = 0
    global totalReplacementCount
    for (keyword, substitute) in keyWordSubstitutions:
        audit(f'Replacing {keyword} with {substitute}')
        regex = re.compile(r'\b' + keyword + r'\b')
        (newText, qty) = re.subn(regex, substitute, text)
        count += qty
        text = newText
    audit(f'{count} replacements made')
    totalReplacementCount += count
    return [text, count]


def checkIfPathContainsExcludedWords(path, excludedWords):
    """
    Checks if the path contains any of the excluded words.
    """
    for excludedWord in excludedWords:
        if excludedWord in path:
            return True
    return False


def isSymLink(path):
    """
    Checks if the path is a symbolic link.
    """
    return os.path.islink(path)


def coupleKeyWordsWithSubstitutes(keyWords, substitutes):
    """
    Couples the key words with the substitutes.
    """
    return zip(keyWords.split(), substitutes.split())


def currentDirectory():
    """
    Returns the current directory.
    """
    return os.getcwd()


def askForDirectoryExclusions():
    """
    Asks the user for directories to exclude.
    """
    directoryExclusions = input("Enter the directory(ies) to exclude: \n")
    return directoryExclusions.split()

def formatErrorWithTrace(e):
    """
    Formats the error with the trace.
    """
    return f'{e}\n{traceback.format_exc()}'

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    try:
        baseDirectory = askForBaseDirectory()
        if baseDirectory == '.' or baseDirectory == './':
            baseDirectory = currentDirectory()
        excludeDirectories = askForDirectoryExclusions()
        excludeDirectories = excludeDirectories + common_excluded_paths
        audit(f'Excluded directories: {excludeDirectories}')
        keyWords = askForKeyWords()
        substitutes = askForSubstitutes()
        keyWordSubstitutions = coupleKeyWordsWithSubstitutes(keyWords, substitutes)
        audit(f'Key words: {keyWords}')
        audit(f'Substitutes: {substitutes}')
        audit(f'Key Word Substitution Tuple: {keyWordSubstitutions}')
        searchAndReplaceInFiles(keyWordSubstitutions, baseDirectory, excludeDirectories)
        audit(f'Total replacements made: {totalReplacementCount}')
        writeAuditsToFile()
    except Exception as e:
        audit(f'Error: {formatErrorWithTrace(e)}')
        writeAuditsToFile()
        raise e
