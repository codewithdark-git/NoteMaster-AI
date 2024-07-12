


para = ("""W3Schools is optimized for learning and training.
        Examples might be simplified to improve reading and learning. 
        Tutorials, references, and examples are constantly reviewed to avoid errors, 
        but we cannot warrant full correctness of all content. While using W3Schools, 
        you agree to have read and accepted our terms of use, cookie and privacy policy.""")

title = para.split("\n", 1)[0]
print(str(title).replace("[ ' ' ]", " "))

