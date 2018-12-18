import re
import timeit
from itertools import islice


class Parse:
    def __init__(self, stopWords):
        self.stopWords = stopWords
        self.NumOfNumbers = 0

    def parseText(self, text):
        string9 = "September SEPTEMBER"
        string8 = "February November December FEBRUARY NOVEMBER DECEMBER"
        string7 = "January October JANUARY OCTOBER"
        string6 = "August AUGUST"
        string5 = "March April MARCH APRIL"
        string4 = "June July JUNE JULY"
        string3 = "May MAY Jan Feb Mar Apr Jun Jul Aug Sep Oct Nov Dec"

        stringTextList = re.split('[ \n]', re.sub("[*~@#^&;:!?\',(){}\[\]\"\=+]", " ", text))
        tokenList = []
        i = 0;
        elements = islice(stringTextList, 0, None)
        for elem in elements:
            if (i == len(stringTextList)):
                break
            if (elem == ""):
                i += 1
                continue
            if ('.' in stringTextList[i] and stringTextList[i].index('.') == 0):
                stringTextList[i] = stringTextList[i][1:]
            elif ('.' in stringTextList[i] and stringTextList[i].index('.') == len(stringTextList[i]) - 1):
                stringTextList[i] = stringTextList[i][:-1]

            if ('/' in stringTextList[i] and stringTextList[i].index('/') == 0):
                stringTextList[i] = stringTextList[i][1:]
            if ('/' in stringTextList[i] and stringTextList[i].index('/') == len(stringTextList[i]) - 1):
                stringTextList[i] = stringTextList[i][:-1]
            if (stringTextList[i] != "between" and stringTextList[i] != "and" and stringTextList[
                i].lower() not in self.stopWords and stringTextList[i].upper() not in self.stopWords):
                curr1 = stringTextList[i]
                if (len(stringTextList[i]) > 1 and stringTextList[i][len(stringTextList[i]) - 1] == '.'):
                    stringTextList[i] = stringTextList[i][:-1]
                    if (len(stringTextList[i]) > 1 and stringTextList[i][-2:] == 'bn' and stringTextList[i].index(
                            'bn') == len(stringTextList[i]) - 2 and '-' not in stringTextList[i]) and (
                            (i + 1 < len(stringTextList) and stringTextList[i + 1] == "Dollars") and (
                            '.' in stringTextList[i] and stringTextList[i][:-(
                            len(stringTextList[i]) - stringTextList[i].index('.'))].isdigit() and stringTextList[i][stringTextList[i].index('.') + 1:-2].isdigit() and
                            stringTextList[i].index('.') != len(stringTextList[i]) - 1) or (
                                    '.' not in stringTextList[i] and stringTextList[i][:-2].isdigit())):
                        tokenList.append(str(float(float(stringTextList[i][:-2]) * 1000)) + " M Dollars")
                    elif len(stringTextList[i]) > 1 and stringTextList[i][-1:] == 'm' and stringTextList[i].index(
                            'm') == len(stringTextList[i]) - 1 \
                            and ((i + 1 < len(stringTextList) and stringTextList[i + 1] == "Dollars") and (
                            '.' in stringTextList[i] and stringTextList[i][:-(
                            len(stringTextList[i]) - stringTextList[i].index('.'))].isdigit() and stringTextList[i][
                                                                                                  stringTextList[
                                                                                                      i].index(
                                                                                                      '.') + 1:-1].isdigit())
                                 or ('.' not in stringTextList[i] and stringTextList[i][:-1].isdigit())):
                        tokenList.append(str(float(stringTextList[i][:-1])) + " M Dollars")
                if stringTextList[i].isdigit() or (
                        ('.' in stringTextList[i]) and (stringTextList[i].count('.') == 1) and
                        (stringTextList[i].index('.') < (len(stringTextList[i]) - 1)) and
                        (stringTextList[i].split('.')[1].isdigit() and
                         stringTextList[i].split('.')[0].isdigit())):  # digits
                    if '.' in stringTextList[i]:
                        digits = len(stringTextList[i]) - len(stringTextList[i][stringTextList[i].index('.'):])
                    else:
                        digits = len(stringTextList[i])
                    rightDigits = ""
                    curr = ""
                    if ((digits >= 4 and digits < 7)):
                        curr = str(float(stringTextList[i]) / 1000) + "K"
                        tokenList.append(curr)  # 1,000
                    elif (digits >= 7 and digits < 10):
                        curr = str(float(stringTextList[i]) / 1000000) + "M"
                        tokenList.append(curr)  # 1,000,000
                    elif (digits >= 10):
                        curr = str(float(stringTextList[i]) / 1000000000) + "B"
                        tokenList.append(curr)  # 1,000,000,000
                    elif (digits < 4):
                        if (i + 1 < len(stringTextList) and stringTextList[i + 1] == "Thousand"):
                            curr = stringTextList[i] + "K"
                            tokenList.append(curr)
                            i = i + 1
                        elif (i + 1 < len(stringTextList) and (
                                stringTextList[i + 1] == "Million" or stringTextList[i + 1] == "million")):
                            curr = stringTextList[i] + "M"
                            tokenList.append(curr)
                            i = i + 1
                        elif (i + 1 < len(stringTextList) and (
                                stringTextList[i + 1] == "Billion" or stringTextList[i + 1] == "billion")):
                            curr = stringTextList[i] + "B"
                            tokenList.append(curr)
                            rightDigits = "000"
                            i = i + 1
                        elif (i + 1 < len(stringTextList) and (
                                stringTextList[i + 1] == "Trillion" or stringTextList[i + 1] == "trillion")):
                            curr = stringTextList[i] + "00B"
                            tokenList.append(curr)
                            i = i + 1
                            rightDigits = "000000"
                        else:
                            curr = stringTextList[i]
                            tokenList.append(curr)
                        if (i + 2 < len(stringTextList) and (
                                stringTextList[i + 1] == "U.S." and stringTextList[i + 2] == "dollars")):
                            tokenList.append(stringTextList[i - 1] + rightDigits + " M" + " Dollars")
                            i = i + 2
                        if (i + 1 < len(stringTextList) and '/' in stringTextList[i + 1]):
                            curr = stringTextList[i] + " " + stringTextList[i + 1]
                            tokenList.append(curr)
                            i = i + 1
                    if (i + 1 < len(stringTextList) and stringTextList[i + 1] == "Dollars"):
                        tokenList.append(curr + " Dollars")
                    if (i + 1 < len(stringTextList) and (
                            stringTextList[i + 1] == "percent" or stringTextList[i + 1] == "percentage")):
                        tokenList.append(curr + "%")
                elif ("-" in stringTextList[i]):
                    for part in stringTextList[i].split('-'):
                        if (part != ""):
                            stringTextList.append(part)
                    if (stringTextList[i].index('-') == 0 and stringTextList[i][1:].isdigit()):
                        tokenList.append(str(stringTextList[i][1:]+"-"))

                    if (stringTextList[i].index('-') != 0 and stringTextList[i].index('-') != len(
                            stringTextList[i]) - 1 and len(stringTextList[i]) != 1):
                        tokenList.append(stringTextList[i])

                elif ((stringTextList[i] in string3 and len(stringTextList[i]) == 3) or  ###### MONTHS!! ######
                      (stringTextList[i] in string4 and len(stringTextList[i]) == 4) or
                      (stringTextList[i] in string5 and len(stringTextList[i]) == 5) or
                      (stringTextList[i] in string6 and len(stringTextList[i]) == 6) or
                      (stringTextList[i] in string7 and len(stringTextList[i]) == 7) or
                      (stringTextList[i] in string8 and len(stringTextList[i]) == 8) or
                      (stringTextList[i] in string9 and len(stringTextList[i]) == 9)):
                    if (i - 1 >= 0 and stringTextList[i - 1].isdigit()):
                        if (len(stringTextList[i - 1]) < 2):
                            tokenList.append(self.monthToNum(stringTextList[i]) + '-0' + stringTextList[i - 1])
                            tokenList.append(stringTextList[i])
                            tokenList.append(stringTextList[i-1])
                        else:
                            tokenList.append(self.monthToNum(stringTextList[i]) + '-' + stringTextList[i - 1])
                            tokenList.append(stringTextList[i])
                            tokenList.append(stringTextList[i-1])
                    elif (i + 1 < len(stringTextList) and stringTextList[i + 1].isdigit()):
                        if (len(stringTextList[i + 1]) < 2):
                            tokenList.append(self.monthToNum(stringTextList[i]) + '-0' + stringTextList[i + 1])
                            tokenList.append(stringTextList[i])
                            tokenList.append(stringTextList[i+1])
                        else:
                            tokenList.append(self.monthToNum(stringTextList[i]) + '-' + stringTextList[i + 1])
                            tokenList.append(stringTextList[i])
                            tokenList.append(stringTextList[i+1])
                    else:
                        tokenList.append(stringTextList[i])

                elif (len(stringTextList[i]) > 0 and stringTextList[i][0] == '$'):
                    curr = stringTextList[i][1:]
                    if (('.' in curr) and (curr.count('.') == 1) and (
                            stringTextList[i].index('.') < (len(stringTextList[i]) - 1)) and
                            (curr.split('.')[1].isdigit() and curr.split('.')[0].isdigit())):
                        digits = len(curr) - len(stringTextList[i][stringTextList[i].index('.'):])
                    else:
                        digits = len(curr)
                    if (digits < 7 and len(stringTextList[i]) > 1 and curr.isdigit()):
                        if ((digits < 4)) and (i + 1 < len(stringTextList)):
                            if (stringTextList[i + 1] == "million"):
                                curr = curr + " M"
                                i = i + 1
                            elif (stringTextList[i + 1] == "billion"):
                                curr = curr + "000" + " M"
                                i = i + 1
                        tokenList.append(curr + " Dollars")
                    elif (digits > 5 and digits < 10 and curr.isdigit()):
                        tokenList.append(str(float(stringTextList[i][1:]) / 1000000) + " M Dollars")
                elif (stringTextList[i] == "between"):
                    iterNum = 0
                    if (i + 3 < len(stringTextList) and stringTextList[i + 2] == "and" and stringTextList[
                        i + 1].isdigit()):
                        iterNum = 4
                    if (i + 5 < len(stringTextList) and stringTextList[i + 3] == "and" and stringTextList[
                        i + 1].isdigit()):
                        iterNum = 6
                    if (i + 6 < len(stringTextList) and stringTextList[i + 4] == "and" and stringTextList[
                        i + 1].isdigit()):
                        iterNum = 8
                    tmp = ""
                    for x in range(0, iterNum - 1):
                        if x + i < len(stringTextList):
                            tmp = tmp + " " + stringTextList[i + x]
                        tmp = tmp[1:]
                    tokenList.append(tmp)
                elif (stringTextList[i] == "kgs" or stringTextList[i] == "Kgs") and (i != 0 and stringTextList[i-1].isdigit()):
                    tokenList.append(stringTextList[i])
                    tokenList.append(stringTextList[i-1] + " KG")
                elif stringTextList[i].isalpha():
                    tokenList.append(stringTextList[i])

            i = i + 1
        return tokenList

    def monthToNum(self, month):
        return {
            'JANUARY': "01", 'January': "01", 'Jan': "01",
            'FEBRUARY': "02", 'February': "02", 'Feb': "02",
            'MARCH': "03", 'March': "03", 'Mar': "03",
            'APRIL': "04", 'April': "04", 'Apr': "04",
            'MAY': "05", 'May': "05", "may": "05",
            'JUNE': "06", 'June': "06", 'Jun': "06",
            'JULY': "07", 'July': "07", 'Jul': "07",
            'AUGUST': "08", 'August': "08", 'Aug': "08",
            'SEPTEMBER': "09", 'September': "09", 'Sep': "09",
            'OCTOBER': "10", 'October': "10", 'Oct': "10",
            'NOVEMBER': "11", 'November': "11", 'Nov': "11",
            'DECEMBER': "12", 'December': "12", 'Dec': "12",

        }[month]
