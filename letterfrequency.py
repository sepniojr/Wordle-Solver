"""
Program I developed which takes in the list of valid wordle words and finds the frequency of each letter in each spot in the 5-letter word. 

"""
if __name__ == "__main__":
    valid_words=[]
    file = open('valid-wordle-words.txt', 'r')
    for valid_word in file:
        valid_word = valid_word.strip()
        valid_words.append(valid_word.upper())


    var1 = {}
    var2 = {}
    var3 = {}
    var4 = {}
    var5 = {}


    for i in range(len(valid_words)):
        for j in range(len(valid_words[i])):
            if j == 0:
                if valid_words[i][j] in var1:
                    var1[valid_words[i][j]] += 1
                else:
                    var1[valid_words[i][j]] = 1
            if j == 1:
                if valid_words[i][j] in var2:
                    var2[valid_words[i][j]] += 1
                else:
                    var2[valid_words[i][j]] = 1
            if j == 2:
                if valid_words[i][j] in var3:
                    var3[valid_words[i][j]] += 1
                else:
                    var3[valid_words[i][j]] = 1
            if j == 3:
                if valid_words[i][j] in var4:
                    var4[valid_words[i][j]] += 1
                else:
                    var4[valid_words[i][j]] = 1
            if j == 4:
                if valid_words[i][j] in var5:
                    var5[valid_words[i][j]] += 1
                else:
                    var5[valid_words[i][j]] = 1
    
    sorted_dict1 = dict(sorted(var1.items(), key=lambda item: item[1], reverse=True))
    print(sorted_dict1.keys())

    sorted_dict2 = dict(sorted(var2.items(), key=lambda item: item[1], reverse=True))
    print(sorted_dict2.keys())
    
    sorted_dict3 = dict(sorted(var3.items(), key=lambda item: item[1], reverse=True))
    print(sorted_dict3.keys())

    sorted_dict4 = dict(sorted(var4.items(), key=lambda item: item[1], reverse=True))
    print(sorted_dict4.keys())

    sorted_dict5 = dict(sorted(var5.items(), key=lambda item: item[1], reverse=True))
    print(sorted_dict5.keys())