def textHeadGenerator(headText):
    title = headText
    paddingStarCount = 6
    paddingSpaceCount = 4
    starRowString = '*' * (len(title) + paddingStarCount)
    blankRowString = '*' + (' ' * (len(title) + paddingSpaceCount)) + '*'
    titleRowString = '*  ' + title + '  *'
    fullTextHeadString = starRowString + '\n' + blankRowString + '\n' + titleRowString + '\n' + blankRowString + '\n' + starRowString
    print(fullTextHeadString)
