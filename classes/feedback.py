class Feedback():
    def __init__(self, name, comments, grade):
        self.name = name
        self.comments = comments
        self.grade = grade

    def __eq__(self, other):
        return self.name == other.name and self.grade == self.grade

    def display(self):
        print('-'*20)
        print('Name: {}\nGrade: {}'.format(self.name, self.grade))

        comments = 'Comments: '
        for comment in self.comments:
            comments += str(comment) + ' '
        print(comments + '\n' + '-'*20)